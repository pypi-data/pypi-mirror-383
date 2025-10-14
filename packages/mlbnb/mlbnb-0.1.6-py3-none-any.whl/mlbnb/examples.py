from heapq import heappop, heappush
from typing import Callable, Iterable, Literal, TypeVar

T = TypeVar("T")
M = TypeVar("M")


def find_best_examples(
    tasks: Iterable[T],
    compute_task_loss: Callable[[T], float],
    num_examples: int,
    mode: Literal["easiest", "hardest"] = "easiest",
) -> tuple[list[T], list[float]]:
    """
    Find the best examples in a dataset according to a given loss function.

    NOTE: Each task should be an individual task and not a batch of tasks.

    :param tasks: The tasks to evaluate.
    :param compute_task_loss: Should use a model to compute the loss of a task.
    :param num_examples: The number of examples to return.
    :param mode: The mode to use for determining the best examples. Either "easiest" or "hardest".
    :return: A list of the best examples and their corresponding losses.
    """

    examples = []

    count = 0

    for task in tasks:
        loss = compute_task_loss(task)

        if mode == "easiest":
            # If the first value in the tuple already exists, the second value is used to
            # break ties. Add a count so that T doesn't have to be sized.
            heappush(examples, (-loss, count, task))
        else:
            heappush(examples, (loss, count, task))

        if len(examples) > num_examples:
            heappop(examples)

        count += 1

    examples = sorted(examples, reverse=True)

    tasks = [example[-1] for example in examples]
    losses = [example[0] for example in examples]
    losses = [-loss for loss in losses] if mode == "easiest" else losses

    return tasks, losses
