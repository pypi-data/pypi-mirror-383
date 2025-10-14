import numpy as np
from typing import Dict, Hashable, Union, List, Tuple
from EqUMP.base.irf import ItemParamsCollection

def mean_mean(
    params_new: ItemParamsCollection,
    params_old: ItemParamsCollection,
    common_new: List[Hashable],
    common_old: List[Hashable],
) -> Tuple[float, float]:
    """
    Transform the IRT scale in common-item nonequivalent groups (CINEG) / nonequivalent groups with anchor test (NEAT) design.
    Estimate scale linking coefficients using parameters of the common items.
    The Mean–Mean (MM) method uses the mean of common-item discrimination and difficulty parameters.

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
    ----------
    Loyd, B. H., & Hoover, H. D. (1980). Vertical equating using the Rasch model. Journal of Educational Measurement, 17(3), 179–193. https://doi.org/10.1111/j.1745-3984.1980.tb00825.x
    """
    # extract a and b parameters for common items
    a_new = np.array([params_new[item]["a"] for item in common_new])
    a_old = np.array([params_old[item]["a"] for item in common_old])

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
    mean_a_new = float(np.mean(a_new))
    mean_a_old = float(np.mean(a_old))
    mean_b_new = float(np.mean(b_new))
    mean_b_old = float(np.mean(b_old))

    A = mean_a_new / mean_a_old
    B = mean_b_old - A * mean_b_new

    # output
    output = A, B
    return output


if __name__ == "__main__":
    from EqUMP.tests.linking.helper import load_KIM_dichotomous_data
    KIM_dic_param_new, KIM_dic_param_old = load_KIM_dichotomous_data()

    res2 = mean_mean(
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

    res3 = mean_mean(
        params_new=KIM_poly_param_new,
        params_old=KIM_poly_param_old,
        common_new=[2, 5, 8, 11, 14, 17, 20],
        common_old=[2, 5, 8, 11, 14, 17, 20]
    )
    print(res3)  # Symmetry
