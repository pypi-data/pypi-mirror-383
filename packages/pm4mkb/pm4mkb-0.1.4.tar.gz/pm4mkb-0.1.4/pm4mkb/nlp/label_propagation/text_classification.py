import sys
import random
from importlib import import_module
from typing import Sequence, NoReturn, Dict, List, Union

import numpy as np
import pandas as pd
from tqdm import tqdm
from bpemb import BPEmb
import torch
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split as tts
from loguru import logger
from transformers import AutoTokenizer

from pm4mkb.nlp.label_propagation._net import train, evaluate, predict, ConvNeuralNet
from pm4mkb.nlp.label_propagation._custom_dataset import CustomLabeledDataset, CustomNonLabeledDataset
from pm4mkb.nlp.label_propagation._custom_exceptions import NotEnoughSamplesForLabelError


torch.manual_seed(0)
random.seed(0)
np.random.seed(0)


def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


g = torch.Generator()
g.manual_seed(0)


# TODO: Autodetect dim and vocabsize of tokenizer
class ConvClassifier:
    """
    Object that adapts labels from train dataset made by user to unmarked texts' data.
    Model and tokenizer must be downloaded.
    """

    def __init__(
        self,
        path_to_model: str,
        path_to_tokenizer: str,
        n_classes: int,
        epochs: int,
        dim: int,
        vocab_size: int,
        n_filters: int = 100,
    ):
        self.tokenizer: Union[BPEmb, AutoTokenizer] = self._collect_tokenizer(
            path_to_model, path_to_tokenizer, dim, vocab_size
        )
        self.model: ConvNeuralNet = ConvNeuralNet(vocab_size, dim, n_classes, n_filters, self.tokenizer.vectors)
        self.epochs: int = epochs
        self._epoch_freeze_weights: int = epochs // 2
        self.train: bool = False

    def _collect_tokenizer(self):
        raise NotImplementedError

    def apply(self, dataloader: Dict[str, DataLoader]) -> NoReturn:
        accu_vals: List[float] = []
        for epoch in range(1, self.epochs + 1):
            logger.info(f"Proceeding epoch {str(epoch)} / {str(self.epochs)}")
            if epoch == self._epoch_freeze_weights:
                logger.info(f"Freezing weights of embeddings")
                self.model.embedding.weight.requires_grad = False
            train(dataloader.get("train"), self.model)
            accu_val = evaluate(dataloader.get("valid"), self.model)
            accu_vals.append(accu_val)
        self.train = True
        if accu_vals[-1] <= accu_vals[0]:
            logger.warning("No effect while domain adoption")
        else:
            logger.info("Adaptation of the model to the domain was successful")

    def get_result(self, dataloader: Dict[str, DataLoader], lbl_decoder: Dict[int, str]) -> pd.DataFrame:
        if not self.train:
            self.apply(dataloader)
        return predict(dataloader.get("predict"), self.model, lbl_decoder)


class SentencePieceConvClassifier(ConvClassifier):
    """
    Object that adapts labels from train dataset made by user to unmarked texts' data.
    Use this type if your text contains typical phrases or clerical phrases, or template expressions that are often repeated from text to text.

    BPEmb outperforms all other sub-word units across all architectures (https://aclanthology.org/L18-1473.pdf).
    Builds on pre-trained subword embeddings, based on Byte-Pair Encoding (BPE).
    """

    def _collect_tokenizer(self, path_to_model, path_to_tokenizer, dim, vs):
        return BPEmb(model_file=path_to_model, emb_file=path_to_tokenizer, dim=dim, vs=vs)


class ContextEmbConvClassifier(ConvClassifier):
    """
    Object that adapts labels from train dataset made by user to unmarked texts' data.
    Use this type if your text is very diverse and resembles a narrative.

    Architecture of AutoTokenizer from transformers is used here for context embeddings.
    """

    def _collect_tokenizer(self, path_to_model, path_to_tokenizer, dim, vs):
        raise NotImplementedError("Coming soon :)")


