from pathlib import Path
from typing import Any

import numpy as np
import pytest
import torch
import torch.nn as nn
from torch.optim.adam import Adam
from torch.optim.lr_scheduler import LRScheduler, StepLR
from torch.optim.optimizer import Optimizer
from torch.utils.data import DataLoader, TensorDataset

from mlbnb.checkpoint import CheckpointManager
from mlbnb.paths import ExperimentPath


class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 1)

    def forward(self, x):
        return self.linear(x)


def create_synthetic_data() -> DataLoader:
    X = torch.randn(100, 10)
    y = torch.randn(100, 1)
    return DataLoader(TensorDataset(X, y), batch_size=50)


def train_model(
    model: nn.Module,
    optimizer: Optimizer,
    scheduler: LRScheduler,
    dataloader: DataLoader,
    num_epochs: int,
) -> None:
    criterion = nn.MSELoss()
    for epoch in range(num_epochs):
        for X, y in dataloader:
            optimizer.zero_grad()
            output = model(X)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
        scheduler.step()


@pytest.fixture
def checkpoint_manager(tmp_path: Path):
    return CheckpointManager(ExperimentPath(tmp_path.parent, tmp_path.name))


def test_checkpoint_integration(checkpoint_manager: CheckpointManager):
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    generator = torch.Generator()
    generator.manual_seed(42)

    # Create model, optimizer, scheduler, and data
    model = SimpleModel()
    optimizer = Adam(model.parameters(), lr=0.01)
    scheduler = StepLR(optimizer, step_size=1, gamma=0.1)
    dataloader = create_synthetic_data()

    # Scenario 1: Train for 2 batches
    train_model(model, optimizer, scheduler, dataloader, num_epochs=2)

    model_state_1 = model.state_dict()
    optimizer_state_1 = optimizer.state_dict()
    scheduler_state_1 = scheduler.state_dict()
    np_state_1 = np.random.get_state()
    torch_state_1 = torch.get_rng_state()

    # Reset random seeds and recreate everything
    torch.manual_seed(42)
    np.random.seed(42)

    model = SimpleModel()
    optimizer = Adam(model.parameters(), lr=0.01)
    scheduler = StepLR(optimizer, step_size=1, gamma=0.1)
    dataloader = create_synthetic_data()

    # Scenario 2: Train for 1 batch, save checkpoint, load checkpoint, train for 1 more batch
    train_model(model, optimizer, scheduler, dataloader, num_epochs=1)

    # Save checkpoint
    checkpoint_manager.save_checkpoint(
        name="integration_test",
        model=model,
        optimiser=optimizer,
        generator=generator,
        scheduler=scheduler,
    )

    # Modify states to ensure loading actually does something
    model.linear.weight.data.fill_(99)
    optimizer.param_groups[0]["lr"] = 1.0
    scheduler.step()

    # Load checkpoint
    checkpoint_manager.reproduce(
        name="integration_test",
        model=model,
        optimiser=optimizer,
        generator=generator,
        scheduler=scheduler,
    )

    # Continue training
    train_model(model, optimizer, scheduler, dataloader, num_epochs=1)

    model_state_2 = model.state_dict()
    optimizer_state_2 = optimizer.state_dict()
    scheduler_state_2 = scheduler.state_dict()
    np_state_2 = np.random.get_state()
    torch_state_2 = torch.get_rng_state()

    # Compare states
    assert _state_checksum(model_state_1) == _state_checksum(model_state_2)
    assert _state_checksum(optimizer_state_1) == _state_checksum(optimizer_state_2)
    assert _state_checksum(scheduler_state_1) == _state_checksum(scheduler_state_2)

    assert np.array_equal(np_state_1[1], np_state_2[1])  # type: ignore
    assert torch.all(torch_state_1.eq(torch_state_2))


def _state_checksum(state_dict: dict[str, Any]) -> int:
    return hash(str(state_dict))
