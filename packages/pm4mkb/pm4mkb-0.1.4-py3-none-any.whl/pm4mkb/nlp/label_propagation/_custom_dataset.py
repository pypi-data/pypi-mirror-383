import numpy as np
import torch


class CustomLabeledDataset:
    def __init__(self, data, targets, tokenizer, max_len):
        self.data = data
        self.targets = targets
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text = str(self.data[idx])
        label = self.targets[idx]

        # input_ids = self.tokenizer(
        #     text.lower(),
        #     padding="max_length", max_length=self.max_len, truncation=True
        # )

        input_ids = np.zeros((int(self.max_len),))
        row = self.tokenizer(text.lower())
        for j, idx in enumerate(row):
            if j <= self.max_len - 1:
                input_ids[j] = idx

        return {"text": torch.tensor(input_ids, dtype=torch.long), "label": torch.tensor(label, dtype=torch.long)}


class CustomNonLabeledDataset:
    def __init__(self, data, tokenizer, max_len):
        self.data = list(set(data))
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text = str(self.data[idx])

        # input_ids = self.tokenizer(
        #     text.lower(),
        #     padding="max_length", max_length=self.max_len, truncation=True
        # )

        input_ids = np.zeros((int(self.max_len),))
        row = self.tokenizer(text.lower())
        for j, idx in enumerate(row):
            if j <= self.max_len - 1:
                input_ids[j] = idx

        return torch.tensor(input_ids, dtype=torch.long), text
