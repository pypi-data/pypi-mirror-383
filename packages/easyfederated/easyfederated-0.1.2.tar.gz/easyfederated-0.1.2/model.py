from typing import Any

from torch import nn, optim, Tensor, tensor, float32, no_grad, sum

from src.lib.backends.torch import FederatedTorch
from src.lib.easyfed import Client, Server, Federated


@Federated(
    server=Server("server.pablofraile.net", save_model_path="/models/test.pl"),
    clients=[Client(name="site1"), Client(name="site2", env_vars={"VAR": "VALUE"})],
    easyfed_config="./test/fake_project/easyfed.yaml"
)
class MyModel(FederatedTorch):

    def __init__(self):
        super().__init__()
        init_weights = tensor([[1, 2, 3],
                               [4, 5, 6],
                               [7, 8, 9]], dtype=float32)
        self.weights = nn.Parameter(init_weights)

    def forward(self, x: Any):
        """
        Forward pass (optional for this example).
        If x is provided, multiply by weight matrix; otherwise return weights.
        """
        if x is None:
            return self.weights
        return x.matmul(self.weights)

    def get_weights(self) -> Tensor:
        return self.weights.detach().cpu()

    def set_weights(self, new_weights) -> None:
        with no_grad():
            self.weights.copy_(new_weights)

    def train_step(self, learning_rate=1.0) -> Tensor:
        optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        optimizer.zero_grad()
        loss = -sum(self.weights)
        loss.backward()
        optimizer.step()
        return self.get_weights()
