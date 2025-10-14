import numpy as np
import pandas as pd
import pytest

from EqUMP.linking import mean_mean
from EqUMP.tests.rbridge import run_rscript


def test_mm_output_structure_and_types():
    params_old = {"i": {"a": 1.0, "b": 0.0}}
    params_new = {"j": {"a": 2.0, "b": 1.0}}
    common_old = ["i"]
    common_new = ["j"]

    out = mean_mean(params_old, params_new, common_old, common_new)

    # Structure
    assert isinstance(out, tuple), f"out is {type(out)}"
    assert len(out) == 2

    # Types
    A, B = out
    assert isinstance(A, (float, np.floating))
    assert isinstance(B, (float, np.floating))


def test_mm_raises_on_missing_keys():
    # Missing 'a' or 'b' should raise KeyError from dict access
    params_old = {"i": {"b": 0.0}}
    params_new = {"j": {"a": 1.0, "b": 1.0}}
    with pytest.raises(KeyError):
        mean_mean(params_old, params_new, ["i"], ["j"])

from pathlib import Path
class TestMM_R:
    @pytest.mark.rbridge
    def test_compare_SNSequate(self, tol=1e-4):
        from EqUMP.tests.linking.helper import load_SNSequate_data
        SNS_param_x, SNS_param_y = load_SNSequate_data()
        SNS_param_new = SNS_param_x[["a","b","c"]].to_dict(orient="index") # SNSequate에서 y가 구 검사형, X가 신 검사형에 주의
        SNS_param_old = SNS_param_y[["a","b","c"]].to_dict(orient="index")
        
        res_python = mean_mean(
            params_new=SNS_param_new,
            params_old=SNS_param_old,
            common_new=[3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
            common_old=[3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
        )

        test_dir = Path(__file__).parent
        res_r = run_rscript(
            payload={}, rscript_path="../SNSequate.R", module_path=str(test_dir)
        )

        A_python = res_python[0]
        B_python = res_python[1]
        A_r = res_r["mm"]["A"]
        B_r = res_r["mm"]["B"]

        assert abs(A_python - A_r) < tol, (
            f"A constants differ: Python={A_python:.6f}, R={A_r:.6f}, "
            f"difference={abs(A_python - A_r):.6f}"
        )
        assert abs(B_python - B_r) < tol, (
            f"B constants differ: Python={B_python:.6f}, R={B_r:.6f}, "
            f"difference={abs(B_python - B_r):.6f}"
        )

        print(f"\nMean-mean Comparison Results:")
        print(f"Python: A={A_python:.6f}, B={B_python:.6f}")
        print(f"R:      A={A_r:.6f}, B={B_r:.6f}")
        print(f"Differences: ΔA={abs(A_python - A_r):.6f}, ΔB={abs(B_python - B_r):.6f}")
    
    @pytest.mark.skip(reason="Temporarily disabled while debugging")
    def test_compare_KB(self):
        pass