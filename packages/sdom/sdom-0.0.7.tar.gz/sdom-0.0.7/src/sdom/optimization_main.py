import logging
#from pympler import muppy, summary
#from pympler import muppy, summary
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition, check_available_solvers
from pyomo.util.infeasible import log_infeasible_constraints
from pyomo.environ import ConcreteModel, Objective, Block, minimize

from .initializations import initialize_sets, initialize_params
from .common.utilities import safe_pyomo_value
from .models.formulations_vre import add_vre_variables, add_vre_expressions, add_vre_balance_constraints
from .models.formulations_thermal import add_thermal_variables, add_thermal_expressions, add_thermal_constraints
from .models.formulations_resiliency import add_resiliency_variables, add_resiliency_constraints
from .models.formulations_storage import add_storage_variables, add_storage_expressions, add_storage_constraints
from .models.formulations_system import objective_rule, add_system_expressions, add_system_constraints
from .models.formulations_imports_exports import add_imports_variables, add_exports_variables, add_imports_exports_cost_expressions, add_imports_constraints, add_exports_constraints
from .models.formulations_hydro import add_hydro_variables, add_hydro_run_of_river_constraints, add_hydro_budget_constraints

from .constants import MW_TO_KW

from .io_manager import get_formulation
# ---------------------------------------------------------------------------------
# Model initialization
# Safe value function for uninitialized variables/parameters

def initialize_model(data, n_hours = 8760, with_resilience_constraints=False, model_name="SDOM_Model"):
    """
    Initializes and configures a Pyomo optimization model for the SDOM framework.
    This function sets up the model structure, including sets, parameters, variables, 
    objective function, and constraints for power system optimization. It supports 
    optional resilience constraints and allows customization of the model name and 
    simulation horizon.
    Args:
        data (dict): Input data required for model initialization, including system 
            parameters, time series, and technology characteristics.
        n_hours (int, optional): Number of hours to simulate (default is 8760, 
            representing a full year).
        with_resilience_constraints (bool, optional): If True, adds resilience-related 
            constraints to the model (default is False).
        model_name (str, optional): Name to assign to the Pyomo model instance 
            (default is "SDOM_Model").
    Returns:
        ConcreteModel: A fully initialized Pyomo ConcreteModel object ready for 
            optimization.
    """

    logging.info("Instantiating SDOM Pyomo optimization model...")
    model = ConcreteModel(name=model_name)

    logging.debug("Instantiating SDOM Pyomo optimization blocks...")
    model.hydro = Block()

    model.imports = Block()
    model.exports = Block()

    model.demand = Block()
    model.nuclear = Block()
    model.other_renewables = Block()
    if with_resilience_constraints:
        model.resiliency = Block() #TODO implement this block
    model.storage = Block()
    model.thermal = Block()
    model.pv = Block()
    model.wind = Block()

    logging.info("Initializing model sets...")
    initialize_sets( model, data, n_hours = n_hours )
    
    logging.info("Initializing model parameters...")
    initialize_params( model, data )    

    # ----------------------------------- Variables -----------------------------------
    logging.info("Adding variables to the model...")
    # Define VRE (wind/solar variables
    logging.debug("-- Adding VRE variables...")
    add_vre_variables( model )

    logging.debug("-- Adding VRE expressions...")
    add_vre_expressions( model )


    logging.debug("-- Adding thermal generation variables...")
    add_thermal_variables( model )

    logging.debug("-- Adding thermal generation expressions...")
    add_thermal_expressions( model )

    # Resilience variables
    if with_resilience_constraints:
        logging.debug("-- Adding resiliency variables...")
        add_resiliency_variables( model )

    # Storage-related variables
    logging.debug("--Adding storage variables...")
    add_storage_variables( model )
    logging.debug("--Adding storage expressions...")
    add_storage_expressions( model )

    logging.debug("-- Adding hydropower generation variables...")
    add_hydro_variables(model)

    # Imports
    if get_formulation(data, component="Imports") != "NotModel":
        logging.debug("-- Adding Imports variables...")
        add_imports_variables( model )
    
    # Exports
    if get_formulation(data, component="Exports") != "NotModel":
        logging.debug("-- Adding Exports variables...")
        add_exports_variables( model )

    add_imports_exports_cost_expressions(model, data)

    add_system_expressions(model)
    # -------------------------------- Objective function -------------------------------
    logging.info("Adding objective function to the model...")
    model.Obj = Objective( rule = objective_rule, sense = minimize )

    # ----------------------------------- Constraints -----------------------------------
    logging.info("Adding constraints to the model...")
    #system Constraints
    logging.debug("-- Adding system constraints...")
    add_system_constraints( model, data )    

    #resiliency Constraints
    if with_resilience_constraints:
        logging.debug("-- Adding resiliency constraints...")
        add_resiliency_constraints( model )
  
    #VRE balance constraints
    logging.debug("-- Adding VRE balance constraints...")
    add_vre_balance_constraints( model )

    #Storage constraints
    logging.debug("-- Adding storage constraints...")
    add_storage_constraints( model )

    logging.debug("-- Adding thermal generation constraints...")
    add_thermal_constraints( model )

    logging.debug("-- Adding hydropower generation constraints...")
    if get_formulation(data, component="hydro")  == "RunOfRiverFormulation":
        add_hydro_run_of_river_constraints(model, data)
    else:
        add_hydro_budget_constraints(model, data)
    

    # Imports
    if get_formulation(data, component="Imports") != "NotModel":
        logging.debug("-- Adding Imports constraints...")
        add_imports_constraints( model, data )
    
    # Imports
    if get_formulation(data, component="Exports") != "NotModel":
        logging.debug("-- Adding Exports constraints...")
        add_exports_constraints( model, data )

        #add_hydro_variables(model)
    
    # Build a model size report
    # Log memory usage before solving
    # all_objects = muppy.get_objects()
    # logging.info("Memory usage before solving:")
    # logging.info(summary.summarize(all_objects))
    # Log memory usage before solving
    # all_objects = muppy.get_objects()
    # logging.info("Memory usage before solving:")
    # logging.info(summary.summarize(all_objects))

    return model