class DataPipeline:
    """
    Object that prepares dataset for label propagation. Proceeding `apply` method gives from one dataframe three
    dataloaders - two for training model, one for prediction.
    """

    LABEL_COL_NAME: str = "label"

    def __init__(
        self,
        data_with_labels: pd.DataFrame,
        data_wo_labels: pd.DataFrame,
        text_col_name: str,
        label_col_name: str,
        _labels: List[str],
        max_len: int,
        batch_size: int,
    ):
        self.lbl_encoder: Dict[str, int] = {v: int(k) for k, v in enumerate(_labels)}
        self.lbl_decoder: Dict[int, str] = {int(k): v for k, v in enumerate(_labels)}

        data_with_labels[self.LABEL_COL_NAME] = data_with_labels[label_col_name].map(self.lbl_encoder)
        self.data_with_labels, self.data_wo_labels = data_with_labels, data_wo_labels
        self.dataloader: Dict[str, DataLoader] = None
        self.max_len, self.batch_size, self.text_col_name = max_len, batch_size, text_col_name

    def apply(self, tokenizer: object) -> NoReturn:
        try:
            X_train, X_test, y_train, y_test = tts(
                self.data_with_labels[self.text_col_name],
                self.data_with_labels[self.LABEL_COL_NAME],
                test_size=0.33,
                random_state=42,
                stratify=self.data_with_labels[self.LABEL_COL_NAME],
            )
        except ValueError as err:
            raise NotEnoughSamplesForLabelError(
                "Not enough samples provided for each label, please, check with `data.label_col_name.value_counts()`"
            ) from err

        X_predict = self.data_wo_labels.drop_duplicates(subset=[self.text_col_name])[self.text_col_name]

        train_dataset = CustomLabeledDataset(
            data=X_train.values, targets=y_train.values, tokenizer=tokenizer.encode_ids, max_len=self.max_len
        )
        valid_dataset = CustomLabeledDataset(
            data=X_test.values, targets=y_test.values, tokenizer=tokenizer.encode_ids, max_len=self.max_len
        )
        predict_dataset = CustomNonLabeledDataset(
            data=X_predict.values, tokenizer=tokenizer.encode_ids, max_len=self.max_len
        )

        del X_train, X_test, y_train, y_test, X_predict

        self.dataloader: Dict[str, DataLoader] = {
            "train": DataLoader(
                train_dataset,
                batch_size=self.batch_size,
                shuffle=True,
                worker_init_fn=seed_worker,
                generator=g,
            ),
            "valid": DataLoader(
                valid_dataset,
                batch_size=self.batch_size,
                shuffle=True,
                worker_init_fn=seed_worker,
                generator=g,
            ),
            "predict": DataLoader(
                predict_dataset,
                batch_size=1,
                shuffle=False,
                worker_init_fn=seed_worker,
                generator=g,
            ),
        }

    def get_result(self) -> Dict[str, DataLoader]:
        if not self.dataloader:
            raise RuntimeError("Call `apply` method first")
        return self.dataloader


