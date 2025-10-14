import numpy as np
import pytest
import torch
import torch.nn as nn
from torch.optim.adam import Adam
from torch.optim.lr_scheduler import StepLR
from torch.optim.optimizer import Optimizer

from mlbnb.checkpoint import (
    Checkpoint,
    CheckpointManager,
)
from mlbnb.paths import ExperimentPath


@pytest.fixture
def checkpoint_manager() -> CheckpointManager:
    return CheckpointManager(ExperimentPath("/tmp/", "test_checkpoints"))


@pytest.fixture
def simple_model() -> nn.Module:
    return nn.Linear(10, 1)


@pytest.fixture
def optimizer(simple_model) -> Adam:
    return Adam(simple_model.parameters())


@pytest.fixture
def scheduler(optimizer) -> StepLR:
    return StepLR(optimizer, step_size=1)


@pytest.fixture
def generator() -> torch.Generator:
    generator = torch.Generator()
    generator.manual_seed(42)
    return generator


def test_save_checkpoint(
    checkpoint_manager: CheckpointManager,
    simple_model: nn.Module,
    optimizer: Optimizer,
    scheduler: StepLR,
    generator: torch.Generator,
):
    checkpoint_manager.save_checkpoint(
        "test_checkpoint",
        simple_model,
        optimizer,
        generator,
        scheduler,
    )
    assert checkpoint_manager.checkpoint_exists("test_checkpoint")


def test_checkpoint_exists(
    checkpoint_manager: CheckpointManager, generator: torch.Generator
):
    assert not checkpoint_manager.checkpoint_exists("non_existent_checkpoint")
    checkpoint_manager.save_checkpoint(
        "existing_checkpoint",
        nn.Linear(5, 1),
        Adam(nn.Linear(5, 1).parameters()),
        generator,
    )
    assert checkpoint_manager.checkpoint_exists("existing_checkpoint")


def test_load_checkpoint(
    checkpoint_manager: CheckpointManager,
    simple_model: nn.Module,
    optimizer: Optimizer,
    generator: torch.Generator,
    scheduler: StepLR,
):
    checkpoint_manager.save_checkpoint(
        "load_test", simple_model, optimizer, generator, scheduler
    )
    loaded_checkpoint = checkpoint_manager.load_checkpoint("load_test")
    assert isinstance(loaded_checkpoint, Checkpoint)


def test_load_non_existent_checkpoint(checkpoint_manager: CheckpointManager):
    with pytest.raises(FileNotFoundError):
        checkpoint_manager.load_checkpoint("non_existent")


def test_reproduce(
    checkpoint_manager: CheckpointManager,
    simple_model: nn.Module,
    optimizer: Optimizer,
    generator: torch.Generator,
    scheduler: StepLR,
):
    # Modify states
    simple_model.weight.data.fill_(1.0)  # ty: ignore
    optimizer.step()
    scheduler.step()
    np.random.rand()
    torch.rand(1)

    # Save checkpoint
    checkpoint_manager.save_checkpoint(
        "reproduce_test", simple_model, optimizer, generator, scheduler
    )

    # Modify states again
    simple_model.weight.data.fill_(2.0)  # ty: ignore
    optimizer.step()
    scheduler.step()
    np.random.rand()
    torch.rand(1)

    # Reproduce
    checkpoint = checkpoint_manager.reproduce(
        "reproduce_test", simple_model, optimizer, generator, scheduler
    )

    # Check if states are restored
    assert torch.all(
        simple_model.state_dict()["weight"].eq(checkpoint.model_state["weight"])
    )
    assert (
        optimizer.state_dict()["param_groups"]
        == checkpoint.optimiser_state["param_groups"]
    )
    assert scheduler.state_dict() == checkpoint.scheduler_state
    assert np.array_equal(np.random.get_state()[1], checkpoint.numpy_random_state[1])  # type: ignore
    assert torch.all(generator.get_state().eq(checkpoint.torch_gen_state))


def test_save_and_load_without_scheduler(
    checkpoint_manager: CheckpointManager,
    simple_model: nn.Module,
    optimizer: Optimizer,
    generator: torch.Generator,
):
    checkpoint_manager.save_checkpoint(
        "no_scheduler", simple_model, optimizer, generator
    )
    loaded_checkpoint = checkpoint_manager.load_checkpoint("no_scheduler")
    assert loaded_checkpoint.scheduler_state is None


@pytest.mark.parametrize("other_state", [{"custom_data": [1, 2, 3]}, "some string", 42])
def test_save_and_load_with_other_state(
    checkpoint_manager, simple_model, optimizer, other_state
):
    checkpoint_state = Checkpoint(
        model_state=simple_model.state_dict(),
        optimiser_state=optimizer.state_dict(),
        scheduler_state=None,
        numpy_random_state=np.random.get_state(),
        torch_gen_state=torch.get_rng_state(),
        other_state=other_state,
    )
    torch.save(checkpoint_state, checkpoint_manager.dir / "other_state_test.pt")
    loaded_checkpoint = checkpoint_manager.load_checkpoint("other_state_test")
    assert loaded_checkpoint.other_state == other_state
