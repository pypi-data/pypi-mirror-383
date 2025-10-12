import numpy as np
import pytest
import verified_numpy as vn

@pytest.fixture
def policy2d_float64():
    return vn.combine((vn.v_dtype(np.float64), vn.v_ndim(2), vn.v_finite, vn.v_row_major_contiguous))

def test_apply_and_verify_success(policy2d_float64):
    arr = np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]])
    vr = vn.make_verified(arr, policy=policy2d_float64)
    va = vr.value
    res = va.apply_and_verify(lambda a: a - a.mean())
    assert res.is_ok(), res.error
    centered = res.value
    # still verified and dtype preserved
    assert centered.dtype == np.float64
    assert centered.ndim == 2

def test_apply_and_verify_breaks_policy_dtype(policy2d_float64):
    arr = np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]])
    va = vn.make_verified(arr, policy=policy2d_float64).value
    # Transformation that breaks dtype requirement
    out = va.apply_and_verify(lambda a: a.astype(np.int32))
    assert out.is_err()
    assert "dtype" in str(out.error).lower()

def test_apply_and_verify_breaks_policy_ndim(policy2d_float64):
    arr = np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]])
    va = vn.make_verified(arr, policy=policy2d_float64).value
    # Return 1D vector (wrong ndim)
    out = va.apply_and_verify(lambda a: a.ravel())
    assert out.is_err()
    assert "expected 2d, got 1d" in str(out.error).lower()

def test_apply_and_verify_raises_is_caught(policy2d_float64):
    arr = np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]])
    va = vn.make_verified(arr, policy=policy2d_float64).value

    def bad(_):
        raise RuntimeError("boom")
    res = va.apply_and_verify(bad)
    assert res.is_err()
    assert "boom" in str(res.unwrap_err()).lower()
