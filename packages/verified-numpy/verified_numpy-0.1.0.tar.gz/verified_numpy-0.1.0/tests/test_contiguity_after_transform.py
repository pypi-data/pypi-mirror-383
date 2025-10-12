import numpy as np
import verified_numpy as vn

def test_apply_and_verify_contiguity_enforced():
    policy = vn.combine((vn.v_dtype(np.float64), vn.v_ndim(2), vn.v_finite, vn.v_row_major_contiguous))
    va = vn.make_verified(np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]]), policy=policy).value

    # Make a Fortran-ordered view
    res = va.apply_and_verify(lambda a: np.asfortranarray(a))
    assert res.is_err()
    assert "contiguous" in str(res.error).lower()
