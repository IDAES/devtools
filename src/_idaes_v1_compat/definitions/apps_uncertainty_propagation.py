from pyomo.common.deprecation import deprecated
from idaes.apps.uncertainty_propagation.sens import sensitivity_calculation


@deprecated(
    """The kaug function has been deprecated.
            Use the sensitivity_calculation() function
            with method='kaug' to access this functionality.""",
    logger="pyomo.contrib.sensitivity_toolbox",
    version="TBD",
)
def kaug(
    instance,
    paramSubList,
    perturbList,
    cloneModel=True,
    tee=False,
    keepfiles=False,
    solver_options=None,
    streamSoln=False,
):
    m = sensitivity_calculation(
        "kaug",
        instance,
        paramSubList,
        perturbList,
        cloneModel,
        tee,
        keepfiles,
        solver_options,
    )

    return m


@deprecated(
    """The sipopt function has been deprecated. Use the
            sensitivity_calculation() function with method='sipopt'
            to access this functionality.""",
    logger="pyomo.contrib.sensitivity_toolbox",
    version="TBD",
)
def sipopt(
    instance,
    paramSubList,
    perturbList,
    cloneModel=True,
    tee=False,
    keepfiles=False,
    streamSoln=False,
):
    m = sensitivity_calculation(
        "sipopt",
        instance,
        paramSubList,
        perturbList,
        cloneModel,
        tee,
        keepfiles,
        solver_options=None,
    )

    return m

