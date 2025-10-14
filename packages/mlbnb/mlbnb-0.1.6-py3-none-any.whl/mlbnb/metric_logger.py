import wandb

from mlbnb.checkpoint import TrainerState


class WandbLogger:
    """
    A class for logging metrics to the console and Weights & Biases.

    :param use_wandb: Whether to use Weights & Biases for logging.
    :param flush_interval_sec: The frequency at which to log metrics in seconds.
    :param train_state: The current state of the training process.
    """

    def __init__(self, use_wandb: bool, train_state: TrainerState):
        self.use_wandb = use_wandb
        self.train_state = train_state

    def log(self, metrics: dict[str, float]) -> None:
        """Log the metrics for the given step."""
        if self.use_wandb:
            metrics["samples_seen"] = self.train_state.samples_seen
            wandb.log(metrics, step=self.train_state.step, commit=False)
