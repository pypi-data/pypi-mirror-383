from pyomo.core import Var, Constraint, Expression
from pyomo.environ import Set, Param, value, NonNegativeReals
import logging
from .models_utils import crf_rule, generic_fixed_om_cost_expr_rule, different_fcr_capex_cost_expr_rule, sum_installed_capacity_by_plants_set_expr_rule, add_generic_fixed_costs, add_generation_variables
from ..constants import MW_TO_KW, THERMAL_PROPERTIES_NAMES

def initialize_thermal_sets(block, data):
    # Initialize THERMAL properties
    block.plants_set = Set( initialize = data['thermal_data']['Plant_id'].astype(str).tolist() )
    block.properties_set = Set( initialize = THERMAL_PROPERTIES_NAMES )
    logging.info(f"Thermal balancing units being considered: {list(block.plants_set)}")

####################################################################################|
# ----------------------------------- Parameters -----------------------------------|
####################################################################################|

def _add_thermal_parameters(block, df):
    
    thermal_dict = df.stack().to_dict()
    thermal_tuple_dict = {( prop, name ): thermal_dict[( name, prop )] for prop in THERMAL_PROPERTIES_NAMES for name in block.plants_set}
    
    block.data = Param( block.properties_set, block.plants_set, initialize = thermal_tuple_dict )
    
    # Gas prices (US$/MMBtu)
    block.fuel_price = Param(
        block.plants_set,
        initialize={bu: block.data["FuelCost", bu] for bu in block.plants_set}
    )

    # Heat rate for gas combined cycle (MMBtu/MWh)
    block.heat_rate = Param( 
        block.plants_set, 
        initialize = {bu: block.data["HeatRate", bu] for bu in block.plants_set}
    )
#block.GasPrice, block.HR, block.FOM_GasCC, block.VOM_GasCC
    # Capex for gas combined cycle units (US$/kW)
    block.CAPEX_M = Param( 
        block.plants_set, 
        initialize ={bu: block.data["Capex", bu] for bu in block.plants_set}
    )

    # Fixed O&M for gas combined cycle (US$/kW-year)
    block.FOM_M = Param( 
        block.plants_set, 
        initialize = {bu: block.data["FOM", bu] for bu in block.plants_set}
    )

    # Variable O&M for gas combined cycle (US$/MWh)
    block.VOM_M = Param( 
        block.plants_set, 
        initialize = {bu: block.data["VOM", bu] for bu in block.plants_set} 
    )
    block.trans_cap_cost = Param(block.plants_set, initialize=0.0)


def add_thermal_parameters(model, data: dict):
    df = data["thermal_data"].set_index("Plant_id")
    _add_thermal_parameters(model.thermal, df)
    
    model.thermal.r = Param( initialize = float(data["scalars"].loc["r"].Value) )  # Interest rate
    model.thermal.FCR = Param( model.thermal.plants_set, initialize = crf_rule ) #Capital Recovery Factor -THERMAL

####################################################################################|
# ------------------------------------ Variables -----------------------------------|
####################################################################################|

