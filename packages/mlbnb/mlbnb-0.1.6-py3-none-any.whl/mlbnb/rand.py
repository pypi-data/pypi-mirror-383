import random
import numpy as np
import pandas as pd
import torch
from loguru import logger
from typing import TypeVar

T = TypeVar("T", pd.DataFrame, pd.Series)


def seed_everything(seed: int) -> None:
    """Seed all default random number generators."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def sample(df: T, n: int, gen: np.random.Generator = np.random.default_rng()) -> T:
    """
    Sample n rows from a DataFrame or Series.

    :param df: The DataFrame or Series to sample from.
    :param n: The number of rows to sample.
    :param gen: (Optional) The random number generator to use.
    """
    if n >= len(df):
        logger.warning("Sampling %d rows from a DataFrame with %d rows", n, len(df))
        return df
    return df.sample(n, random_state=gen)


def split(
    df: T,
    frac: float,
    gen: np.random.Generator = np.random.default_rng(),
) -> tuple[T, T]:
    """
    Split a DataFrame/Series into two parts.

    :param df: The DataFrame/Series to split.
    :param frac: The fraction of the DataFrame/Series to include in the first part.
    :param gen: (Optional) The random number generator to use.
    """
    left_idxs = df.sample(frac=frac, random_state=gen).index
    right_idxs = df.index.difference(left_idxs)
    return df.loc[left_idxs], df.loc[right_idxs]
