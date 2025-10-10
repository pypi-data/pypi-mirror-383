from __future__ import annotations

from enum import Enum
from typing import cast

import arrayfire_wrapper.lib as wrapper

from arrayfire import Array
from arrayfire.array_object import afarray_as_array
from arrayfire.dtypes import Dtype, float32


class RandomEngineType(Enum):
    PHILOX = 100  # PHILOX_4X32_10
    THREEFRY = 200  # THREEFRY_2X32_16
    MERSENNE = 300  # MERSENNE_GP11213


class RandomEngine:
    """
    Class to handle random number generator engines.

    Parameters
    ----------
    engine_type : RandomEngineType, optional, default: RandomEngineType.PHILOX
        Specifies the type of random engine to be created. Can be one of:
        - RandomEngineType.PHILOX
        - RandomEngineType.THREEFRY
        - RandomEngineType.MERSENNE

    seed : int, optional, default: 0
        Specifies the seed for the random engine.
    """

    def __init__(self, engine_type: RandomEngineType = RandomEngineType.PHILOX, seed: int = 0) -> None:
        """
        Initialize a random engine instance.

        Parameters
        ----------
        engine_type : RandomEngineType, optional, default: RandomEngineType.PHILOX
            Specifies the type of random engine to be created.

        seed : int, optional, default: 0
            Specifies the seed for the random engine.
        """
        self._engine = wrapper.create_random_engine(engine_type.value, seed)

    def __del__(self) -> None:
        """
        Destructor to release the random engine resources.
        """
        wrapper.release_random_engine(self._engine)
        return None

    def set_type(self, engine_type: RandomEngineType) -> None:
        """
        Set the type of the random engine.

        Parameters
        ----------
        engine_type : RandomEngineType
            Specifies the type of the random engine to be set.
        """
        wrapper.random_engine_set_type(self._engine, engine_type.value)
        return None

    def get_type(self) -> RandomEngineType:
        """
        Get the type of the random engine.

        Returns
        -------
        RandomEngineType
            The type of the random engine.
        """
        engine_type_value = wrapper.random_engine_get_type(self._engine)
        return RandomEngineType(engine_type_value)

    def set_seed(self, seed: int) -> None:
        """
        Set the seed for the random engine.

        Parameters
        ----------
        seed : int
            Specifies the seed to be set for the random engine.
        """
        wrapper.random_engine_set_seed(self._engine, seed)
        return None

    def get_seed(self) -> int:
        """
        Get the seed for the random engine.

        Returns
        -------
        int
            The seed value of the random engine.
        """
        return wrapper.random_engine_get_seed(self._engine)

    def get_engine(self) -> wrapper.AFRandomEngineHandle:
        """
        Get the ArrayFire random engine handle.

        Returns
        -------
        wrapper.AFRandomEngineHandle
            The ArrayFire random engine handle associated with this RandomEngine instance.
        """
        return self._engine

    @classmethod
    def from_engine(cls, engine: wrapper.AFRandomEngineHandle) -> RandomEngine:
        """
        Create a RandomEngine instance from an existing RandomEngine handle.

        Parameters
        ----------
        engine : wrapper.AFRandomEngineHandle
            The existing RandomEngine handle.

        Returns
        -------
        RandomEngine
            A new RandomEngine instance created from the provided engine handle.
        """
        instance = cls.__new__(cls)
        instance._engine = engine
        return instance


@afarray_as_array
def randn(shape: int | tuple[int, ...], /, *, dtype: Dtype = float32, engine: RandomEngine | None = None) -> Array:
    """
    Create a multi-dimensional array containing values sampled from a normal distribution with mean 0
    and standard deviation of 1.

    Parameters
    ----------
    shape : int | tuple[int, ...]
        The shape of the resulting array. Must be a tuple with at least one element, e.g., shape=(3,).

    dtype : Dtype, optional, default: `float32`
        The data type of the array elements.

    engine : RandomEngine | None, optional
        The random number generator engine to be used. If None, uses a default engine created by ArrayFire.

    Returns
    -------
    Array
        A multi-dimensional array whose elements are sampled from a normal distribution. The dimensions of the array
        are determined by `shape`:
        - If shape is (x,), the output is a 1D array of size (x,).
        - If shape is (x, y), the output is a 2D array of size (x, y).
        - If shape is (x, y, z), the output is a 3D array of size (x, y, z).
        - For more dimensions, the output shape corresponds directly to the specified `shape` tuple.

    Notes
    -----
    The function supports creating arrays of up to N dimensions, where N is determined by the length
    of the `shape` tuple.

    Raises
    ------
    ValueError
        If `shape` is not int or tuple with less than one value.
    """
    if isinstance(shape, int):
        shape = (shape,)

    if not isinstance(shape, tuple) or not shape:
        raise ValueError("Argument shape must be a tuple with at least 1 value.")

    if engine is None:
        return cast(Array, wrapper.randn(shape, dtype))

    return cast(Array, wrapper.random_normal(shape, dtype, engine.get_engine()))


@afarray_as_array
def randu(shape: int | tuple[int, ...], /, *, dtype: Dtype = float32, engine: RandomEngine | None = None) -> Array:
    """
    Create a multi-dimensional array containing values from a uniform distribution.

    Parameters
    ----------
    shape : int | tuple[int, ...]
        The shape of the resulting array. Must have at least 1 element, e.g., shape=(3,)

    dtype : Dtype, optional, default: float32
        Data type of the array.

    engine : RandomEngine | None, optional, default: None
        If engine is None, uses a default engine created by ArrayFire.

    Returns
    -------
    Array
        A multi-dimensional array whose elements are sampled uniformly between [0, 1].

    Notes
    -----
    The `shape` parameter determines the dimensions of the resulting array:
    - If shape is (x1,), the output is a 1D array of size (x1,).
    - If shape is (x1, x2), the output is a 2D array of size (x1, x2).
    - If shape is (x1, x2, x3), the output is a 3D array of size (x1, x2, x3).
    - If shape is (x1, x2, x3, x4), the output is a 4D array of size (x1, x2, x3, x4).

    Raises
    ------
    ValueError
        If shape is not a tuple or has less than one value.
    """
    if isinstance(shape, int):
        shape = (shape,)

    if not isinstance(shape, tuple) or not shape:
        raise ValueError("Argument shape must be a tuple with at least 1 value.")

    if engine is None:
        result = wrapper.randu(shape, dtype)
        return cast(Array, result)

    result = wrapper.random_uniform(shape, dtype, engine.get_engine())
    return cast(Array, result)
