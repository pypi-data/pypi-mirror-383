from pathlib import Path
from typing import TypeAlias

from omegaconf import OmegaConf

from mlbnb.paths import (
    ExperimentPath,
    get_experiment_paths,
    get_experiment_paths_matching_config,
)

Config: TypeAlias = dict


def test_experiment_path_init(tmp_path: Path):
    """Test that the ExperimentPath is initialized correctly."""
    exp_path = ExperimentPath(tmp_path, "test_run")
    assert exp_path.root == tmp_path / "test_run"
    assert exp_path.name == "test_run"
    assert tmp_path.exists()


def test_experiment_path_from_path(tmp_path: Path):
    """Test that the ExperimentPath can be created from a path."""
    path = tmp_path / "test_run"
    exp_path = ExperimentPath.from_path(path)
    assert exp_path.root == path
    assert exp_path.name == "test_run"


def test_experiment_path_from_config(tmp_path: Path, monkeypatch):
    """Test that the ExperimentPath can be created from a config."""
    monkeypatch.setattr("mlbnb.paths.gen_run_name", lambda: "test_run")
    cfg = OmegaConf.create({"a": 1, "b": 2})
    exp_path = ExperimentPath.from_config(cfg, tmp_path)
    assert exp_path.root == tmp_path / "test_run"
    assert exp_path.name == "test_run"
    config_path = exp_path / "cfg.yaml"
    assert config_path.exists()
    loaded_cfg = OmegaConf.load(config_path)
    assert loaded_cfg == cfg


def test_experiment_path_get_config(tmp_path: Path):
    """Test that the config can be loaded from an ExperimentPath."""
    exp_path = ExperimentPath(tmp_path, "test_run")
    config_path = exp_path / "cfg.yaml"
    cfg = OmegaConf.create({"a": 1, "b": 2})
    OmegaConf.save(cfg, config_path)
    loaded_cfg = exp_path.get_config()
    assert loaded_cfg == cfg


def test_experiment_path_dunder_methods(tmp_path: Path):
    """Test the dunder methods of ExperimentPath."""
    exp_path = ExperimentPath(tmp_path, "test_run")
    assert str(exp_path) == str(tmp_path / "test_run")
    assert repr(exp_path) == f"ExperimentPath({tmp_path / 'test_run'})"
    assert exp_path / "file.txt" == tmp_path / "test_run" / "file.txt"


def create_dummy_experiment(root: Path, name: str, cfg: Config) -> ExperimentPath:
    """Create a dummy experiment for testing."""
    exp_path = ExperimentPath(root, name)
    config_path = exp_path / "cfg.yaml"
    OmegaConf.save(cfg, config_path)
    return exp_path


def test_get_experiment_paths(tmp_path: Path):
    """Test that all experiment paths can be retrieved."""
    create_dummy_experiment(tmp_path, "run1", {"a": 1})
    create_dummy_experiment(tmp_path, "run2", {"a": 2})
    paths = get_experiment_paths(tmp_path)
    assert len(paths) == 2


def test_get_experiment_paths_with_predicate(tmp_path: Path):
    """Test that experiment paths can be filtered with a predicate."""
    create_dummy_experiment(tmp_path, "run1", {"a": 1})
    create_dummy_experiment(tmp_path, "run2", {"a": 2})
    paths = get_experiment_paths(tmp_path, lambda cfg: cfg.a == 1)
    assert len(paths) == 1
    assert paths[0].name == "run1"


def test_get_experiment_paths_with_multiple_predicates(tmp_path: Path):
    """Test that experiment paths can be filtered with multiple predicates."""
    create_dummy_experiment(tmp_path, "run1", {"a": 1, "b": 1})
    create_dummy_experiment(tmp_path, "run2", {"a": 1, "b": 2})
    create_dummy_experiment(tmp_path, "run3", {"a": 2, "b": 2})
    predicates = [lambda cfg: cfg.a == 1, lambda cfg: cfg.b == 2]
    paths = get_experiment_paths(tmp_path, predicates)
    assert len(paths) == 1
    assert paths[0].name == "run2"


def test_get_experiment_paths_matching_config(tmp_path: Path):
    """Test that experiment paths can be retrieved by matching a config."""
    cfg1 = {"a": 1, "b": {"c": 3}}
    cfg2 = {"a": 2, "b": {"c": 4}}
    create_dummy_experiment(tmp_path, "run1", cfg1)
    create_dummy_experiment(tmp_path, "run2", cfg2)
    create_dummy_experiment(tmp_path, "run3", cfg2)

    query_cfg = OmegaConf.create(cfg2)
    paths = get_experiment_paths_matching_config(query_cfg, tmp_path)
    assert len(paths) == 2
    assert {path.name for path in paths} == {"run2", "run3"}
