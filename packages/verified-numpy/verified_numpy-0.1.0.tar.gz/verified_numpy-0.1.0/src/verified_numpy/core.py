"""
An improved, robust wrapper for NumPy arrays using functional and contract paradigms.

This module provides a `VerifiedArray` class that guarantees its instances
adhere to a specific, user-defined validation policy. It emphasizes:
1.  Immutability: All instances are read-only.
2.  Explicitness: Transformations must be performed via an explicit method.
3.  Type Safety: Generics track the array's data type through transformations.
4.  Composability: Validation policies are built from small, reusable functions.
"""

import functools as _ft
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Final,
    Generic,
    Iterable,
    List,
    Protocol,
    TypeVar,
    runtime_checkable,
)

import numpy as np
import numpy.typing as npt
from static_error_handler import Err, Ok, Result

# =======================
# Typing: generalized arrays with input/output distinction
# =======================

# Generic type for the array's data type.
DType = TypeVar("DType", bound=np.generic)
# A second generic type to precisely track the dtype of transformation outputs.
DTypeOut = TypeVar("DTypeOut", bound=np.generic)

Arr = npt.NDArray[DType]

# =======================
# Validators (pure, composable)
# =======================

# A validator is a pure function that returns a list of error strings.
# An empty list signifies success.
Validator = Callable[[npt.NDArray[Any]], List[str]]


def v_dtype(expected: npt.DTypeLike) -> Validator:
    """Returns a validator that checks for a specific dtype."""
    expected_dtype = np.dtype(expected)

    def _v(x: npt.NDArray[Any]) -> List[str]:
        return (
            []
            if x.dtype == expected_dtype
            else [f"Expected dtype {expected_dtype}, got {x.dtype}"]
        )

    return _v


def v_ndim(expected_ndim: int) -> Validator:
    """Returns a validator that checks for a specific number of dimensions."""

    def _v(x: npt.NDArray[Any]) -> List[str]:
        return (
            []
            if x.ndim == expected_ndim
            else [f"Expected {expected_ndim}D, got {x.ndim}D"]
        )

    return _v


def v_finite(x: npt.NDArray[Any]) -> List[str]:
    """Validator: fails if any non-finite (NaN, inf) values are present."""
    return [] if np.isfinite(x).all() else ["Non-finite values present"]


def v_nonempty(x: npt.NDArray[Any]) -> List[str]:
    """Validator: fails if the array has zero elements."""
    return [] if x.size > 0 else ["Array is empty"]


def v_row_major_contiguous(x: npt.NDArray[Any]) -> List[str]:
    """Validator: fails if the array is not C-style (row-major) contiguous."""
    return [] if x.flags["C_CONTIGUOUS"] else ["Array not C-contiguous"]


def _named(fn: Callable, name: str):
    """Internal helper to give a readable name to combined validators."""
    fn.__name__ = name
    fn.__qualname__ = name
    setattr(fn, "__pretty__", name)  # For custom reprs
    return fn


def combine(validators: Iterable[Validator]) -> Validator:
    """
    Combines multiple validators into a single one that runs them all.
    This version uses a simple, readable for-loop.
    """
    validators = tuple(validators)

    def apply_all(x: npt.NDArray[Any]) -> List[str]:
        all_errors: List[str] = []
        for v in validators:
            all_errors.extend(v(x))
        return all_errors

    # Create a descriptive name for the combined policy for easier debugging.
    names = " & ".join(
        getattr(v, "__pretty__", getattr(v, "__name__", v.__class__.__name__))
        for v in validators
    )
    return _named(apply_all, f"Policy[{names}]")


# =======================
# Verified Wrapper
# =======================


@runtime_checkable
class _ReadOnlyArrayLike(Protocol):
    """Protocol to signal array-interoperability for type checkers."""

    def __array__(self, dtype: npt.DTypeLike | None = None) -> np.ndarray: ...