# TODO: Autodetect model type
# TODO: replace with correct module name after concatenation
# TODO Нужно добавить проверку, что у нас нет разметки значений которых очень мало для обучения
class LabelPropagation:
    """
    User interface for label propagation.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe with texts and its partial labels.

        Proceeding dataframe splits into two parts - for training the model (where labels exist)
        and prediction (where labels are absent).
        Important to keep control on number of labeled texts for each class.
        Too few samples on class crushes the propagation (not enough information for model).

    text_col_name: str
        Name of column with texts.

    label_col_name: str
        Name of column with labels.

    undefined_label: str
        Label which means these texts' labels (in other words - rows) needs to be predicted.

    path_to_model: str
        Path to `.model` or folder with model in case transformers.

    path_to_tokenizer: str
        Path to `tokenizer` (`dim`) or folder with with tokenizer in case transformers.

    n_classes: int
        Number of labeled by user classes in train dataset.

    tokenizer_type: str
        Allowed `sentence_piece` or `context_embeddings` only.
        (!) Temporaly work with `sentence_piece` only, `context_embeddings` will be added soon.

        `sentence_piece` - use this type if your text contains typical phrases or clerical phrases,
                           or template expressions that are often repeated from text to text.
        BPEmb outperforms all other sub-word units across all architectures (https://aclanthology.org/L18-1473.pdf).
        Builds on pre-trained subword embeddings, based on Byte-Pair Encoding (BPE).

        `context_embeddings` - use this type if your text is very diverse and resembles a narrative
        Architecture of AutoTokenizer from transformers is used here for context embeddings.

    batch_size: int, default = 16
        Number of texts to be used at every train iteration during domain adoption.

    perc_samples_for_max_len: float, default = 0.1
        Weight of texts in dataset to calculate average sentence length.

    epochs: int, default = 10
        Number of iteration to be done for domain adoption.

    dim: int
        Dimensions in embedding (depends on model).

    vocab_size: int
        Number of tokens in model vocabulary.

    Examples
    --------
    >>> from pm4mkb.nlp.label_propagation import LabelPropagation
    >>>
    >>> lp = LabelPropagation(
    ... my_data,
    ... tokenizer_type="sentence_piece",
    ... path_to_model = "ru.wiki.bpe.vs100000.model",
    ... path_to_tokenizer = "ru.wiki.bpe.vs100000.d300.w2v.bin",
    ... text_col_name="Сообщение",
    ... label_col_name="Название кластера",
    ... undefined_label="<MASK>")
    >>> lp.apply()
    >>> lp.get_result()
    """

    _tokenizer_interfaces = {
        "sentence_piece": "SentencePieceConvClassifier",
        "context_embeddings": "ContextEmbConvClassifier",
    }

    def __init__(
        self,
        data: pd.DataFrame,
        text_col_name: str,
        label_col_name: str,
        undefined_label: str,
        path_to_model: str,
        path_to_tokenizer: str,
        tokenizer_type: str,
        batch_size: int = 16,
        perc_samples_for_max_len: float = 0.1,
        epochs: int = 10,
        dim: int = 300,
        vocab_size: int = 100000,
    ):
        assert tokenizer_type in ("sentence_piece", "context_embeddings")

        # Collect all labels from dataset
        data[label_col_name] = data[label_col_name].astype(str)
        data.drop_duplicates(subset=[text_col_name], inplace=True)
        _labels: List[str] = data[label_col_name].value_counts().index.to_list()
        _labels.remove(undefined_label)

        # Split dataset by 2 pieces - with labels and without them to predict
        data_with_labels: pd.DataFrame = data[~(data[label_col_name] == undefined_label)][
            [text_col_name, label_col_name]
        ]
        data_wo_labels: pd.DataFrame = data[data[label_col_name] == undefined_label][[text_col_name]]

        # Collect pipeline and classifier
        _module_name = self._tokenizer_interfaces.get(tokenizer_type)
        self.classifier: Union[SentencePieceConvClassifier, ContextEmbConvClassifier] = getattr(
            import_module(sys.modules[__name__].__name__), _module_name
        )(path_to_model, path_to_tokenizer, len(_labels), epochs, dim, vocab_size)
        max_len: int = self._get_max_len(
            texts=data.sample(int(perc_samples_for_max_len * len(data_with_labels)))[text_col_name].values,
            tokenizer=self.classifier.tokenizer,
        )
        self.data_pipe = DataPipeline(
            data_with_labels, data_wo_labels, text_col_name, label_col_name, _labels, max_len, batch_size
        )

        self.answers: pd.DataFrame = None

    @staticmethod
    def _get_max_len(texts: Sequence[str], tokenizer: object, quantile: float = 0.95) -> int:
        """
        Calculates number of tokens to be used in sentence embeddings.

        Recommendation: number of tokens is calculated for N random texts before train and predict dataset split.
        Too many tokens affects much embedding dimension and, moreover, paddings. For this reason quantile can be set.
        """

        text_lengths: List[float] = list()
        for text in tqdm(texts):
            text_lengths.append(len(tokenizer.encode(str(text).lower())))
        avg_token_count: int = int(np.quantile(text_lengths, quantile))
        logger.info(f"Calculating max len for sentences in dataset: {str(avg_token_count)}")
        return avg_token_count

    def apply(self) -> NoReturn:
        """Proceed data pipeline and classifier to be able to make predictions"""

        # Prepare datasets
        self.data_pipe.apply(self.classifier.tokenizer)
        # Domain adoption
        self.classifier.apply(self.data_pipe.dataloader)
        # Predict
        self.answers: pd.DataFrame = self.classifier.get_result(
            self.data_pipe.dataloader, self.data_pipe.lbl_decoder
            )

    def get_result(self) -> pd.DataFrame:
        """Proceed inference by classifier for part of dataset without labels"""
        if not isinstance(self.answers, pd.DataFrame):
            raise RuntimeError("Call `apply` first")
        return self.answers
