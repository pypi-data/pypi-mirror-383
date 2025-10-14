import numpy as np
import pandas as pd
import pytest

from EqUMP.linking import haebara, transform_item_params
from EqUMP.tests.rbridge import run_rscript


def _within_tolerances(est, ref, abs_tol=1e-3, rel_tol=1e-3):
    A_e, B_e = est
    A_r, B_r = ref
    abs_ok = max(abs(A_e - A_r), abs(B_e - B_r)) <= abs_tol
    rel_ok = max(
        abs(A_e - A_r) / max(1.0, abs(A_r)),
        abs(B_e - B_r) / max(1.0, abs(B_r)),
    ) <= rel_tol
    return abs_ok and rel_ok


def _loss_at(A, B, params_new, params_old, common_new, common_old, model_new, model_old, D=1.702):
    """
    Todo
    ----
    - (25.09.10) This function is redundant, see linking.HB.Haebara
    """
    # replicate gauss-hermite used by default in haebara
    from EqUMP.base import gauss_hermite_quadrature
    from EqUMP.linking.HB.Haebara import haebara_loss
    nodes, weights = gauss_hermite_quadrature(nq=None)
    return haebara_loss(
        params_new=params_new,
        params_old=params_old,
        common_new=common_new,
        common_old=common_old,
        model_new=model_new,
        model_old=model_old,
        D=D,
        A=A,
        B=B,
        nodes_new=nodes,
        weights_new=weights,
        nodes_old=nodes,
        weights_old=weights,
        symmetry=True,
    )

@pytest.mark.skip(reason="Temporarily disabled while debugging")
def test_hb_oracle_3pl_multistart_stability():
    # Old-form 3PL items (small set for speed)
    params_old = {
        "i1": {"a": 0.9, "b": -1.0, "c": 0.20},
        "i2": {"a": 1.2, "b": 0.0, "c": 0.15},
        "i3": {"a": 1.5, "b": 1.0, "c": 0.25},
        "i4": {"a": 0.7, "b": 0.5, "c": 0.10},
    }
    model_map = {k: "3PL" for k in params_old.keys()}
    common_old = list(params_old.keys())
    common_new = list(params_old.keys())  # aligned

    # Oracle transform to create new form
    A_true, B_true = 1.25, -0.30
    params_new = transform_item_params(
        params=params_old,
        A=A_true,
        B=B_true,
        direction="to_new",
    )

    # Multi-start initializations (keep small for CI performance)
    starts = [
        (1.0, 0.0),
        (0.7, -0.5),
        (1.6, 0.5),
        (1.3, -0.2),
        (0.9, 0.3),
    ]

    estimates = []
    losses = []
    for A0, B0 in starts:
        A_hat, B_hat = haebara(
            params_new=params_new,
            params_old=params_old,
            common_new=common_new,
            common_old=common_old,
            model_new=model_map,
            model_old=model_map,
            D=1.702,
            A0=A0,
            B0=B0,
        )
        estimates.append((A_hat, B_hat))
        losses.append(
            _loss_at(A_hat, B_hat, params_new, params_old, common_new, common_old, model_map, model_map, D=1.702)
        )

    # Reference: pick solution with minimum loss
    ref_idx = int(np.argmin(np.asarray(losses)))
    A_ref, B_ref = estimates[ref_idx]
    loss_ref = losses[ref_idx]

    # All estimates should merge within tight tolerances and have similar loss
    for (A_e, B_e), loss_e in zip(estimates, losses):
        assert _within_tolerances((A_e, B_e), (A_ref, B_ref), 1e-3, 1e-3)
        assert abs(loss_e - loss_ref) <= 1e-8

    # Also ensure recovery is close to oracle A_true, B_true
    assert _within_tolerances((A_ref, B_ref), (A_true, B_true), 5e-3, 5e-3)

