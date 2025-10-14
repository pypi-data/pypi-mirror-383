from typing import Dict, Hashable, Union, List, Literal, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import root_scalar
from EqUMP.base import create_prob_df, trf
from EqUMP.base.irf import ItemParamsCollection, ItemModelType

def tse_bound(
    params: ItemParamsCollection,
) -> Tuple[float, float]:
    lower = sum(float(v["c"]) for v in params.values() if "c" in v)
    upper = sum(np.atleast_1d(v["b"]).size for v in params.values())
    
    output = lower, upper
    return output

def tse_loss(
    ts: float,
    params: ItemParamsCollection,
    model: Dict[Hashable, ItemModelType],
    theta: float = 0.0,
    D: float = 1.702
) -> float: 
    keys = list(params.keys())
    params = [params[k] for k in keys]
    model = [model[k] for k in keys]
    df = create_prob_df(theta=theta, items=params, model=model, D=D)
    T = float(trf(df))
    
    loss = ts - T
    return loss

def tse(
    ts: float,
    params_new: ItemParamsCollection,
    params_old: ItemParamsCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
    model_new: Dict[Hashable, ItemModelType],
    model_old: Dict[Hashable, ItemModelType],
    theta: float = 0.0,
    D: float = 1.702, 
    anchor: Literal["internal", "external"] = "internal"
) -> Tuple[float, float]:
    """
    Performs true score equating of the new test form to the old test form under a common-item nonequivalent groups (CINEG) / nonequivalent groups with anchor test (NEAT) design. 
    Calculate the latent trait level and the true score on the old test form that corresponds to a given score on the new form, using the linking results.

    Parameters
    ----------
    ts: float
        test score on the new test form
    params_new: ItemParamsCollection
        item parameters of the new test form
    params_old: ItemParamsCollection
        item parameters of the old test form
    common_new: List[Hashable]
        common items in the new test form
    common_old: List[Hashable]
        common items in the old test form
    model_new: Dict[Hashable, ItemModelType]
        model of the new test form
    model_old: Dict[Hashable, ItemModelType]
        model of the old test form
    theta: float, optional
        initial value of theta
    D: float, optional
        scaling constant
    anchor: Literal["internal", "external"], optional
        anchor type

    Returns
    -------
    theta_updated: float
        updated theta value
    T_old: float
        true score on the old test form

    Examples
    --------
    >>> # Define item parameters for a multi-item test (new form)
    >>> params_new = {
    ...     0: {"a": 1.2, "b": -0.5},
    ...     1: {"a": 1.0, "b": 0.0},
    ...     2: {"a": 1.5, "b": 0.8},
    ...     3: {"a": 0.9, "b": -1.2}
    ... }
    >>> # Define item parameters for old form
    >>> params_old = {
    ...     0: {"a": 1.15, "b": -0.47},
    ...     1: {"a": 0.95, "b": 0.05},
    ...     2: {"a": 1.45, "b": 0.85},
    ...     3: {"a": 0.85, "b": -1.15}
    ... }
    >>> # Common items are items 0, 1, 2 (indices in both forms)
    >>> common_new = [0, 1, 2]
    >>> common_old = [0, 1, 2]
    >>> # Define item models
    >>> model_new = {0: "2PL", 1: "2PL", 2: "2PL", 3: "2PL"}
    >>> model_old = {0: "2PL", 1: "2PL", 2: "2PL", 3: "2PL"}
    >>> # Equate a test score of 2.5 on the new form
    >>> ts = 2.5
    >>> theta_eq, score_old = tse(ts, params_new, params_old, common_new, common_old, 
    ...                            model_new, model_old, theta=0.0, D=1.702, anchor="internal")
    >>> # Returns: (theta_estimate, equivalent_score_on_old_form)
    """
    
    if anchor == "external":
        params_new = {k: v for k, v in params_new.items() if k not in common_new}
        params_old = {k: v for k, v in params_old.items() if k not in common_old}
        model_new = {k: v for k, v in model_new.items()  if k not in common_new}
        model_old = {k: v for k, v in model_old.items()  if k not in common_old}

    def obj(v: float) -> float:
        return tse_loss(
            ts=ts,
            theta=v,
            params=params_new,
            model=model_new,
            D=D
        )
    
    res = root_scalar(obj, bracket=[-10.0, 10.0], method='brentq', xtol=1e-7)
    theta_updated = float(res.root)
    
    # Convert params_old dict to list for create_prob_df
    keys_old = list(params_old.keys())
    params_old_list = [params_old[k] for k in keys_old]
    model_old_list = [model_old[k] for k in keys_old]
    
    df_old = create_prob_df(
        theta=theta_updated,
        items=params_old_list,
        model=model_old_list,
        D=D
        )
    T_old = float(trf(df_old))
    
    output = theta_updated, T_old
    return output
