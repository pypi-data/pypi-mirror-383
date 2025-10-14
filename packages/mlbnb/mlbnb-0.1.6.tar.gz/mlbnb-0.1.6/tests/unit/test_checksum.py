from mlbnb.checksum import compute_checksum
import torch


def test_single_tensor():
    tensor = torch.tensor([1.0, -2.0, 3.0])
    expected_checksum = 6.0  # |1.0| + |-2.0| + |3.0|
    assert compute_checksum(tensor) == expected_checksum


def test_nested_list_of_tensors():
    tensors = [torch.tensor([1.0, -2.0]), torch.tensor([3.0, -4.0])]
    expected_checksum = 10.0  # |1.0| + |-2.0| + |3.0| + |-4.0|
    assert compute_checksum(tensors) == expected_checksum


def test_nested_dict_of_tensors():
    tensors = {"a": torch.tensor([1.0, -2.0]), "b": {"c": torch.tensor([3.0, -4.0])}}
    expected_checksum = 10.0  # |1.0| + |-2.0| + |3.0| + |-4.0|
    assert compute_checksum(tensors) == expected_checksum


def test_mixed_structure():
    mixed_structure = {
        "a": torch.tensor([1.0, -2.0]),
        "b": [torch.tensor([3.0, -4.0]), {"c": torch.tensor([5.0, -6.0])}],
    }
    expected_checksum = 21.0  # |1.0| + |-2.0| + |3.0| + |-4.0| + |5.0| + |-6.0|
    assert compute_checksum(mixed_structure) == expected_checksum


def test_empty_structure():
    assert compute_checksum([]) == 0.0
    assert compute_checksum({}) == 0.0


def test_non_tensor_elements():
    mixed_structure = {
        "a": torch.tensor([1.0, -2.0]),
        "b": [3, "string", torch.tensor([3.0, -4.0]), {"c": torch.tensor([5.0, -6.0])}],
    }
    expected_checksum = 21.0  # |1.0| + |-2.0| + |3.0| + |-4.0| + |5.0| + |-6.0|
    assert compute_checksum(mixed_structure) == expected_checksum
