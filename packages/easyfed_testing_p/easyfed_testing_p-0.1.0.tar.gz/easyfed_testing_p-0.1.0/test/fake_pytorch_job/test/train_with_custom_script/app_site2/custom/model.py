import torch
import torch.nn as nn
import torch.optim as optim


class SimpleTorchModel(nn.Module):
    def __init__(self):
        super(SimpleTorchModel, self).__init__()
        init_weights = torch.tensor([[1, 2, 3],
                                     [4, 5, 6],
                                     [7, 8, 9]], dtype=torch.float32)
        self.weights = nn.Parameter(init_weights)

    def forward(self, x):
        """
        Forward pass (optional for this example). 
        If x is provided, multiply by weight matrix; otherwise return weights.
        """
        if x is None:
            return self.weights
        return x.matmul(self.weights)

    def get_weights(self):
        """Return a copy of the weights as a NumPy array."""
        return self.weights.detach().cpu()

    def set_weights(self, new_weights):
        with torch.no_grad():
            self.weights.copy_(new_weights)

    def train_step(self, learning_rate=1.0):
        """
        One training step: use SGD on a dummy loss so that each weight gets +1 update.
        We mimic the original numpy update (weights += learning_rate).
        """
        optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        optimizer.zero_grad()
        loss = -torch.sum(self.weights)
        loss.backward()
        optimizer.step()
        return self.get_weights()

    def evaluate(self):
        """Compute a metric (mean of weights) like the original."""
        weight_mean = torch.mean(self.weights).item()
        return {"weight_mean": weight_mean}
