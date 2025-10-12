from typing import NoReturn, Dict

from transformers import pipeline
from tqdm import tqdm
import pandas as pd


class QuestionAnswering:
    """
    Model object that processes question with Q&A extractor model.

    Parameters
    ----------
    path_to_model: pipeline
        Question answering model architecture proceeding with transformers.

    Examples
    --------
    >>> from pm4mkb.nlp.qa_extractor import QuestionAnswering, DataPipeline
    >>> import pandas as pd
    >>> data_pipe = DataPipeline(data, text_col_name="context", question="С какой проблемой обратился пользователь?")
    >>> model = QuestionAnswering(path_to_model="mdeberta-v3")
    >>> 
    >>> data_pipe.apply(model)
    >>> data_pipe.get_result()
    """
    
    def __init__(self, path_to_model: str):
        self.model = pipeline("question-answering", path_to_model)
    
    def apply(self):
        pass

    def get_result(self, question: str, context):
        return self.model(question=question, context=context)['answer']


class DataPipeline:
    """
    Object that prepares dataframe for question&answering.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe with text column to extract information from.

    text_col_name: str
        Name of column with texts to proceed extraction.

    question: str
        Context question to every text in dataframe. Must be clear, concrete and related to every text in corpus.

    Examples
    --------
    >>> from pm4mkb.nlp.qa_extractor import QuestionAnswering, DataPipeline
    >>> import pandas as pd
    >>> data_pipe = DataPipeline(data, text_col_name="context", question="С какой проблемой обратился пользователь?")
    >>> model = QuestionAnswering(path_to_model="mdeberta-v3")
    >>> 
    >>> data_pipe.apply(model)
    >>> data_pipe.get_result()
    """

    ANSWERS_COL_NAME: str = 'answers'

    def __init__(self, data: pd.DataFrame, text_col_name: str, question: str):
        self.data: pd.DataFrame = data
        self.question: str = question
        self.text_col_name: str = text_col_name

        self.answers: Dict[str, str] = dict()

    def apply(self, model) -> NoReturn:
        """
        Runs Q&A on every text in corpus.

        Parameters
        ----------
        model: QuestionAnswering
            Model instance prepared with QuestionAnswering.
        """
        for context in tqdm(self.data[self.text_col_name].unique()):
            self.answers[context] = model.get_result(self.question, str(context))

    def get_result(self) -> pd.DataFrame:
        """
        Runs Q&A on every text in corpus.

        Parameters
        ----------
        model: QuestionAnswering
            Model instance prepared with QuestionAnswering.

        Returns
        ----------
        data: pd.DataFrame
            Returns dataframe with new column `answers`
        """
        if not self.answers:
            raise RuntimeError("Call `apply` first")
        self.data[self.ANSWERS_COL_NAME] = self.data[self.text_col_name].map(self.answers)
        return self.data
