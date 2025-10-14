import pytest
from typing import List

from mlbnb.examples import find_best_examples


class DummyTask:
    def __init__(self, difficulty: float):
        self.difficulty = difficulty

    def __repr__(self) -> str:
        return f"Task(difficulty={self.difficulty})"


def dummy_loss_fn(task: DummyTask) -> float:
    return abs(task.difficulty - 5)


@pytest.fixture
def tasks() -> List[DummyTask]:
    return [DummyTask(difficulty) for difficulty in range(1, 10)]


def test_find_easiest_examples(tasks: List[DummyTask]) -> None:
    easiest_examples, losses = find_best_examples(
        tasks, dummy_loss_fn, 3, mode="easiest"
    )
    assert [task.difficulty for task in easiest_examples] == [5, 6, 4]
    assert losses == [0.0, 1.0, 1.0]


def test_find_hardest_examples(tasks: List[DummyTask]) -> None:
    hardest_examples, losses = find_best_examples(
        tasks, dummy_loss_fn, 3, mode="hardest"
    )

    assert [task.difficulty for task in hardest_examples] == [9, 1, 8]
    assert losses == [4.0, 4.0, 3.0]


def test_find_easiest_examples_with_fewer_tasks() -> None:
    tasks = [DummyTask(1), DummyTask(2)]
    easiest_examples, losses = find_best_examples(
        tasks, dummy_loss_fn, 3, mode="easiest"
    )
    assert [task.difficulty for task in easiest_examples] == [2, 1]
    assert losses == [3.0, 4.0]


def test_find_hardest_examples_with_fewer_tasks() -> None:
    tasks = [DummyTask(1), DummyTask(2)]
    hardest_examples, losses = find_best_examples(
        tasks, dummy_loss_fn, 3, mode="hardest"
    )
    assert [task.difficulty for task in hardest_examples] == [1, 2]
    assert losses == [4.0, 3.0]


def test_find_easiest_examples_with_zero_tasks() -> None:
    tasks: List[DummyTask] = []
    easiest_examples, losses = find_best_examples(
        tasks, dummy_loss_fn, 3, mode="easiest"
    )
    assert easiest_examples == []
    assert losses == []


def test_find_hardest_examples_with_zero_tasks() -> None:
    tasks: List[DummyTask] = []
    hardest_examples, losses = find_best_examples(
        tasks, dummy_loss_fn, 3, mode="hardest"
    )
    assert hardest_examples == []
    assert losses == []


def test_find_easiest_examples_with_exact_num_examples(tasks: List[DummyTask]) -> None:
    easiest_examples, losses = find_best_examples(
        tasks, dummy_loss_fn, 10, mode="easiest"
    )
    assert [task.difficulty for task in easiest_examples] == [5, 6, 4, 7, 3, 8, 2, 9, 1]
    assert losses == [0.0, 1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0]


def test_find_hardest_examples_with_exact_num_examples(tasks: List[DummyTask]) -> None:
    hardest_examples, losses = find_best_examples(
        tasks, dummy_loss_fn, 10, mode="hardest"
    )
    assert [task.difficulty for task in hardest_examples] == [9, 1, 8, 2, 7, 3, 6, 4, 5]
    assert losses == [4.0, 4.0, 3.0, 3.0, 2.0, 2.0, 1.0, 1.0, 0.0]
