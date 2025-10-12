import pytest

import verified_numpy as vn
import numpy as np
from typing import Final

def test_core():
    # An example policy. Users can create their own by combining validators.
    verify_policy: Final[vn.Validator] = vn.combine((
        vn.v_dtype(np.float64),
        vn.v_ndim(2),
        vn.v_finite,
        vn.v_nonempty,
        vn.v_row_major_contiguous,
    ))
    # --- Happy Path: Create and use a valid array ---
    print("--- Basic Success Case ---")
    valid_np_array = np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]])
    va_res = vn.make_verified(valid_np_array, policy=verify_policy)

    if va_res.is_ok():
        va = va_res.value
        print(f"Successfully created VerifiedArray with shape: {va.shape}")

        # Use safe, explicit properties
        print(f"Array dtype: {va.dtype}, ndim: {va.ndim}")

        # Use NumPy functions that work via __array__ protocol
        print(f"Sum calculated by NumPy: {np.sum(va)}")

        # --- Safe Transformation ---
        print("\n--- Safe Transformation via apply_and_verify ---")
        centered_res = va.apply_and_verify(lambda arr: arr - arr.mean())
        if centered_res.is_ok():
            print(f"Centered array:\n{centered_res.value.value}")
        else:
            print(f"Centering failed: {centered_res.error}")

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
    va_res_fail = vn.make_verified(invalid_np_array, policy=verify_policy)

    if va_res_fail.is_err():
        print(f"Verification failed as expected: {va_res_fail.error}")
