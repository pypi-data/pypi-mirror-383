from typing import Dict, Hashable, Union, List, Literal, Tuple, Optional
import numpy as np
from scipy.optimize import minimize
from EqUMP.base import IRF, gauss_hermite_quadrature, fixed_point_quadrature, ItemParamsCollection
from EqUMP.base.irf import ItemModelType
from EqUMP.linking.helper import transform_item_params, validate_and_prepare_custom_quadrature

def haebara_loss(
    params_new: ItemParamsCollection,
    params_old: ItemParamsCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
    model_new: Dict[Hashable, ItemModelType],
    model_old: Dict[Hashable, ItemModelType],
    D: float = 1.702,
    A: float = 1.0,
    B: float = 0.0,
    nodes_new: Optional[np.ndarray] = None,
    weights_new: Optional[np.ndarray] = None,
    nodes_old: Optional[np.ndarray] = None,
    weights_old: Optional[np.ndarray] = None,
    symmetry: bool = True,
) -> float:

    # new -> old
    params_new_t = transform_item_params(
        params_new, A, B, direction="to_old"
    )

    # Pre-create IRF objects for common items (new transformed and old)
    irf_new_t = {c_new: IRF(params=params_new_t[c_new], model=model_new[c_new], D=D) 
                 for c_new in common_new}
    irf_old = {c_old: IRF(params=params_old[c_old], model=model_old[c_old], D=D) 
               for c_old in common_old}

    diff1 = 0.0
    for x, w in zip(nodes_old, weights_old):
        x = float(x); w = float(w)
        for c_new, c_old in zip(common_new, common_old):
            P_new_t = irf_new_t[c_new].prob(x)
            P_old = irf_old[c_old].prob(x)
            d = (P_old - P_new_t).to_numpy(dtype=float).ravel()
            diff1 += float(d @ d) * w
    
    M1 = 0.0
    for c_old in common_old:
        M = 1 + np.asarray(params_old[c_old]["b"], dtype=float).size # item category k = 0, ... m -> the number of category: 1 + m
        M1 += M
    S1 = M1 * float(np.sum(weights_old))
    
    loss1 = diff1 / S1
    
    # old -> new
    params_old_t = transform_item_params(
        params_old, A, B, direction="to_new"
    )

    # Pre-create IRF objects for common items (new and old transformed)
    irf_new = {c_new: IRF(params=params_new[c_new], model=model_new[c_new], D=D) 
               for c_new in common_new}
    irf_old_t = {c_old: IRF(params=params_old_t[c_old], model=model_old[c_old], D=D) 
                 for c_old in common_old}

    diff2 = 0.0
    for x, w in zip(nodes_new, weights_new):
        x = float(x); w = float(w)
        for c_new, c_old in zip(common_new, common_old):
            P_new = irf_new[c_new].prob(x)
            P_old_t = irf_old_t[c_old].prob(x)
            d = (P_new - P_old_t).to_numpy(dtype=float).ravel()
            diff2 += float(d @ d) * w

    M2 = 0.0
    for c_new in common_new:
        M = 1 + np.asarray(params_new[c_new]["b"], dtype=float).size # item category k = 0, ... m -> the number of category: 1 + m
        M2 += M
    S2 = M2 * float(np.sum(weights_new))
    
    loss2 = diff2 / S2

    if symmetry == True:
        output = float(loss1 + loss2)
    elif symmetry == False:
        output = float(loss1)

    return output


