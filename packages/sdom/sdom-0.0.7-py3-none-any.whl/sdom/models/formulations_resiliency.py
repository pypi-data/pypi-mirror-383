from pyomo.core import Var, Constraint
from pyomo.environ import Param, NonNegativeReals
from ..constants import CRITICAL_LOAD_PERCENTAGE, PCLS_TARGET

####################################################################################|
# ----------------------------------- Parameters -----------------------------------|
####################################################################################|
def add_resiliency_parameters(model, data):
    model.EUE_max = Param( initialize = float(data["scalars"].loc["EUE_max"].Value), mutable=True )  # Maximum EUE (in MWh) - Maximum unserved Energy


####################################################################################|
# ------------------------------------ Variables -----------------------------------|
####################################################################################|

def add_resiliency_variables( model ):
    # Define variables related to system resiliency
    model.LoadShed = Var( model.h, domain=NonNegativeReals, initialize = 0 )

####################################################################################|
# ----------------------------------- Constraints ----------------------------------|
####################################################################################|
def pcls_constraint_rule( model ):
    
    return sum( model.demand.ts_parameter[h] - model.LoadShed[h] for h in model.h ) \
        >= PCLS_TARGET * sum( model.demand.ts_parameter[h] for h in model.h ) * CRITICAL_LOAD_PERCENTAGE

# EUE - Expected Unserved Energy - Constraint : Resilience
def max_eue_constraint_rule( model ):
    return sum( model.LoadShed[h] for h in model.h ) <= model.EUE_max

def add_resiliency_constraints( model ):
    """
    Add resiliency-related constraints to the model.
    
    Parameters:
    model: The optimization model to which resiliency constraints will be added.
    
    Returns:
    None
    """
    model.PCLS_Constraint = Constraint( rule = pcls_constraint_rule )
    model.MaxEUE_Constraint = Constraint( rule = max_eue_constraint_rule )