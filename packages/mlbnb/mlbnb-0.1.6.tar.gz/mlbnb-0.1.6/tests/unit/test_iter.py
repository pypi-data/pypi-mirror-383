from typing import Any, Generator, List

from mlbnb.iter import StepIterator


def test_step_iterator_basic() -> None:
    data: List[int] = [1, 2, 3]
    steps: int = 5
    iterator: StepIterator[int] = StepIterator(data, steps)
    result: List[int] = list(iterator)
    assert len(result) == steps
    assert result == [1, 2, 3, 1, 2]


def test_step_iterator_exact_steps() -> None:
    data: List[int] = [1, 2, 3]
    steps: int = 3
    iterator: StepIterator[int] = StepIterator(data, steps)
    result: List[int] = list(iterator)
    assert len(result) == steps
    assert result == [1, 2, 3]


def test_step_iterator_more_data_than_steps() -> None:
    data: List[int] = [1, 2, 3, 4, 5]
    steps: int = 3
    iterator: StepIterator[int] = StepIterator(data, steps)
    result: List[int] = list(iterator)
    assert len(result) == steps
    assert result == [1, 2, 3]


def test_step_iterator_zero_steps() -> None:
    data: List[int] = [1, 2, 3]
    steps: int = 0
    iterator: StepIterator[int] = StepIterator(data, steps)
    result: List[int] = list(iterator)
    assert len(result) == steps
    assert result == []


def test_step_iterator_empty_delegate() -> None:
    data: List[Any] = []
    steps: int = 5
    iterator: StepIterator[Any] = StepIterator(data, steps)
    result: List[Any] = list(iterator)
    assert len(result) == 0
    assert result == []


def test_step_iterator_with_generator_delegate() -> None:
    def gen_data() -> Generator[int, None, None]:
        yield 1
        yield 2
        yield 3

    steps: int = 5
    iterator: StepIterator[int] = StepIterator(gen_data(), steps)
    result: List[int] = list(iterator)
    # When delegate is a one-time generator, StepIterator should yield only its content once
    assert len(result) == 3
    assert result == [1, 2, 3]