# ---------------------------------------------------------------------------------
# Results collection function
def collect_results( model ):
    """
    Collects and computes results from a Pyomo optimization model for an energy system.
    This function extracts key results from the provided Pyomo model instance, including total costs,
    installed capacities, generation, dispatch, and detailed cost breakdowns for various technologies
    (solar PV, wind, gas, and multiple storage types such as Li-Ion, CAES, PHS, and H2).
    The results are returned as a dictionary with descriptive keys.
    Parameters
    ----------
    model : pyomo.core.base.PyomoModel.ConcreteModel
        The Pyomo model instance containing the optimization results and parameters.
    Returns
    -------
    results : dict
        A dictionary containing the following keys and their corresponding computed values:
            - 'Total_Cost': Total objective value of the model.
            - 'Total_CapCC': Installed capacity of gas combined cycle.
            - 'Total_CapPV': Total installed capacity of solar PV.
            - 'Total_CapWind': Total installed capacity of wind.
            - 'Total_CapScha': Installed charging power capacity for each storage type.
            - 'Total_CapSdis': Installed discharging power capacity for each storage type.
            - 'Total_EcapS': Installed energy capacity for each storage type.
            - 'Total_GenPV': Total generation from solar PV.
            - 'Total_GenWind': Total generation from wind.
            - 'Total_GenS': Total storage discharge for each storage type.
            - 'SolarPVGen': Hourly solar PV generation.
            - 'WindGen': Hourly wind generation.
            - 'GenGasCC': Hourly gas combined cycle generation.
            - 'SolarCapex', 'WindCapex': Annualized capital expenditures for solar and wind.
            - 'SolarFOM', 'WindFOM': Fixed O&M costs for solar and wind.
            - 'Storage1PowerCapex', 'Storage1EnergyCapex', 'Storage1FOM', 'Storage1VOM': Cost breakdowns for Storage1.
            - 'Storage2PowerCapex', 'Storage2EnergyCapex', 'Storage2FOM', 'Storage2VOM': Cost breakdowns for Storage2.
            -  ...
            - 'StoragenPowerCapex', 'StoragenEnergyCapex', 'StoragenFOM', 'StoragenVOM': Cost breakdowns for Storagen.
            - 'GasCCCapex', 'GasCCFuel', 'GasCCFOM', 'GasCCVOM': Cost breakdowns for gas combined cycle.
    Notes
    -----
    - The function assumes the existence of a helper function `safe_pyomo_value` to safely extract values from Pyomo variables.
    - The model is expected to have specific sets and parameters (e.g., model.pv.plants_set, model.wind.plants_set, model.storage.j, model.h, and various cost parameters).
    """

    logging.info("Collecting SDOM results...")
    results = {}
    results['Total_Cost'] = safe_pyomo_value(model.Obj.expr)

    # Capacity and generation results
    logging.debug("Collecting capacity results...")
    results['Total_CapCC'] = safe_pyomo_value(model.thermal.total_installed_capacity )
    results['Total_CapPV'] = safe_pyomo_value( model.pv.total_installed_capacity )
    results['Total_CapWind'] = safe_pyomo_value( model.wind.total_installed_capacity )
    results['Total_CapScha'] = {j: safe_pyomo_value(model.storage.Pcha[j]) for j in model.storage.j}
    results['Total_CapSdis'] = {j: safe_pyomo_value(model.storage.Pdis[j]) for j in model.storage.j}
    results['Total_EcapS'] = {j: safe_pyomo_value(model.storage.Ecap[j]) for j in model.storage.j}

    # Generation and dispatch results
    logging.debug("Collecting generation dispatch results...")
    results['Total_GenPV'] = safe_pyomo_value(model.pv.total_generation)
    results['Total_GenWind'] = safe_pyomo_value(model.wind.total_generation)
    results['Total_GenS'] = {j: sum(safe_pyomo_value(model.storage.PD[h, j]) for h in model.h) for j in model.storage.j}

    results['SolarPVGen'] = {h: safe_pyomo_value(model.pv.generation[h]) for h in model.h}
    results['WindGen'] = {h: safe_pyomo_value(model.wind.generation[h]) for h in model.h}
    results['AggThermalGen'] = {h: sum(safe_pyomo_value(model.thermal.generation[h, bu]) for bu in model.thermal.plants_set) for h in model.h}

    results['SolarCapex'] = safe_pyomo_value( model.pv.capex_cost_expr )
    results['WindCapex'] =  safe_pyomo_value( model.wind.capex_cost_expr )
    results['SolarFOM'] = safe_pyomo_value( model.pv.fixed_om_cost_expr )
    results['WindFOM'] =  safe_pyomo_value( model.wind.fixed_om_cost_expr )

    logging.debug("Collecting storage results...")
    storage_tech_list = list(model.storage.j)

    for tech in storage_tech_list:
        results[f'{tech}PowerCapex'] = model.storage.CRF[tech]*(MW_TO_KW*model.storage.data['CostRatio', tech] * model.storage.data['P_Capex', tech]*model.storage.Pcha[tech]
                        + MW_TO_KW*(1 - model.storage.data['CostRatio', tech]) * model.storage.data['P_Capex', tech]*model.storage.Pdis[tech])
        results[f'{tech}EnergyCapex'] = model.storage.CRF[tech]*MW_TO_KW*model.storage.data['E_Capex', tech]*model.storage.Ecap[tech]
        results[f'{tech}FOM'] = MW_TO_KW*model.storage.data['CostRatio', tech] * model.storage.data['FOM', tech]*model.storage.Pcha[tech] \
                        + MW_TO_KW*(1 - model.storage.data['CostRatio', tech]) * model.storage.data['FOM', tech]*model.storage.Pdis[tech]
        results[f'{tech}VOM'] = model.storage.data['VOM', tech] * sum(model.storage.PD[h, tech] for h in model.h)

    results['TotalThermalCapex'] = sum( model.thermal.FCR[bu] * MW_TO_KW * model.thermal.CAPEX_M[bu] * model.thermal.plant_installed_capacity[bu] for bu in model.thermal.plants_set )
    results['ThermalFuel'] = sum( (model.thermal.fuel_price[bu] * model.thermal.heat_rate[bu]) * sum(model.thermal.generation[h, bu] for h in model.h) for bu in model.thermal.plants_set )
    results['ThermalFOM'] = safe_pyomo_value( model.thermal.fixed_om_cost_expr )
    results['ThermalVOM'] = sum( model.thermal.VOM_M[bu] * sum(model.thermal.generation[h, bu] for h in model.h) for bu in model.thermal.plants_set )

    return results





