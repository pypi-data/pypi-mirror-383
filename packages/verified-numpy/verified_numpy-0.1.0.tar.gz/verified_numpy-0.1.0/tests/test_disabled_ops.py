import numpy as np
import pytest
import verified_numpy as vn

def _va():
    p = vn.combine((vn.v_dtype(np.float64), vn.v_ndim(2), vn.v_finite, vn.v_row_major_contiguous))
    return vn.make_verified(np.ascontiguousarray([[1.0, 2.0], [3.0, 4.0]]), policy=p).value

@pytest.mark.parametrize("op", [
    lambda v: v - 1,
    lambda v: 1 - v,
    lambda v: v / 2,
    lambda v: 2 / v,
    lambda v: v // 2,
    lambda v: 2 // v,
    lambda v: v ** 2,
    lambda v: 2 ** v,
    lambda v: v @ np.eye(2),
])
def test_all_disabled_ops(op):
    with pytest.raises(TypeError):
        _ = op(_va())
