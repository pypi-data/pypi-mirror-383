import functools
import time
from types import TracebackType
from typing import Any, Callable, Iterable, Iterator, Optional, Type, TypeVar

from mlbnb.metric_logger import WandbLogger

T = TypeVar("T")


class WandbProfiler:
    def __init__(
        self,
        wandb_logger: WandbLogger,
        prefix: str = "timings_ms",
    ):
        self.wandb_logger = wandb_logger
        self.prefix = prefix

    def profiled(self, name: str) -> Callable[[T], T]:
        """
        Returns a function that profiles any operation passed to it.
        Usage: p = TrainingProfiler(); result = p.profiled("forward")(model(x))

        :param name: The name of the operation to profile.
        """
        start_time = time.perf_counter()

        def timed_call(result: T) -> T:
            # T is the type returned by the function being profiled.
            elapsed_time_ms = (time.perf_counter() - start_time) * 1000
            self.log(name, elapsed_time_ms)
            return result

        return timed_call

    def log(self, name: str, elapsed_time_ms: float) -> None:
        self.wandb_logger.log({f"{self.prefix}/{name}": elapsed_time_ms})

    def profiled_iter(self, name: str, iterable: Iterable[T]) -> Iterator[T]:
        """
        Profile each iteration of an iterator.
        Usage: for batch in profiler.iter("data_loading", dataloader):

        :param name: The name of the operation to profile.
        :param iterable: The iterable to profile.
        """
        iterator = iter(iterable)
        while True:
            try:
                yield self.profiled(name)(next(iterator))
            except StopIteration:
                break

    def profiled_function(
        self, name: str
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to profile a function.
        Usage: @profiler.profiled_function("data_loading")

        :param name: The name of the operation to profile.
        """

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self.profiled(name)(func(*args, **kwargs))

            return wrapper

        return decorator

    def profile(self, name: str) -> "ProfileContext":
        """
        Context manager for profiling a section of code.
        Usage: with profiler.profile("data_processing"):
                    # code to profile
        :param name: The name of the operation to profile.
        """
        return ProfileContext(self, name)


class ProfileContext:
    """Context manager for profiling code sections."""

    def __init__(self, profiler: WandbProfiler, name: str):
        self.profiler = profiler
        self.name = name
        self.start_time = 0.0

    def __enter__(self) -> "ProfileContext":
        self.start_time = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        elapsed_time_ms = (time.perf_counter() - self.start_time) * 1000
        self.profiler.log(self.name, elapsed_time_ms)