def configure_solver(solver_config_dict:dict):
    """
    Configure and return a Pyomo solver instance.

    Parameters:
    - solver_name (str): Name of the solver (e.g., 'xpress', 'highs', 'cbc', 'gurobi').
    - solver_options (dict): Optional dictionary of solver-specific options.

    Returns:
    - solver (SolverFactory): Configured Pyomo solver instance.
    """

    
    if solver_config_dict["solver_name"]=="cbc": #or solver_config_dict["solver_name"]=="xpress_direct":
        solver = SolverFactory(solver_config_dict["solver_name"],
                               executable=solver_config_dict["executable_path"]) if solver_config_dict["executable_path"] else SolverFactory(solver_config_dict["solver_name"])
        
    else:
        solver = SolverFactory(solver_config_dict["solver_name"])

    if not solver.available():
        raise RuntimeError(f"Solver '{solver_config_dict['solver_name']}' is not available on this system.")

    # Apply solver-specific options
    if solver_config_dict["options"]:
        for key, value in solver_config_dict["options"].items():
            solver.options[key] = value

    return solver

def get_default_solver_config_dict(solver_name="cbc", executable_path=".\\Solver\\bin\\cbc.exe"):
    solver_dict = {
        "solver_name": "appsi_" + solver_name,
        "options":{
            #"loglevel": 3,
            "mip_rel_gap": 0.002,
            #"keepfiles": True,
            #"logfile": "solver_log.txt", # The filename used to store output for shell solvers
            },
        "solve_keywords":{
            "tee": True, #If true solver output is printed both to the standard output as well as saved to the log file.
            "load_solutions": True, #If True (the default), then solution values are automically transfered to Var objects on the model
            "report_timing": True, #If True (the default), then timing information is reported
            "logfile": "solver_log.txt", # The filename used to store output for shell solvers
            #"solnfile": "./results_pyomo/solver_soln.txt", # The filename used to store the solution for shell solvers
            "timelimit": None, # The number of seconds that a shell solver is run before it is terminated. (default is None)
            },  
    }
    
    if solver_name == "cbc":
        solver_dict["solver_name"] = solver_name
        solver_dict["executable_path"] = executable_path
    elif solver_name == "xpress":
        solver_dict["solver_name"] = "xpress_direct"
        #solver_dict = {"solver_name": "xpress",}
        #solver_dict["executable_path"] = executable_path

    return solver_dict


