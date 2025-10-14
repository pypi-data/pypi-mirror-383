from pathlib import Path
from typing import Any, Callable

from loguru import logger
from omegaconf import DictConfig, OmegaConf

from mlbnb.file import ensure_exists
from mlbnb.namegen import gen_run_name


class ExperimentPath:
    root: Path
    name: str

    def __init__(self, root: Path | str, name: str):
        self.root = Path(root) / name
        self.name = name
        ensure_exists(self.root)

    @staticmethod
    def from_config(cfg: Any, root: Path) -> "ExperimentPath":
        """
        Create an ExperimentPath from a config object and a root directory.
        Generates a new run name and saves the config to cfg.yaml in the new path.

        :param cfg: The configuration object to save.
        :param root: The root directory where the experiment will be created.
        """
        new_name = gen_run_name()
        path = ExperimentPath(root, new_name)

        config_path = path / "cfg.yaml"
        OmegaConf.save(cfg, config_path)
        return path

    @staticmethod
    def from_path(path: Path) -> "ExperimentPath":
        """
        Create an ExperimentPath from an existing path.

        :param path: The path to the experiment directory.
        """
        return ExperimentPath(path.parent, path.name)

    def get_config(self) -> DictConfig:
        """
        Load the config file associated with this experiment path.
        """
        config_path = self / "cfg.yaml"
        config = OmegaConf.load(config_path)
        return config  # type: ignore

    def __str__(self) -> str:
        return str(self.root)

    def __repr__(self) -> str:
        return f"ExperimentPath({self.root})"

    def __truediv__(self, other: str) -> Path:
        return self.root / other


PredicateType = Callable[[Any], bool]


def get_experiment_paths(
    root: Path, predicates: PredicateType | list[PredicateType] = lambda _: True
) -> list[ExperimentPath]:
    """
    Get all experiment paths in a directory matching a filter.

    :param root: The root directory to recursively search in.
    :param predicates: A filter (or list of filters) that takes a config
        object and returns whether or not the path should be included.
    """
    if not isinstance(predicates, list):
        predicates = [predicates]

    paths = root.rglob("*/cfg.yaml")
    paths = [ExperimentPath.from_path(path.parent) for path in paths]
    paths = [
        path for path in paths if _matches_predicates(path.get_config(), predicates)
    ]
    logger.info("Found {} matching experiment path(s)", len(paths))
    return paths


def _matches_predicates(cfg: Any, predicates: list[PredicateType]) -> bool:
    return all(predicate(cfg) for predicate in predicates)


def get_experiment_paths_matching_config(
    query_cfg: Any, root: Path
) -> list[ExperimentPath]:
    """
    Get all experiment paths that match the entire config.

    :param query_cfg: The DictConfig object to match against.
    :param root: The root directory to search in.
    """
    query_yaml = OmegaConf.to_yaml(query_cfg)

    def matches_entire_cfg(cfg: Any) -> bool:
        cfg_yaml = OmegaConf.to_yaml(cfg)
        return cfg_yaml == query_yaml

    return get_experiment_paths(root, matches_entire_cfg)
