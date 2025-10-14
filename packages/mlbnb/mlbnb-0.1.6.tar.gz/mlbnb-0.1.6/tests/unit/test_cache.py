import pytest
import torch
from torch.utils.data import Dataset

from mlbnb.cache import CachedDataset


class RandomDataset(Dataset):
    def __init__(self, size: int):
        self.size = size

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return torch.rand(1)


@pytest.fixture
def random_dataset() -> RandomDataset:
    return RandomDataset(10)


# Make sure that without cache, we get different values every time.
def test_random_dataset_is_random(random_dataset: RandomDataset):
    checksum = 0

    for i in range(len(random_dataset)):
        checksum += random_dataset[i].item()

    checksum2 = 0

    for i in range(len(random_dataset)):
        checksum2 += random_dataset[i].item()

    # There is technically a chance that this test will fail, but it is very low.
    assert checksum != checksum2


def test_cached_dataset(random_dataset: RandomDataset):
    cached_dataset = CachedDataset(random_dataset)

    checksum = 0

    for i in range(len(cached_dataset)):
        checksum += cached_dataset[i].item()

    checksum2 = 0

    for i in range(len(cached_dataset)):
        checksum2 += cached_dataset[i].item()

    assert checksum == checksum2
