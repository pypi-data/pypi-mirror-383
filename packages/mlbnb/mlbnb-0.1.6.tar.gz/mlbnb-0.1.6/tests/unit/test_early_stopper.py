import pytest

from mlbnb.early_stopper import EarlyStopper


@pytest.fixture
def early_stopper() -> EarlyStopper:
    return EarlyStopper(5)


def test_early_stopper_no_improvement(early_stopper: EarlyStopper):
    # Gets worse and worse
    assert not early_stopper.should_stop(0.1)
    assert not early_stopper.should_stop(0.2)
    assert not early_stopper.should_stop(0.3)
    assert not early_stopper.should_stop(0.4)
    assert not early_stopper.should_stop(0.5)
    assert not early_stopper.should_stop(0.6)
    # Should stop after 5 epochs without improvement
    assert early_stopper.should_stop(0.7)


def test_early_stopper_rollercoaster(early_stopper: EarlyStopper):
    # Gets worse and worse
    assert not early_stopper.should_stop(0.1)
    assert not early_stopper.should_stop(0.2)
    assert not early_stopper.should_stop(0.15)
    assert not early_stopper.should_stop(0.25)
    assert not early_stopper.should_stop(0.0)
    assert not early_stopper.should_stop(0.0)
    assert not early_stopper.should_stop(0.1)
    assert not early_stopper.should_stop(0.2)
    assert not early_stopper.should_stop(0.15)
    assert not early_stopper.should_stop(0.1)
    assert early_stopper.should_stop(0.2)
