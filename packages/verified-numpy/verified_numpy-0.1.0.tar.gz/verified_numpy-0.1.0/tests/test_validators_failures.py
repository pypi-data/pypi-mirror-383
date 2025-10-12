import numpy as np
import pytest
import verified_numpy as vn

@pytest.fixture
def policy_all():
    return vn.combine((
        vn.v_dtype(np.float64),
        vn.v_ndim(2),
        vn.v_finite,
        vn.v_nonempty,
        vn.v_row_major_contiguous,
    ))

@pytest.mark.parametrize(
    "arr,expect_message",
    [
        (np.array([[1, 2]], dtype=np.int32), "dtype"),              # wrong dtype
        (np.array([1.0, 2.0], dtype=np.float64), "expected 2d, got 1d"),           # wrong ndim
        (np.array([[]], dtype=np.float64), "empty"),             # empty
        (np.array([[np.nan, 1.0]]), "finite"),                      # NaN
        (np.array([[np.inf, 1.0]]), "finite"),                      # Inf
        (np.asfortranarray([[1.0, 2.0], [3.0, 4.0]]), "contiguous") # not C-contiguous
    ]
)
def test_make_verified_errors(policy_all, arr, expect_message):
    res = vn.make_verified(arr, policy=policy_all)
    assert res.is_err()
    # If your errors expose .error or .message, assert on that. Keep fuzzy:
    assert expect_message.lower() in str(res.unwrap_err()).lower()
