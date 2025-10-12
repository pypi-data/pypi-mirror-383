import numpy as np
import verified_numpy as vn

def _policy():
    return vn.combine((vn.v_dtype(np.float64), vn.v_ndim(2), vn.v_finite, vn.v_row_major_contiguous))

def test_numpy_add_two_verifiedarrays_returns_ndarray():
    base = np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]])
    va1 = vn.make_verified(base, policy=_policy()).value
    va2 = vn.make_verified(base, policy=_policy()).value
    out = np.add(va1, va2)  # triggers __array_ufunc__
    assert isinstance(out, np.ndarray)
    assert np.all(out == base + base)
