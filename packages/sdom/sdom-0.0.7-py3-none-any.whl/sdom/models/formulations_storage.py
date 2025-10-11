from pyomo.core import Var, Constraint, Expression
from pyomo.environ import Set, Param, Binary, NonNegativeReals, sqrt
from ..constants import STORAGE_PROPERTIES_NAMES, MW_TO_KW
from .models_utils import crf_rule

def initialize_storage_sets(block, data: dict):
    block.j = Set( initialize = data['STORAGE_SET_J_TECHS'] )
    block.b = Set( within=block.j, initialize = data['STORAGE_SET_B_TECHS'] )
    
    # Initialize storage properties
    block.properties_set = Set( initialize = STORAGE_PROPERTIES_NAMES )
####################################################################################|
# ----------------------------------- Parameters -----------------------------------|
####################################################################################|

def add_storage_parameters(model, data: dict):
    # Battery life and cycling
    max_cycles_dict = data['storage_data'].loc['MaxCycles'].to_dict()

    model.storage.MaxCycles = Param( model.storage.j,  initialize = max_cycles_dict )
    # Storage data initialization
    storage_dict = data["storage_data"].stack().to_dict()
    storage_tuple_dict = {(prop, tech): storage_dict[(prop, tech)] for prop in STORAGE_PROPERTIES_NAMES for tech in model.storage.j}
    model.storage.data = Param( model.storage.properties_set, model.storage.j, initialize = storage_tuple_dict )

    model.storage.r = Param( initialize = float(data["scalars"].loc["r"].Value) )  # Interest rate
    model.storage.CRF = Param( model.storage.j, initialize = crf_rule ) #Capital Recovery Factor -STORAGE

####################################################################################|
# ------------------------------------ Variables -----------------------------------|
####################################################################################|
def add_storage_variables(model):
    # Charging power for storage technology j in hour h
    model.storage.PC = Var(model.h, model.storage.j, domain=NonNegativeReals, initialize=0)
    # Discharging power for storage technology j in hour h
    model.storage.PD = Var(model.h, model.storage.j, domain=NonNegativeReals, initialize=0)
    # State-of-charge for storage technology j in hour h
    model.storage.SOC = Var(model.h, model.storage.j, domain=NonNegativeReals, initialize=0)
    # Charging capacity for storage technology j
    model.storage.Pcha = Var(model.storage.j, domain=NonNegativeReals, initialize=0)
    # Discharging capacity for storage technology j
    model.storage.Pdis = Var(model.storage.j, domain=NonNegativeReals, initialize=0)
    # Energy capacity for storage technology j
    model.storage.Ecap = Var(model.storage.j, domain=NonNegativeReals, initialize=0)

    model.storage.capacity_fraction = Var(model.storage.j, model.h, domain=Binary, initialize=0)


####################################################################################|
# ----------------------------------- Expressions ----------------------------------|
####################################################################################|

def storage_power_capex_cost_expr_rule(block, j):
     return (   block.CRF[j] * (
                    MW_TO_KW * block.data['CostRatio', j] * block.data['P_Capex', j]*block.Pcha[j]
                    + MW_TO_KW * (1 - block.data['CostRatio', j]) * block.data['P_Capex', j]*block.Pdis[j]
                    )
                )

def storage_energy_capex_cost_expr_rule(block, j):
     return ( block.CRF[j] * ( MW_TO_KW *block.data['E_Capex', j]*block.Ecap[j] ) )

def storage_fixed_om_cost_expr_rule(block, j):
     return (    MW_TO_KW * block.data['CostRatio', j] * block.data['FOM', j]*block.Pcha[j]
                + MW_TO_KW * (1 - block.data['CostRatio', j]) * block.data['FOM', j]*block.Pdis[j]
                )

def _add_storage_expressions(block):
    block.power_capex_cost_expr = Expression(block.j, rule = storage_power_capex_cost_expr_rule )
    block.energy_capex_cost_expr = Expression(block.j, rule = storage_energy_capex_cost_expr_rule )
    block.capex_cost_expr = Expression(block.j,  rule = lambda m,j: m.power_capex_cost_expr[j] + m.energy_capex_cost_expr[j] )

    block.fixed_om_cost_expr = Expression(block.j,  rule = storage_fixed_om_cost_expr_rule )

    block.total_capex_cost = Expression( rule = sum( block.capex_cost_expr[j] for j in block.j ) )
    block.total_fixed_om_cost = Expression( rule = sum( block.fixed_om_cost_expr[j] for j in block.j ) )


def add_storage_expressions(model):
    _add_storage_expressions(model.storage)
     


