class EarlyStopper:
    """
    Early stopper class to stop training when the model stops improving.
    """

    def __init__(self, patience: int = 5):
        """
        :param patience: Number of epochs without improvement before stopping training.
        """
        self.patience = patience
        self.best_loss = float("inf")
        self.epochs_without_improvement = 0

    def should_stop(self, loss: float) -> bool:
        """
        :param score: The score to compare with the best score.
        :return: True if the model should stop training, False otherwise.
        """
        if loss < self.best_loss:
            self.best_loss = loss
            self.epochs_without_improvement = 0
        else:
            self.epochs_without_improvement += 1
        return self.epochs_without_improvement > self.patience