# Run solver function
def run_solver(model, solver_config_dict:dict):
    """
    Solves the given optimization model using the CBC solver, optionally running multiple times with varying target values.
    Args:
        model: The Pyomo optimization model to be solved. The model must have an attribute 'GenMix_Target' that can be set.
        log_file_path (str, optional): Path to the solver log file. Defaults to './solver_log.txt'.
        optcr (float, optional): The relative MIP gap (optimality criterion) for the solver. Defaults to 0.0.
        num_runs (int, optional): Number of optimization runs to perform, each with a different 'GenMix_Target' value. Defaults to 1.
        cbc_executable_path (str, optional): Path to the CBC solver executable. If None, uses the default CBC solver.
    Returns:
        tuple: A tuple containing:
            - results_over_runs (list): List of dictionaries with results from each run, including 'GenMix_Target' and other collected results.
            - best_result (dict or None): The result dictionary with the lowest 'Total_Cost' found across all runs, or None if no optimal solution was found.
            - result (SolverResults): The Pyomo solver results object from the last run.
    """

    logging.info("Starting to solve SDOM model...")
    solver = configure_solver(solver_config_dict)
    results_over_runs = []
    best_result = None
    best_objective_value = float('inf')

    target_value = float(model.GenMix_Target.value)
    
    logging.info(f"Running optimization for GenMix_Target = {target_value:.2f}")
    result = solver.solve(model, 
                          tee = solver_config_dict["solve_keywords"].get("tee", True),
                          load_solutions = solver_config_dict["solve_keywords"].get("load_solutions", True),
                          #logfile = solver_config_dict["solve_keywords"].get("logfile", "solver_log.txt"),
                          timelimit = solver_config_dict["solve_keywords"].get("timelimit", None),
                          report_timing = solver_config_dict["solve_keywords"].get("report_timing", True),
                          keepfiles = solver_config_dict["solve_keywords"].get("keepfiles", True),
                          #logfile='solver_log.txt'
                            )
    
    if (result.solver.status == SolverStatus.ok) and (result.solver.termination_condition == TerminationCondition.optimal):
        # If the solution is optimal, collect the results
        run_results = collect_results(model)
        run_results['GenMix_Target'] = target_value
        results_over_runs.append(run_results)
        # Update the best result if it found a better one
        if 'Total_Cost' in run_results and run_results['Total_Cost'] < best_objective_value:
            best_objective_value = run_results['Total_Cost']
            best_result = run_results
    else:
        logging.warning(f"Solver did not find an optimal solution for GenMix_Target = {target_value:.2f}.")
        # Log infeasible constraints for debugging
        logging.warning("Logging infeasible constraints...")
        log_infeasible_constraints(model)

    return results_over_runs, best_result, result
