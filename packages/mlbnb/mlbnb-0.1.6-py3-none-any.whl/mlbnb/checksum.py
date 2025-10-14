import numpy as np
import torch
from typing import Any
from collections.abc import Iterable


def compute_checksum(obj: Any, max_iterations=1000) -> float:
    """
    Compute a quick and dirty checksum for an object that contains
    torch tensors in any hierarchical structure. The checksum is
    computed as the sum of the absolute values of all tensors.
    This is not guaranteed to be unique, but it is a quick way to
    check if two objects are the same.

    Supported types:
        - torch.Tensor
        - np.ndarray
        - dict
        - iterables

    :param obj: The object to compute the checksum for.
    :param max_iterations: The maximum number of iterations to perform.
    """

    class State:
        def __init__(self):
            self.checksum = 0.0
            self.iterations = 0

    state = State()

    def _checksum(obj: Any) -> None:
        if state.iterations >= max_iterations:
            return

        state.iterations += 1

        if isinstance(obj, torch.Tensor):
            state.checksum += obj.abs().sum().item()
        elif isinstance(obj, np.ndarray):
            state.checksum += np.abs(obj).sum()
        elif isinstance(obj, dict):
            for k, v in obj.items():
                _checksum(k)
                _checksum(v)
                if state.iterations >= max_iterations:
                    return
        elif isinstance(obj, str):
            pass  # skip strings
        elif isinstance(obj, Iterable):
            for item in obj:
                _checksum(item)
                if state.iterations >= max_iterations:
                    return

    _checksum(obj)
    return state.checksum
