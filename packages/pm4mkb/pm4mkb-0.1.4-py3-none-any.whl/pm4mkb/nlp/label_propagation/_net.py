import torch
from tqdm import tqdm
import numpy as np
import pandas as pd


class ConvNeuralNet(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, n_classes, n_filters, embedding_matrix):
        super().__init__()
        self.kernel_num = n_filters
        self.embedding = torch.nn.Embedding(input_dim, hidden_dim)

        self.embedding.weight = torch.nn.Parameter(torch.tensor(embedding_matrix, dtype=torch.float32))
        self.embedding.weight.requires_grad = True

        self.conv1 = torch.nn.Conv2d(1, self.kernel_num, (2, hidden_dim))
        self.conv2 = torch.nn.Conv2d(1, self.kernel_num, (4, hidden_dim))
        self.conv3 = torch.nn.Conv2d(1, self.kernel_num, (8, hidden_dim))

        self.dropout = torch.nn.Dropout(0.5)
        self.fc1 = torch.nn.Linear(3 * self.kernel_num, n_classes)

    def forward(self, x):
        x = self.embedding(x)
        x = x.unsqueeze(1)

        conv_out_1 = torch.nn.functional.relu(self.conv1(x)).squeeze(3)
        conv_out_2 = torch.nn.functional.relu(self.conv2(x)).squeeze(3)
        conv_out_3 = torch.nn.functional.relu(self.conv3(x)).squeeze(3)

        conv_out_1 = torch.nn.functional.max_pool1d(conv_out_1, conv_out_1.size(2)).squeeze(2)
        conv_out_2 = torch.nn.functional.max_pool1d(conv_out_2, conv_out_2.size(2)).squeeze(2)
        conv_out_3 = torch.nn.functional.max_pool1d(conv_out_3, conv_out_3.size(2)).squeeze(2)

        x = torch.cat([conv_out_1, conv_out_2, conv_out_3], 1)

        x = self.dropout(x)
        logit = self.fc1(x)

        return logit


def train(dataloader, model):
    model.train()
    total_acc, total_count = 0, 0
    device = torch.device("cpu")
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-4, weight_decay=1e-4)

    for _, batch in enumerate(tqdm(dataloader)):
        text = batch["text"].to(device)
        label = batch["label"].to(device)
        optimizer.zero_grad()
        predicted_label = model(text)
        loss = criterion(predicted_label, label)
        loss.backward()
        optimizer.step()
        predicted_label = predicted_label.detach().cpu().numpy()
        label = label.to(device).numpy()
        total_acc += accuracy(predicted_label, label)
        total_count += len(label)

    return total_acc / total_count


def evaluate(dataloader, model):
    model.eval()
    total_acc, total_count, total_loss = 0, 0, 0
    device = torch.device("cpu")
    criterion = torch.nn.CrossEntropyLoss()

    with torch.no_grad():
        for _, batch in enumerate(tqdm(dataloader)):
            text = batch["text"].to(device)
            label = batch["label"].to(device)
            predicted_label = model(text)
            total_loss += criterion(predicted_label, label)
            predicted_label = predicted_label.detach().cpu().numpy()
            label = label.to(device).numpy()
            total_acc += accuracy(predicted_label, label)
            total_count += len(label)

    return total_acc / total_count


def accuracy(probs, targets):
    outputs = np.argmax(probs, axis=1)
    return np.sum(outputs == targets)


def predict(dataloader, model, decoder):
    texts, labels = [], []
    with torch.no_grad():
        for emb, text in tqdm(dataloader):
            texts.append(text[0])
            probs = torch.softmax(model(emb), 1).detach().cpu().numpy()
            labels.append(decoder[np.argmax(probs[0])])
    return pd.DataFrame({"text": texts, "label": labels})
