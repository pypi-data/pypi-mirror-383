from __future__ import annotations

import bisect
import os
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    List,
    Sequence,
)

import numpy as np
import numpy.typing as npt
from loguru import logger


@dataclass
class Coordinate:
    name: str
    values: npt.NDArray[np.float32]
    is_sorted: bool


@dataclass
class LabelledArrayMetadata:
    coords: list[Coordinate]
    shape: tuple[int, ...]
    dtype: np.dtype


ContiguousIndexType = int | slice
IndexType = ContiguousIndexType | list[int]


class LabelledArray:
    def __init__(
        self,
        data: npt.NDArray[Any],
        coords: List[Coordinate],
    ) -> None:
        self._validate(data, coords)

        self.data = data
        self.coords = coords

    def _validate(self, data: npt.NDArray[Any], coords: List[Coordinate]):
        if len(coords) != data.ndim:
            raise ValueError(
                "Number of coordinates must match number of dimensions in data"
            )

        for i, coord in enumerate(coords):
            if len(coord.values) != data.shape[i]:
                raise ValueError(
                    f"Length of coordinate `{coord.name}` must match the "
                    f"length of the data along dimension {i}, found "
                    f"{len(coord.values)} and {data.shape[i]} respectively."
                )

    def sel(self, **index_coords: Any) -> LabelledArray:
        indices = self._find_indices(**index_coords)

        # Select the data.
        sliced_data = self.data
        sliced_coords = []
        for i, (coord, idx) in enumerate(zip(self.coords, indices)):
            # TODO: Does this work?
            if idx is slice(None):
                sliced_coords.append(coord)
                continue

            sliced_data = np.take(sliced_data, idx, axis=i)
            sliced_coord = Coordinate(
                name=coord.name,
                values=np.take(coord.values, idx),
                is_sorted=coord.is_sorted,
            )

            sliced_coords.append(sliced_coord)

        return LabelledArray(data=sliced_data, coords=sliced_coords)

    # TODO jonas: Type hints
    def _find_indices(self, **index_coords: Any) -> tuple[Any, ...]:
        """
        Find the indices of the given coordinate values in the LabelledArray.

        Args:
            index_coords: Dictionary of coordinate names and their values.

        Returns:
            List of indices for each coordinate in the LabelledArray.
        """

        for key, val in index_coords.items():
            if not _is_list_like(val):
                index_coords[key] = [val]

        indices: list[list[int] | None] = []
        for coord in self.coords:
            if coord.name not in index_coords:
                indices.append(None)
                continue

            coord_indices: list[int] = []
            # Search for the index of the value in the coordinate.
            for value in index_coords[coord.name]:
                if coord.is_sorted:
                    index = bisect.bisect_left(coord.values, value)
                    assert coord.values[index] == value, (
                        f"Value {value} not found in coord {coord.name}"
                    )
                    coord_indices.append(index)

                else:
                    index = int(np.where(coord.values == value)[0][0])
                    coord_indices.append(index)

            indices.append(coord_indices)

        return tuple(indices)

    def set_at(self, value: npt.NDArray[Any], **index_coords: Any) -> None:
        """
        Set the value at a specific coordinate in the LabelledArray.

        Args:
            value: Value to set.
            index_coords: Dictionary of coordinate names and their values.
        """

        indices = self._find_indices(**index_coords)
        indices = _simplify_indices(indices)

        self.data[indices] = value