@pytest.mark.skip(reason="Temporarily disabled while debugging")
def test_hb_oracle_mixed_multistart_stability():
    # Old-form mixed 3PL + GPCM
    params_old = {
        # 3PL
        "d1": {"a": 1.1, "b": -1.2, "c": 0.18},
        "d2": {"a": 0.8, "b": 0.4, "c": 0.22},
        # GPCM (no c)
        "p1": {"a": 0.9, "b": np.array([-1.0, 0.0])},
        "p2": {"a": 1.3, "b": np.array([-0.5, 0.7, 1.4])},
    }
    model_map = {
        "d1": "3PL",
        "d2": "3PL",
        "p1": "GPCM",
        "p2": "GPCM",
    }
    common_old = list(params_old.keys())
    common_new = list(params_old.keys())  # aligned

    # Oracle transform
    A_true, B_true = 0.85, 0.40
    params_new = transform_item_params(
        params=params_old,
        A=A_true,
        B=B_true,
        direction="to_new",
    )

    starts = [
        (1.0, 0.0),
        (0.6, -0.8),
        (1.4, 0.8),
        (0.9, 0.2),
    ]

    estimates = []
    losses = []
    for A0, B0 in starts:
        A_hat, B_hat = haebara(
            params_new=params_new,
            params_old=params_old,
            common_new=common_new,
            common_old=common_old,
            model_new=model_map,
            model_old=model_map,
            D=1.702,
            A0=A0,
            B0=B0,
        )
        estimates.append((A_hat, B_hat))
        losses.append(
            _loss_at(A_hat, B_hat, params_new, params_old, common_new, common_old, model_map, model_map, D=1.702)
        )

    ref_idx = int(np.argmin(np.asarray(losses)))
    A_ref, B_ref = estimates[ref_idx]
    loss_ref = losses[ref_idx]

    for (A_e, B_e), loss_e in zip(estimates, losses):
        assert _within_tolerances((A_e, B_e), (A_ref, B_ref), 1e-3, 1e-3)
        assert abs(loss_e - loss_ref) <= 1e-8

    # Oracle proximity (mixed models may be a bit tougher; keep same tolerance for rigor)
    assert _within_tolerances((A_ref, B_ref), (A_true, B_true), 5e-3, 5e-3)

from pathlib import Path
class TestHB_R:
    @pytest.mark.rbridge
    def test_compare_SNSequate(self, tol=1e-5):
        """Compare Haebara linking constants to SNSequate results."""
        from EqUMP.tests.linking.helper import load_SNSequate_data
        SNS_param_x, SNS_param_y = load_SNSequate_data()
        SNS_param_new = SNS_param_x[["model", "a","b","c"]].to_dict(orient="index") # SNSequate에서 y가 구 검사형, X가 신 검사형에 주의
        SNS_param_old = SNS_param_y[["model", "a","b","c"]].to_dict(orient="index")
        
        res_python = haebara(
            items_new=SNS_param_new,
            items_old=SNS_param_old,
            common_new=[3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
            common_old=[3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
            D=1.7,
            quadrature="custom",
            custom_quadrature={
                "nodes_new": np.linspace(-4, 4, 161),
                "nodes_old": np.linspace(-4, 4, 161),
                "weights_new": np.full(161, 0.05),
                "weights_old": np.full(161, 0.05),
            },
            symmetry=False,
        )
        A_python = res_python[0]
        B_python = res_python[1]

        test_dir = Path(__file__).parent
        res_r = run_rscript(
            payload={}, rscript_path="../SNSequate.R", module_path=str(test_dir)
        )
        A_r = res_r["hb"]["A"]
        B_r = res_r["hb"]["B"]

        assert abs(A_python - A_r) < tol, (
            f"A constants differ: Python={A_python:.6f}, R={A_r:.6f}, "
            f"difference={abs(A_python - A_r):.6f}"
        )
        assert abs(B_python - B_r) < tol, (
            f"B constants differ: Python={B_python:.6f}, R={B_r:.6f}, "
            f"difference={abs(B_python - B_r):.6f}"
        )

        print(f"\nHaebara Comparison Results:")
        print(f"Python: A={A_python:.6f}, B={B_python:.6f}")
        print(f"R:      A={A_r:.6f}, B={B_r:.6f}")
        print(f"Differences: ΔA={abs(A_python - A_r):.6f}, ΔB={abs(B_python - B_r):.6f}")
        
    @pytest.mark.skip(reason="Temporarily disabled while debugging")
    def test_compare_KB(self):
        pass
