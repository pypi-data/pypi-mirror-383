from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np
import torch
from loguru import logger
from torch import nn
from torch.optim.lr_scheduler import LRScheduler
from torch.optim.optimizer import Optimizer, StateDict

from mlbnb.file import ensure_parent_exists
from mlbnb.paths import ExperimentPath


@dataclass
class Checkpoint:
    """
    Data class representing the checkpoint state.

    :param model_state: The state dictionary of the PyTorch model.
    :param optimiser_state: The state dictionary of the PyTorch optimizer.
    :param numpy_random_state: The state of the NumPy random number generator.
    :param torch_gen_state: The state of the PyTorch random number generator.
    :param scheduler_state: The state dictionary of the PyTorch learning rate scheduler.
    :param other_state: Any other state. Should be generated via Saveable interface.
    """

    model_state: dict[str, Any]
    optimiser_state: StateDict
    numpy_random_state: dict[str, Any]
    torch_gen_state: torch.Tensor
    scheduler_state: Optional[dict[str, Any]] = None
    other_state: Optional[dict[str, Any]] = None


class Saveable(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def load_from_dict(self, data: dict[str, Any]) -> None:
        pass


class CheckpointManager:
    """
    Manager for saving and loading (torch) checkpoints.

    """

    def __init__(self, root: ExperimentPath):
        self.dir = root / "checkpoints"

    def save_checkpoint(
        self,
        name: str,
        model: nn.Module,
        optimiser: Optimizer,
        generator: torch.Generator,
        scheduler: Optional[LRScheduler] = None,
        other_state: Optional[Saveable] = None,
    ):
        """
        Generate and save a checkpoint from the current experiment state.

        :param name: The name of the checkpoint.
        :param model: The PyTorch model.
        :param optimiser: The PyTorch optimizer.
        :param generator: The PyTorch random number generator.
        :param scheduler: The PyTorch learning rate scheduler.
        :param other_state: Any other state. Should be generated via Saveable interface.
        """
        checkpoint_state = Checkpoint(
            model_state=model.state_dict(),
            optimiser_state=optimiser.state_dict(),
            numpy_random_state=np.random.get_state(),
            torch_gen_state=generator.get_state(),
            scheduler_state=scheduler.state_dict() if scheduler is not None else None,
            other_state=other_state.to_dict() if other_state is not None else None,
        )

        path = self.dir / f"{name}.pt"
        ensure_parent_exists(path)
        torch.save(checkpoint_state, path)
        logger.debug("Saved checkpoint to {}", path)

    def checkpoint_exists(self, name: str) -> bool:
        return (self.dir / f"{name}.pt").exists()

    def list_checkpoints(self) -> list[str]:
        if not self.dir.exists():
            return []
        return [path.stem for path in self.dir.iterdir() if path.is_file()]

    def load_checkpoint(self, name: str) -> Checkpoint:
        path = self.dir / f"{name}.pt"
        return self.load_checkpoint_from_path(path)

    @staticmethod
    def load_checkpoint_from_path(path: Path) -> Checkpoint:
        """
        Load a checkpoint from a specific path.

        :param path: The path to the checkpoint.
        :return: The loaded checkpoint.
        :raises FileNotFoundError: If the checkpoint file does not exist.
        """
        if not path.exists():
            raise FileNotFoundError("No checkpoint file found at", path)

        result = torch.load(path, weights_only=False)
        logger.debug("Loaded checkpoint from {}", path)
        return result

    def get_checkpoint_path(self, name: str) -> Path:
        return self.dir / f"{name}.pt"

    def reproduce(
        self,
        name: str,
        model: nn.Module,
        optimiser: Optimizer,
        generator: torch.Generator,
        scheduler: Optional[LRScheduler] = None,
        other_state: Optional[Saveable] = None,
    ) -> Checkpoint:
        """
        Reproduce the experiment state from a checkpoint.

        :param name: The name of the checkpoint.
        :param model: The PyTorch model.
        :param optimiser: The PyTorch optimizer.
        :param generator: The PyTorch random number generator.
        :param scheduler: The PyTorch learning rate scheduler.
        :param other_state: Any other state. Should be generated via Saveable interface.
        :return: The loaded checkpoint.
        """
        checkpoint = self.load_checkpoint(name)

        self._apply_checkpoint(
            checkpoint,
            model=model,
            optimiser=optimiser,
            generator=generator,
            scheduler=scheduler,
            other_state=other_state,
        )

        return checkpoint

    @staticmethod
    def _apply_checkpoint(
        checkpoint: Checkpoint,
        model: nn.Module,
        optimiser: Optimizer,
        generator: torch.Generator,
        scheduler: Optional[LRScheduler] = None,
        other_state: Optional[Saveable] = None,
    ) -> None:
        model.load_state_dict(checkpoint.model_state)
        optimiser.load_state_dict(checkpoint.optimiser_state)

        if scheduler is not None and checkpoint.scheduler_state is not None:
            scheduler.load_state_dict(checkpoint.scheduler_state)  # type: ignore
        if other_state is not None and checkpoint.other_state is not None:
            other_state.load_from_dict(checkpoint.other_state)  # type: ignore

        np.random.set_state(checkpoint.numpy_random_state)
        generator.set_state(checkpoint.torch_gen_state)

    @staticmethod
    def reproduce_from_path(
        path: Path,
        model: nn.Module,
        optimiser: Optimizer,
        generator: torch.Generator,
        scheduler: Optional[LRScheduler] = None,
        other_state: Optional[Saveable] = None,
    ) -> Checkpoint:
        """
        Reproduce the experiment state from a checkpoint at a specific path.

        (See CheckpointManager.reproduce for more details.)
        """
        checkpoint = CheckpointManager.load_checkpoint_from_path(path)

        CheckpointManager._apply_checkpoint(
            checkpoint,
            model=model,
            optimiser=optimiser,
            generator=generator,
            scheduler=scheduler,
            other_state=other_state,
        )

        return checkpoint

    def reproduce_model(self, model: nn.Module, name: str) -> Checkpoint:
        checkpoint = self.load_checkpoint(name)
        model.load_state_dict(checkpoint.model_state)
        return checkpoint

    @staticmethod
    def reproduce_model_from_path(model: nn.Module, path: Path) -> Checkpoint:
        checkpoint = CheckpointManager.load_checkpoint_from_path(path)
        model.load_state_dict(checkpoint.model_state)
        return checkpoint


@dataclass
class TrainerState(Saveable):
    """
    State of the trainer.
    """

    step: int
    samples_seen: int
    epoch: int
    best_val_loss: float
    val_loss: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "TrainerState":
        return TrainerState(
            step=data["step"],
            samples_seen=data["samples_seen"],
            epoch=data["epoch"],
            best_val_loss=data["best_val_loss"],
            val_loss=data["val_loss"],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def load_from_dict(self, data: dict[str, Any]) -> None:
        self.step = data["step"]
        self.samples_seen = data["samples_seen"]
        self.epoch = data["epoch"]
        self.best_val_loss = data["best_val_loss"]
        self.val_loss = data["val_loss"]
