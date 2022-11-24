# from _idaes_v1_compat import activate; activate()
# from _idaes_v1_compat import activate

from pyomo.environ import (
    ConcreteModel,
)
from idaes.core import FlowsheetBlock
from idaes.core.util import get_solver


m = ConcreteModel()
m.fs = FlowsheetBlock(default={"dynamic": False})
print(m)