def add_thermal_variables(model):
    model.thermal.plant_installed_capacity = Var(model.thermal.plants_set, domain=NonNegativeReals, initialize=0)
    add_generation_variables(model.thermal, model.h, model.thermal.plants_set, domain=NonNegativeReals,  initialize=0)

    # Compute and set the upper bound for CapCC
    CapCC_upper_bound_value = max(
        value(model.demand.ts_parameter[h]) - value(model.nuclear.alpha) *
        value(model.nuclear.ts_parameter[h])
        - value(model.hydro.alpha) * value(model.hydro.ts_parameter[h])
        - value(model.other_renewables.alpha) * value(model.other_renewables.ts_parameter[h])
        for h in model.h
    )
    cap_thermal_units = sum(model.thermal.data["MaxCapacity", bu] for bu in model.thermal.plants_set)
    if ( len( list(model.thermal.plants_set) ) <= 1 ):
        model.thermal.plant_installed_capacity[model.thermal.plants_set[1]].setlb( model.thermal.data["MinCapacity", model.thermal.plants_set[1]] )
        if ( CapCC_upper_bound_value > cap_thermal_units ):
            model.thermal.plant_installed_capacity[model.thermal.plants_set[1]].setub( CapCC_upper_bound_value )
            logging.warning(f"There is only one thermal balancing unit. " \
            f"Upper bound for Capacity variable was set to {CapCC_upper_bound_value} instead of the input = {cap_thermal_units} to ensure feasibility.")
        else:
            model.thermal.plant_installed_capacity[model.thermal.plants_set[1]].setub( model.thermal.data["MaxCapacity", model.thermal.plants_set[1]] )
    else:
        
        for bu in model.thermal.plants_set:
            model.thermal.plant_installed_capacity[bu].setub( model.thermal.data["MaxCapacity", bu] )
            model.thermal.plant_installed_capacity[bu].setlb( model.thermal.data["MinCapacity", bu] )
        if ( CapCC_upper_bound_value > cap_thermal_units ):
            logging.warning(f"Total allowed capacity for thermal units is {cap_thermal_units}MW. This value might be insufficient to achieve problem feasibility, consider increase it to at least {CapCC_upper_bound_value}MW.")


####################################################################################|
# ----------------------------------- Expressions ----------------------------------|
####################################################################################|
def total_thermal_expr_rule(m):
    """
    Expression to calculate the total generation from thermal units.
    
    Parameters:
    m: The optimization model instance.
    h: Time period index.
    bu: Balancing unit index.
    
    Returns:
    The sum of generation from the specified thermal unit across all time periods.
    """
    return sum(m.GenCC[h, bu] for h in m.h for bu in m.thermal.plants_set)

def _add_thermal_expressions(block, set_hours):
    block.total_plant_generation = Expression( block.plants_set, rule = lambda m, bu:sum(m.generation[h, bu] for h in set_hours ) )
    block.total_generation = Expression( rule = sum(block.total_plant_generation[bu] for bu in block.plants_set) )
    block.total_installed_capacity = Expression( rule = sum_installed_capacity_by_plants_set_expr_rule )

    block.fixed_om_cost_expr = Expression( rule = generic_fixed_om_cost_expr_rule )
    block.capex_cost_expr = Expression( rule = different_fcr_capex_cost_expr_rule )

    block.total_fuel_cost_expr = Expression( 
        rule = sum(
            ( block.fuel_price[bu] * block.heat_rate[bu] ) * ( block.total_plant_generation[bu] )
            for bu in block.plants_set ) 
            )
    
    block.total_vom_cost_expr = Expression( 
        rule = sum( block.VOM_M[bu] * block.total_plant_generation[bu] for bu in block.plants_set ) 
        )

def add_thermal_expressions(model):
    _add_thermal_expressions(model.thermal, model.h)
    


####################################################################################|
# ----------------------------------- Constraints ----------------------------------|
####################################################################################|

def add_thermal_constraints( model ):
    set_hours = model.h
    # Capacity of the backup generation
    model.thermal.capacity_generation_constraint = Constraint( set_hours, model.thermal.plants_set, rule = lambda m,h,bu: m.plant_installed_capacity[bu] >= m.generation[h,bu]  )


####################################################################################|
# -----------------------------------= Add_costs -----------------------------------|
####################################################################################|
def add_thermal_fixed_costs(model):
    """
    Add cost-related variables for thermal units to the model.

    Parameters:
    model: The optimization model to which thermal cost variables will be added.

    Returns:
    Costs sum for each thermal unit, including capital and fixed O&M costs.
    """
    return (
        add_generic_fixed_costs(model.thermal)
    )

def add_thermal_variable_costs(model):
    """
    Add variable costs (Fuel cost + VOM cost) for thermal units to the model.

    Parameters:
    model: The optimization model to which thermal variable costs will be added.

    Returns:
    Variable costs sum for thermal units, including fuel costs.
    """
    return (
        model.thermal.total_fuel_cost_expr + model.thermal.total_vom_cost_expr
    )