####################################################################################|
# ----------------------------------- Add_costs -----------------------------------|
####################################################################################|
def add_storage_fixed_costs(model):
    """
    Add cost-related variables for storage technologies to the model.
    
    Parameters:
    model: The optimization model to which storage cost variables will be added.
    
    Returns:
    Costs sum for storage technologies, including capital and fixed O&M costs.
    """
    return ( # Storage Capex and Fixed O&M
            model.storage.total_capex_cost  + model.storage.total_fixed_om_cost 
            )

def add_storage_variable_costs(model):
    """
    Add variable costs for storage technologies to the model.
    
    Parameters:
    model: The optimization model to which storage variable costs will be added.
    
    Returns:
    Variable costs sum for storage technologies, including variable O&M costs.
    """
    return (
        sum( model.storage.data['VOM', j] * sum(model.storage.PD[h, j]
                  for h in model.h) for j in model.storage.j )
    )

####################################################################################|
# ----------------------------------- Constraints ----------------------------------|
####################################################################################|

# State-Of-Charge Balance -
def soc_balance_rule(model, h, j):
    if h > 1: 
        return model.storage.SOC[h, j] == model.storage.SOC[h-1, j] \
            + sqrt(model.storage.data['Eff', j]) * model.storage.PC[h, j] \
            - model.storage.PD[h, j] / sqrt(model.storage.data['Eff', j])
    else:
        # cyclical or initial condition
        return model.storage.SOC[h, j] == model.storage.SOC[max(model.h), j] \
            + sqrt(model.storage.data['Eff', j]) * model.storage.PC[h, j] \
            - model.storage.PD[h, j] / sqrt(model.storage.data['Eff', j])

# Max cycle year
def max_cycle_year_rule(model, j): #TODO check here this hardcoded Li-Ion
    n_steps = model.n_steps_modeled
    iterate = range(1, n_steps + 1)
    return sum(model.PD[h, j] for h in iterate) <= (model.MaxCycles[j] / model.data['Lifetime', j]) * model.Ecap[j]

def add_storage_constraints( model ):
    """
    Add storage-related constraints to the model.
    
    Parameters:
    model: The optimization model to which storage constraints will be added.
    
    Returns:
    None
    """
    # Ensure that the charging and discharging power do not exceed storage limits
    model.storage.ChargSt= Constraint(model.h, model.storage.j, rule=lambda m, h, j: m.PC[h, j] <= m.data['Max_P', j] * m.capacity_fraction[j, h])
    model.storage.DischargeSt = Constraint(model.h, model.storage.j, rule=lambda m, h, j: m.PD[h, j] <= m.data['Max_P', j] * (1 - m.capacity_fraction[j, h]))

    # Hourly capacity bounds
    model.storage.MaxHourlyCharging = Constraint(model.h, model.storage.j, rule= lambda m,h,j: m.PC[h, j] <= m.Pcha[j])
    model.storage.MaxHourlyDischarging = Constraint(model.h, model.storage.j, rule= lambda m,h,j: m.PD[h, j] <= m.Pdis[j])

    # Limit state of charge of storage by its capacity
    model.storage.MaxSOC = Constraint(model.h, model.storage.j, rule=lambda m, h, j: m.SOC[h,j]<= m.Ecap[j])
    # SOC Balance Constraint
    model.SOCBalance = Constraint(model.h, model.storage.j, rule=soc_balance_rule)

    # - Constraints on the maximum charging (Pcha) and discharging (Pdis) power for each technology
    model.storage.MaxPcha = Constraint( model.storage.j, rule=lambda m, j: m.Pcha[j] <= m.data['Max_P', j] )
    model.storage.MaxPdis = Constraint( model.storage.j, rule=lambda m, j: m.Pdis[j] <= m.data['Max_P', j] )

    # Charge and discharge rates are equal -
    model.storage.PchaPdis = Constraint( model.storage.b, rule=lambda m, j: m.Pcha[j] == m.Pdis[j] )

    # Max and min energy capacity constraints (handle uninitialized variables)
    model.storage.MinEcap = Constraint(model.storage.j, rule= lambda m,j: m.Ecap[j] >= m.data['Min_Duration', j] * m.Pdis[j] / sqrt(m.data['Eff', j]))
    model.storage.MaxEcap = Constraint(model.storage.j, rule= lambda m,j: m.Ecap[j] <= m.data['Max_Duration', j] * m.Pdis[j] / sqrt(m.data['Eff', j]))


    model.storage.MaxCycleYear_constraint = Constraint( model.storage.j, rule=max_cycle_year_rule)