def haebara(
    items_new: ItemParamsCollection,
    items_old: ItemParamsCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
    D: float = 1.702,
    A0: float = 1.0,
    B0: float = 0.0,
    quadrature: Literal["gauss_hermite", "fixed_point", "custom"] = "gauss_hermite",
    nq: Optional[int] = 30,
    theta_range: Tuple[float, float] = (-4.0, 4.0),
    custom_quadrature: Optional[Dict[str, Union[np.ndarray, List[float]]]] = None,
    symmetry: bool = True,
) -> Tuple[float, float]:
    """
    Transform the IRT scale of the new test form to the old test form in common-item nonequivalent groups (CINEG) / nonequivalent groups with anchor test (NEAT) design. 
    Estimate scale linking coefficients using parameters of the common items.
    The Haebara method uses the item response function of common-item.
    
    Parameters
    ----------
    items_new/old : Dict
        Item parameters for the new/old test form.
        - "a": discrimination parameter
        - "b": 
            Dichotomous: difficulty parameter
            Polytomous: step difficulties parameter
        - "c": pseudo-guessing parameter
    common_new/old : List
        List of common item identifiers in the new/old test form.
    D : float, optional
        Scaling constant (default 1.702).
    A0 : float, optional
        Initial value of scaling coefficient (A) (default 1.0).
    B0 : float, optional
        Initial value of scaling coefficient (B) (default 0.0).
    quadrature : str, optional
        Method for numerical integration.
        One of {"gauss_hermite", "fixed_point", "custom"} (default "gauss_hermite").
    nq: int, optional
        Number of quadrature nodes (default 30). 
        Used if quadrature="gauss_hermite" or "fixed_point".
    theta_range: Tuple of float, optional
        Lower and upper bounds of the latent trait (default -4 to 4).
        Used if quadrature="fixed_point".
    custom_quadrature: Dict, optional
        Custom quadrature specification used if quadrature="custom".
        Expected keys: {
            "nodes_new", "weights_new", "nodes_old", "weights_old"
        }. Values may be sequences or numpy arrays. All arrays must be 1D, same length within each form, weights non-negative, and contain no NaNs/Inf.
    symmetry: bool, optional
        If True, the loss function considers both direction (new → old and old → new). 
        If False, the loss function considers only new → old.
    
    Returns
    -------
    Tuple[float, float]
        A : Slope of linear linkinking function
        B : Intercepts of linear linkinking function
    
    References
    ----------
    Haebara, T. (1980). Equating Logistic Ability Scales by a Weighted Least Squares Method. Japanese Psychological Research, 22(3), 144-149. https://doi.org/10.4992/psycholres1954.22.144 

    Examples
    --------
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
    """
    if quadrature == "gauss_hermite":
        if nq is None:
            nq = 30
        nodes, weights = gauss_hermite_quadrature(nq=nq)
        nodes_new = nodes_old = nodes
        weights_new = weights_old = weights

    elif quadrature == "fixed_point":
        if nq is None:
            nq = 40
        nodes, weights = fixed_point_quadrature(nq=nq, theta_range=theta_range)
        nodes_new = nodes_old = nodes
        weights_new = weights_old = weights

    elif quadrature == "custom":
        if custom_quadrature is None:
            raise ValueError("custom_quadrature must be provided when quadrature='custom'.")
        nodes_new, weights_new, nodes_old, weights_old = validate_and_prepare_custom_quadrature(custom_quadrature)
    else:
        raise ValueError("quadrature must be one of {'gauss_hermite', 'fixed_point', 'custom' }.")
    
    from EqUMP.linking.helper import adjust_item_input
    model_new, params_new = adjust_item_input(items_new)
    model_old, params_old = adjust_item_input(items_old)
    
    def obj(v: Tuple[float, float]) -> float:
        return haebara_loss(
            params_new=params_new,
            params_old=params_old,
            common_new=common_new,
            common_old=common_old,
            model_new=model_new,
            model_old=model_old,
            D=D,
            A=float(v[0]),
            B=float(v[1]),
            nodes_new=nodes_new,
            weights_new=weights_new,
            nodes_old=nodes_old,
            weights_old=weights_old,
            symmetry=symmetry,
        )

    res = minimize(obj, x0=([A0, B0]), method="BFGS",
                   options = {
                       "gtol": 1e-6,
                       "maxiter": 1000,
                       "eps": 1e-8  
                   })

    # output
    A, B = float(res.x[0]), float(res.x[1])
    output = A, B
    return output