class MemmapLabelledArray(LabelledArray):
    def __init__(self, data: np.memmap, coords: list[Coordinate]):
        super().__init__(data, coords)
        self.data = data

    @staticmethod
    def allocate_new(
        filepath: str | Path,
        shape: tuple[int, ...],
        coord_names: Sequence[str],
        coord_values: Sequence[Sequence[Any]],
        dtype: np.dtype = np.dtype(np.float32),
        max_size_gb: int = 50,
    ) -> MemmapLabelledArray:
        """
        Creates and saves a zeros-filled memmap-based LabelledArray at the
        specified path.
        """
        MemmapLabelledArray._validate_allocation(
            shape, coord_names, coord_values, dtype, max_size_gb
        )

        coords = []

        for name, values in zip(coord_names, coord_values):
            is_sorted = _dim_is_sorted(values)
            val_arr = np.array(values)
            coords.append(Coordinate(name, val_arr, is_sorted))

        filepath = Path(filepath)
        os.makedirs(filepath, exist_ok=True)

        metadata = LabelledArrayMetadata(coords, shape, dtype)

        with open(filepath / "metadata.pkl", "wb") as f:
            pickle.dump(metadata, f)

        data_memmap = np.memmap(
            filename=filepath / "data.memmap",
            dtype=dtype,
            mode="w+",
            shape=shape,
        )

        data_memmap[...] = np.nan
        data_memmap.flush()
        return MemmapLabelledArray(
            data=data_memmap,
            coords=coords,
        )

    @staticmethod
    def _validate_allocation(
        shape: tuple[int, ...],
        coord_names: Sequence[str],
        coord_values: Sequence[Sequence[Any]],
        dtype: np.dtype,
        max_size_gb: int,
    ) -> None:
        if len(shape) != len(coord_names):
            raise ValueError(
                f"""Length of shape {shape} ({len(shape)}) must match length of
                coord_names {coord_names} ({len(coord_names)})"""
            )

        for name, values in zip(coord_names, coord_values):
            if len(values) != shape[coord_names.index(name)]:
                raise ValueError(
                    f"""Length of values {len(values)} for coord {name} must match
                    shape along that dimension {shape[coord_names.index(name)]}"""
                )

        size_gb = compute_array_size_gb(shape, dtype)
        if size_gb > max_size_gb:
            raise ValueError(f"""Allocating a memmap of shape {shape} requires
                             {size_gb} GB of space, which exceeds the maximum
                             of {max_size_gb}. If this is intentional, increase
                             the value of max_size_gb.""")
        logger.info("Allocating memory map of size {}", size_gb)

    @staticmethod
    def load_from_path(filepath: str | Path) -> MemmapLabelledArray:
        """
        Loads a memmap-based LabelledArray from the specified path.
        """
        filepath = Path(filepath)
        with open(filepath / "metadata.pkl", "rb") as f:
            metadata: LabelledArrayMetadata = pickle.load(f)

        data_memmap = np.memmap(
            filename=filepath / "data.memmap",
            dtype=metadata.dtype,
            mode="r",
            shape=metadata.shape,
        )

        return MemmapLabelledArray(
            data=data_memmap,
            coords=metadata.coords,
        )

    def set_at(
        self, value: np.ndarray[Any, np.dtype[Any]], **index_coords: Any
    ) -> None:
        super().set_at(value, **index_coords)
        self.data.flush()


def compute_array_size_gb(shape: tuple[int, ...], dtype: np.dtype) -> float:
    file_size = np.prod(shape) * dtype.itemsize
    return float(file_size / (1024**3))


def filter_variables(variables: Sequence[str], exclude: Sequence[str]) -> List[str]:
    return [var for var in variables if var not in exclude]


def _dim_is_sorted(values: Sequence[Any]) -> bool:
    """
    Check if a dimension is sorted.
    """
    if isinstance(values, np.ndarray):
        return bool(np.all(np.diff(values).astype(float) >= 0))
    else:
        return all(values[i] <= values[i + 1] for i in range(len(values) - 1))


def _simplify_indices(
    indices: Sequence[list[int] | None],
) -> tuple[int | slice, ...]:
    """
    Simplifies advanced indices to basic indices or throws.
    """
    simplified_indices: list[int | slice] = []
    for idx in indices:
        if isinstance(idx, list):
            simplified_indices.append(_try_simplify_list(idx))
        elif idx is None:
            simplified_indices.append(slice(None))
        else:
            raise ValueError(f"Unexpected index type: {type(idx)}")

    return tuple(simplified_indices)


def _try_simplify_list(idx_list: list[int]) -> slice | int:
    if len(idx_list) == 1:
        return idx_list[0]

    query_idx = idx_list[0]
    for idx in idx_list[1:]:
        if idx == query_idx + 1:
            query_idx += 1
            continue
        raise ValueError(
            """Failed to turn the passed indices into a slice. This happens
            when passed coordinates are not consecutive elements."""
        )

    return slice(idx_list[0], idx_list[-1] + 1)


def _is_list_like(obj: Any) -> bool:
    if isinstance(obj, Sequence):
        return True
    if isinstance(obj, np.ndarray):
        return True
    return False
