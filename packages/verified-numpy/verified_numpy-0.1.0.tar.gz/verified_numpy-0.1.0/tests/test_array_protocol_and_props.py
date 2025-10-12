import numpy as np
import verified_numpy as vn

def test_numpy_ufunc_and_props_roundtrip():
    policy = vn.combine((vn.v_dtype(np.float64), vn.v_ndim(2), vn.v_finite, vn.v_row_major_contiguous))
    base = np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]])
    res = vn.make_verified(base, policy=policy)
    assert res.is_ok(), res.error
    va = res.value

    # __array__ integration:
    assert np.sum(va) == np.sum(base)
    # Properties:
    assert va.ndim == 2
    assert va.dtype == np.float64
    assert va.shape == (2, 2)

    # __repr__/__str__ usually include class name / shape / dtype
    s = repr(va)
    assert "Verified" in s or "verified" in s
