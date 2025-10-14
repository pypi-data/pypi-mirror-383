import numpy as np
from typing import Dict, Hashable, Union, List, Tuple
from EqUMP.base.irf import ItemParamsCollection


def mean_sigma(
    params_new: ItemParamsCollection,
    params_old: ItemParamsCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
) -> Tuple[float, float]:
    """
    Transform the IRT scale of the new test form to the old test form in common-item nonequivalent groups (CINEG) / nonequivalent groups with anchor test (NEAT) design.
    Estimate scale linking coefficients using parameters of the common items.
    The Mean–Sigma (MS) method uses the mean and standard deviation of common-item difficulty parameters.

    Parameters
    ----------
    params_new/old : Dict
        Item parameters for the new/old test form.
        - "a": discrimination parameter
        - "b":
            Dichotomous: difficulty parameter
            Polytomous: step difficulties parameter
        - "c": pseudo-guessing parameter
    common_new/old : List
        List of common item identifiers in the new/old test form.

    Returns
    -------
    Tuple[float, float]
        A : Slope of linear linkinking function
        B : Intercepts of linear linkinking function
    
    References
    -----
    Marco, G. L. (1977). Item characteristic curve solutions to three intractable testing problems 1. ETS Research Bulletin Series, 1977(1), i-41.
    """
    # extract b parameters for common items
    b_new = np.concatenate(
        [
            np.atleast_1d(np.asarray(params_new[item]["b"], dtype=float)).ravel()
            for item in common_new
        ]
    )
    b_old = np.concatenate(
        [
            np.atleast_1d(np.asarray(params_old[item]["b"], dtype=float)).ravel()
            for item in common_old
        ]
    )

    # compute A and B
    sigma_b_new = float(np.std(b_new, ddof=0))
    sigma_b_old = float(np.std(b_old, ddof=0))
    mean_b_new = float(np.mean(b_new))
    mean_b_old = float(np.mean(b_old))

    A = sigma_b_old / sigma_b_new
    B = mean_b_old - A * mean_b_new

    output = A, B

    return output

if __name__ == "__main__":
    from EqUMP.tests.linking.helper import load_KIM_dichotomous_data
    KIM_dic_param_new, KIM_dic_param_old = load_KIM_dichotomous_data()
    res2 = mean_sigma(
        params_new=KIM_dic_param_new,
        params_old=KIM_dic_param_old,
        common_new=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        common_old=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    )
    print(res2)

    
    from EqUMP.tests.linking.helper import load_KIM_polytomous_data
    KIM_poly_param_new, KIM_poly_param_old = load_KIM_polytomous_data()
    model_map = {
        **{i: "3PL" for i in range(1, 16)},
        **{i: "GPCM" for i in range(16, 22)},
    }

    res3 = mean_sigma(
        params_new=KIM_poly_param_new,
        params_old=KIM_poly_param_old,
        common_new=[2, 5, 8, 11, 14, 17, 20],
        common_old=[2, 5, 8, 11, 14, 17, 20]
    )
    print(res3)  # Symmetry