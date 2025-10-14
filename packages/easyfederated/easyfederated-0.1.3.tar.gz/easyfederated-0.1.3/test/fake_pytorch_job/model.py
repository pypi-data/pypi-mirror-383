from typing import Any

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

    def forward(self, x: Any):
        """
        Forward pass (optional for this example). 
        If x is provided, multiply by weight matrix; otherwise return weights.
        """
        if x is None:
            return self.weights
        return x.matmul(self.weights)

    def get_weights(self) -> torch.Tensor:
        return self.weights.detach().cpu()

    def set_weights(self, new_weights) -> None:
        with torch.no_grad():
            self.weights.copy_(new_weights)

    def train_step(self, learning_rate=1.0) -> torch.Tensor:
        optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        optimizer.zero_grad()
        loss = -torch.sum(self.weights)
        loss.backward()
        optimizer.step()
        return self.get_weights()