@dataclass(frozen=True, slots=True)
class VerifiedArray(Generic[DType]):
    """
    An immutable, verified NumPy array wrapper.

    Invariants are defined by the attached `policy`. The wrapper guarantees
    that the contained `value` has passed this policy check. The underlying
    array is made read-only.
    """

    value: Arr[DType]
    policy: Validator

    # --- Construction and Immutability ---
    @staticmethod
    def _freeze(x: Arr[DTypeOut]) -> Arr[DTypeOut]:
        """Creates a read-only view of an array."""
        y = x.view()
        y.setflags(write=False)
        return y

    # --- NumPy Interoperability ---
    def __array__(self, dtype: npt.DTypeLike | None = None) -> np.ndarray:
        """Allows NumPy functions to treat this object as an array."""
        return np.asarray(self.value, dtype=dtype)

    # Higher priority ensures that `np.func(va, arr)` prefers our implementation.
    __array_priority__ = 1000

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """
        Handles NumPy ufuncs (e.g., np.sin, np.add).
        Returns a raw ndarray, forcing the user to explicitly re-verify.
        """
        # Replace any VerifiedArray inputs with their underlying raw arrays.
        new_inputs = tuple(
            (inp.value if isinstance(inp, VerifiedArray) else inp) for inp in inputs
        )
        return getattr(ufunc, method)(*new_inputs, **kwargs)

    # --- Explicit, Safe Attribute Access ---
    # Provide direct, safe access to common non-mutating properties.
    # This is clearer than __getattr__ and provides better IDE support.
    @property
    def shape(self) -> tuple[int, ...]:
        return self.value.shape

    @property
    def dtype(self) -> np.dtype[DType]:
        return self.value.dtype

    @property
    def ndim(self) -> int:
        return self.value.ndim

    @property
    def size(self) -> int:
        return self.value.size

    @property
    def T(self) -> Arr[DType]:
        return self.value.T

    # --- Stronger Contract Boundary: Disabling Operators ---
    def _raise_operator_error(self, *args, **kwargs):
        """Helper to raise a clear error for disabled operators."""
        raise TypeError(
            "Direct operators (+, -, *, etc.) are disabled on VerifiedArray to "
            "prevent accidental loss of verification. Use the .apply_and_verify() "
            "method for all transformations."
        )

    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = _raise_operator_error
    __pow__ = __rpow__ = __truediv__ = __rtruediv__ = __floordiv__ = (
        _raise_operator_error
    )
    __matmul__ = __rmatmul__ = _raise_operator_error

    # --- Core Transformation Method ---
    def apply_and_verify(
        self, f: Callable[[Arr[DType]], Arr[DTypeOut]], policy: Validator | None = None
    ) -> Result["VerifiedArray[DTypeOut]", str | List[str]]:
        """
        Applies a pure function to the underlying array and re-verifies the result.

        This is the primary method for performing safe transformations.
        The output type `DTypeOut` is tracked, preserving type safety.
        """
        p = self.policy if policy is None else policy
        try:
            result_array = f(self.value)
        except Exception as e:
            return Err(f"apply_and_verify: {e}")

        errors = p(result_array)
        if errors:
            return Err(errors)

        # Freeze the new array to maintain the immutability invariant.
        return Ok(VerifiedArray(VerifiedArray._freeze(result_array), p))


# =======================
# Smart Constructor
# =======================


def make_verified(
    x: Arr[DType], policy: Validator
) -> Result[VerifiedArray[DType], str | List[str]]:
    """
    Validates an array against a policy and wraps it in a VerifiedArray.

    This is the main entry point into the "verified" system.
    """
    try:
        errors = policy(x)
    except Exception as e:
        return Err(f"make_verified: {e}")
    if errors:
        return Err(errors)
    return Ok(VerifiedArray(VerifiedArray._freeze(x), policy))


# =======================
# "Verified-only" APIs
# =======================


def mean_of_verified(a: VerifiedArray[Any]) -> float:
    """Example function that only accepts a VerifiedArray."""
    # No need to check for finite values, dtype, etc. The contract guarantees it.
    return float(a.value.mean())


def normalize_rows(
    a: VerifiedArray[np.float64],
) -> Result[VerifiedArray[np.float64], List[str]]:
    """
    Example transformation that consumes and produces a VerifiedArray.
    The function logic can be simpler because it trusts its input.
    """

    def _f(x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        row_sums = x.sum(axis=1, keepdims=True)
        # Avoid division by zero
        safe_sums = np.where(row_sums == 0.0, 1.0, row_sums)
        return x / safe_sums

    # Re-verify the output with the same policy.
    return a.apply_and_verify(_f)


if __name__ == "__main__":
    # An example policy. Users can create their own by combining validators.
    verify_policy: Final[Validator] = combine(
        (
            v_dtype(np.float64),
            v_ndim(2),
            v_finite,
            v_nonempty,
            v_row_major_contiguous,
        )
    )
    # --- Happy Path: Create and use a valid array ---
    print("--- Basic Success Case ---")
    valid_np_array = np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]])
    va_res = make_verified(valid_np_array, policy=verify_policy)

    if va_res.is_ok():
        va = va_res.unwrap()
        print(f"Successfully created VerifiedArray with shape: {va.shape}")

        # Use safe, explicit properties
        print(f"Array dtype: {va.dtype}, ndim: {va.ndim}")

        # Use NumPy functions that work via __array__ protocol
        print(f"Sum calculated by NumPy: {np.sum(va)}")

        # --- Safe Transformation ---
        print("\n--- Safe Transformation via apply_and_verify ---")
        centered_res = va.apply_and_verify(lambda arr: arr - arr.mean())
        if centered_res.is_ok():
            centered_res_value = centered_res.unwrap()
            print(f"Centered array:\n{centered_res_value.value}")
        else:
            centered_res_error = centered_res.unwrap_err()
            print(f"Centering failed: {centered_res_error}")

        # --- Operator Error ---
        print("\n--- Testing Disabled Operator ---")
        try:
            # This will fail intentionally, demonstrating the strong contract boundary.
            result = va + 1
        except TypeError as e:
            print(f"Caught expected error: {e}")

    # --- Failure Path: Try to create an invalid array ---
    print("\n--- Failure Case (Wrong DType) ---")
    invalid_np_array = np.array([[1, 2], [3, 4]], dtype=np.int32)
    va_res_fail = make_verified(invalid_np_array, policy=verify_policy)

    if va_res_fail.is_err():
        va_res_fail_error = va_res_fail.unwrap_err()
        print(f"Verification failed as expected: {va_res_fail_error}")