if __name__ == "__main__":
    from EqUMP.tests.linking.helper import load_KIM_dichotomous_data
    KIM_dic_param_new, KIM_dic_param_old = load_KIM_dichotomous_data()

    res2 = haebara(
        params_new=KIM_dic_param_new,
        params_old=KIM_dic_param_old,
        common_new=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        common_old=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        model_new={k: "3PL" for k in KIM_dic_param_new.keys()},
        model_old={k: "3PL" for k in KIM_dic_param_old.keys()},
        D=1.7,
        quadrature="fixed_point",
        nq=31,
        symmetry=True,
    )
    print(res2)
    
    res3 = haebara(
        params_new=KIM_dic_param_new,
        params_old=KIM_dic_param_old,
        common_new=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        common_old=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        model_new={k: "3PL" for k in KIM_dic_param_new.keys()},
        model_old={k: "3PL" for k in KIM_dic_param_old.keys()},
        D=1.7,
        quadrature="fixed_point",
        nq=31,
        symmetry=False,
    )   
    print(res3)

    
    from EqUMP.tests.linking.helper import load_KIM_polytomous_data
    KIM_poly_param_new, KIM_poly_param_old = load_KIM_polytomous_data()
    model_map = {
        **{i: "3PL" for i in range(1, 16)},
        **{i: "GPCM" for i in range(16, 22)},
    }

    res4 = haebara(
        params_new=KIM_poly_param_new,
        params_old=KIM_poly_param_old,
        common_new=[2, 5, 8, 11, 14, 17, 20],
        common_old=[2, 5, 8, 11, 14, 17, 20],
        model_new=model_map,
        model_old=model_map,
        D=1.7,
        quadrature="custom",
        custom_quadrature={
            "nodes_new": np.linspace(-4, 4, 25),
            "nodes_old": np.linspace(-4, 4, 25),
            "weights_new": [
                0.00005,
                0.00018,
                0.00058,
                0.00162,
                0.00407,
                0.00909,
                0.01802,
                0.03208,
                0.05242,
                0.07958,
                0.10850,
                0.12790,
                0.13530,
                0.12830,
                0.10380,
                0.07739,
                0.05391,
                0.03367,
                0.01853,
                0.00898,
                0.00384,
                0.00146,
                0.00049,
                0.00015,
                0.00004,
            ],
            "weights_old": [
                0.00005,
                0.00018,
                0.00058,
                0.00162,
                0.00400,
                0.00882,
                0.01755,
                0.03207,
                0.05363,
                0.08041,
                0.10810,
                0.13070,
                0.13850,
                0.12570,
                0.09952,
                0.07580,
                0.05455,
                0.03494,
                0.01900,
                0.00873,
                0.00355,
                0.00132,
                0.00045,
                0.00014,
                0.0004,
            ],
        },
        symmetry=True,
    )
    print(res4)  # Symmetry

    res5 = haebara(
        params_new=KIM_poly_param_new,
        params_old=KIM_poly_param_old,
        common_new=[2, 5, 8, 11, 14, 17, 20],
        common_old=[2, 5, 8, 11, 14, 17, 20],
        model_new=model_map,
        model_old=model_map,
        D=1.7,
        quadrature="custom",
        custom_quadrature={
            "nodes_new": np.linspace(-4, 4, 25),
            "nodes_old": np.linspace(-4, 4, 25),
            "weights_new": [
                0.00005,
                0.00018,
                0.00058,
                0.00162,
                0.00407,
                0.00909,
                0.01802,
                0.03208,
                0.05242,
                0.07958,
                0.10850,
                0.12790,
                0.13530,
                0.12830,
                0.10380,
                0.07739,
                0.05391,
                0.03367,
                0.01853,
                0.00898,
                0.00384,
                0.00146,
                0.00049,
                0.00015,
                0.00004,
            ],
            "weights_old": [
                0.00005,
                0.00018,
                0.00058,
                0.00162,
                0.00400,
                0.00882,
                0.01755,
                0.03207,
                0.05363,
                0.08041,
                0.10810,
                0.13070,
                0.13850,
                0.12570,
                0.09952,
                0.07580,
                0.05455,
                0.03494,
                0.01900,
                0.00873,
                0.00355,
                0.00132,
                0.00045,
                0.00014,
                0.0004,
            ],
        },
        symmetry=False,
    )
    print(res5)
