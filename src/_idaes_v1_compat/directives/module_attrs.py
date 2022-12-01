from bwcompat.patch.directives import ProxyModuleAttr


core_util = ProxyModuleAttr.for_modules({
    "idaes.core.util": {
        "get_solver": "idaes.core.solvers:get_solver",
        "copy_port_values": None,
        "TagReference": None,
    },
    "idaes.core.util.testing": {
        "get_solver": "idaes.core.solvers:get_solver",
        "get_default_solver": "idaes.core.solvers:get_solver",
    },
    "idaes.core.util.misc": {
        "get_solver": "idaes.core.solvers:get_solver",
        "_GeneralVarLikeExpressionData": "idaes.core.base.var_like_expression:_GeneralVarLikeExpressionData",
        "VarLikeExpression": "idaes.core.base.var_like_expression:VarLikeExpression",
        "SimpleVarLikeExpression": "idaes.core.base.var_like_expression:SimpleVarLikeExpression",
        "AbstractSimpleVarLikeExpression": "idaes.core.base.var_like_expression:AbstractSimpleVarLikeExpression",
        "IndexedVarLikeExpression": "idaes.core.base.var_like_expression:IndexedVarLikeExpression",
        "TagReference": None,
        "copy_port_values": None,
        "svg_tag": None,
        "svg_tag_new": None,
    },
    "idaes.core.util.config": {
        "list_of_floats": None,
        "list_of_strings": None,
        "list_of_phase_types": None,
        "PhaseType": "idaes.core.base.phases:PhaseType"
    },
    "idaes.core.util.initialization": {
        "FlowsheetBlock": "idaes.core.base:FlowsheetBlock"
    },
    "idaes.core.util.dyn_utils": {
        "is_implicitly_indexed_by": None,
    },
    "idaes.core.util.scaling": {
        "scale_single_constraint": None,
        "scale_constraints": None,
    },
    "idaes.core.util.plot": {
        "stitch_dynamic": None,
    },
    "idaes.core.util.tables": {
        "tag_state_quantities": None,
    },
    "idaes.core.util.expr_doc": {
        "ipython_document_constraints": None,
    },
    "idaes.core.util.testing": {
        "default_solver": "idaes.core.solvers:get_solver",
    },
})


unc_prop = ProxyModuleAttr.for_modules({
    "idaes.apps.uncertainty_propagation.sens": {
        "kaug": "_idaes_v1_compat.definitions.apps_uncertainty_propagation:kaug",
        "sipopt": "_idaes_v1_compat.definitions.apps_uncertainty_propagation:sipopt",
    },
})

pure_props = ProxyModuleAttr.from_mapping({
    "idaes.generic_models.properties.core.pure.NIST:cp_mol_ig_comp": "idaes.models.properties.modular_properties.pure.NIST:NIST.cp_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.RPP3:cp_mol_ig_comp": "idaes.models.properties.modular_properties.pure.RPP3:RPP3.cp_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.RPP4:cp_mol_ig_comp": "idaes.models.properties.modular_properties.pure.RPP4:RPP4.cp_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.RPP5:cp_mol_ig_comp": "idaes.models.properties.modular_properties.pure.RPP5:RPP5.cp_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.NIST:enth_mol_ig_comp": "idaes.models.properties.modular_properties.pure.NIST:NIST.enth_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.RPP3:enth_mol_ig_comp": "idaes.models.properties.modular_properties.pure.RPP3:RPP3.enth_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.RPP4:enth_mol_ig_comp": "idaes.models.properties.modular_properties.pure.RPP4:RPP4.enth_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.RPP5:enth_mol_ig_comp": "idaes.models.properties.modular_properties.pure.RPP5:RPP5.enth_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.NIST:entr_mol_ig_comp": "idaes.models.properties.modular_properties.pure.NIST:NIST.entr_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.RPP3:entr_mol_ig_comp": "idaes.models.properties.modular_properties.pure.RPP3:RPP3.entr_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.RPP4:entr_mol_ig_comp": "idaes.models.properties.modular_properties.pure.RPP4:RPP4.entr_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.RPP5:entr_mol_ig_comp": "idaes.models.properties.modular_properties.pure.RPP5:RPP5.entr_mol_ig_comp",
    "idaes.generic_models.properties.core.pure.NIST:pressure_sat_comp": "idaes.models.properties.modular_properties.pure.NIST:NIST.pressure_sat_comp",
    "idaes.generic_models.properties.core.pure.RPP3:pressure_sat_comp": "idaes.models.properties.modular_properties.pure.RPP3:RPP3.pressure_sat_comp",
    "idaes.generic_models.properties.core.pure.RPP4:pressure_sat_comp": "idaes.models.properties.modular_properties.pure.RPP4:RPP4.pressure_sat_comp",
    "idaes.generic_models.properties.core.pure.RPP5:pressure_sat_comp": "idaes.models.properties.modular_properties.pure.RPP5:RPP5.pressure_sat_comp",
    "idaes.generic_models.properties.core.pure.Perrys:cp_mol_liq_comp": "idaes.models.properties.modular_properties.pure.Perrys:Perrys.cp_mol_liq_comp",
    "idaes.generic_models.properties.core.pure.Perrys:enth_mol_liq_comp": "idaes.models.properties.modular_properties.pure.Perrys:Perrys.enth_mol_liq_comp",
    "idaes.generic_models.properties.core.pure.Perrys:entr_mol_liq_comp": "idaes.models.properties.modular_properties.pure.Perrys:Perrys.entr_mol_liq_comp",
    "idaes.generic_models.properties.core.pure.Perrys:dens_mol_liq_comp": "idaes.models.properties.modular_properties.pure.Perrys:Perrys.dens_mol_liq_comp",
    "idaes.generic_models.properties.core.pure.Perrys:dens_mol_liq_comp_eqn_1": "idaes.models.properties.modular_properties.pure.Perrys:Perrys.dens_mol_liq_comp_eqn_1",
    "idaes.generic_models.properties.core.pure.Perrys:dens_mol_liq_comp_eqn_2": "idaes.models.properties.modular_properties.pure.Perrys:Perrys.dens_mol_liq_comp_eqn_2",
})

util_system = ProxyModuleAttr.for_modules({
    "idaes.util.system": {
        "fail_if_tempdir_is_curdir": "idaes.core.dmf.util:fail_if_tempdir_is_curdir",
        "NamedTemporaryFile": "idaes.core.dmf.util:NamedTemporaryFile",
        "mkdtemp": "idaes.core.dmf.util:mkdtemp",
        "TemporaryDirectory": None,
    },
})


powergen = ProxyModuleAttr.with_no_replacement({
    "idaes.power_generation.control.pid_controller": [
        "PIDController",
        "PIDControllerData",
        "UnitModelBlockData",
        "declare_process_block_class",
        "ConfigurationError",
    ],
    "idaes.power_generation.flowsheets.NGFC.NGFC_flowsheet": [
        "build_power_island",
        "set_power_island_inputs",
        "build_reformer",
        "set_reformer_inputs",
        "scale_flowsheet",
        "initialize_power_island",
        "initialize_reformer",
        "connect_reformer_to_power_island",
        "SOFC_ROM_setup",
        "add_SOFC_energy_balance",
        "add_result_constraints",
        "make_stream_dict",
        "pfd_result",
        "main",
        "FlowsheetBlock",
        "copy_port_values",
        "svg_tag",
        "degrees_of_freedom",
        "create_stream_table_dataframe",
        "InitializationError",
        "GenericParameterBlock",
        "GenericReactionParameterBlock",
        "Mixer",
        "Heater",
        "HeatExchanger",
        "PressureChanger",
        "GibbsReactor",
        "StoichiometricReactor",
        "Separator",
        "Translator",
        "delta_temperature_underwood_callback",
        "ThermodynamicAssumption",
        "SplittingType",
        "MomentumMixingType",
        "get_prop",
        "get_rxn",
        "build_SOFC_ROM",
        "initialize_SOFC_ROM",
    ],
    "idaes.power_generation.flowsheets.gas_turbine.gas_turbine": [
        "tag_model",
        "write_pfd_results",
        "performance_curves",
        "main",
        "run_full_load",
        "run_series",
        "FlowsheetBlock",
        "GenericParameterBlock",
        "GenericReactionParameterBlock",
        "propagate_state",
        "get_solver",
        "get_prop",
        "get_rxn",
        "use_idaes_solver_configuration_defaults",
    ],
    "idaes.power_generation.flowsheets.supercritical_power_plant.boiler_subflowsheet_build": [
        "DeltaTMethod",
    ],
    "idaes.power_generation.properties.NGFC.ROM.SOFC_ROM": [
        "build_dict",
        "build_matrix",
        "build_SOFC_ROM",
        "initialize_SOFC_ROM",
    ],
    "idaes.power_generation.properties.natural_gas_PR": [
        "EosType",
        "get_prop",
        "get_rxn",
    ],
    "idaes.power_generation.unit_models.boiler_heat_exchanger": [
        "_DeprecateDeltaTMethod",
        "DeltaTMethod",
        "delta_temperature_underwood_tune_callback",
        "ControlVolume0DBlock",
        "MaterialBalanceType",
        "EnergyBalanceType",
        "MomentumBalanceType",
        "UnitModelBalanceType",
        "is_physical_parameter_block",
        "DefaultBool",
        "functions_lib",
        "InitializationError",
        "UnitModelBlockData",
    ],
    "idaes.power_generation.unit_models.helm.condenser_ntu": [
        "ConfigurationError",
    ],
})


convergence = ProxyModuleAttr.with_no_replacement({
    "idaes.convergence.generic_models.pressure_changer": [
        "PressureChangerConvergenceEvaluation",
        "FlowsheetBlock",
        "PressureChanger",
        "ThermodynamicAssumption",
    ],
    "idaes.convergence.power_generation.compressor": [
        "HelmIsentropicCompressor",
        "create_isentropic_compressor",
        "HelmIsentropicCompressorConvergenceEvaluation",
        "get_solver",
    ],
    "idaes.convergence.power_generation.heater": [
        "create_model_steady_state",
        "create_model_dynamic",
        "HelmValve",
        "FlowsheetBlock",
        "MaterialBalanceType",
        "Heater",
        "_set_port",
        "get_solver",
    ],
    "idaes.convergence.power_generation.turbine": [
        "create_isentropic_turbine",
        "HelmIsentropicTurbineConvergenceEvaluation",
        "HelmIsentropicTurbine",
        "get_solver",
    ],
})


costing = ProxyModuleAttr.with_no_replacement({
    "idaes.power_generation.costing.power_plant_costing": [
        "get_PP_costing",
        "get_cCO2_costing",
        "get_ASU_cost",
        "get_fixed_OM_costs",
        "get_variable_OM_costs",
        "get_sCO2_unit_cost",
        "initialize_fixed_OM_costs",
        "initialize_variable_OM_costs",
        "costing_initialization",
        "display_total_plant_costs",
        "display_bare_erected_costs",
        "display_equipment_costs",
        "get_total_TPC",
        "display_flowsheet_cost",
        "check_sCO2_costing_bounds",
    ],
    "idaes.core.util.unit_costing": [
        "global_costing_parameters",
        "_make_vars",
        "hx_costing",
        "pressure_changer_costing",
        "vessel_costing",
        "platforms_ladders",
        "plates_cost",
        "fired_heater_costing",
        "cstr_costing",
        "flash_costing",
        "rstoic_costing",
        "pfr_costing",
        "initialize",
        "calculate_scaling_factors",
        "const",
        "ConfigurationError",
    ],
})


dmf = ProxyModuleAttr.with_no_replacement({
    "idaes.dmf": [
        "find_property_packages",
        "index_property_packages",
    ],
    "idaes.dmf.propdata": [
        "AddedCSVColumnError",
        "Fields",
        "PropertyTable",
        "PropertyData",
        "PropertyMetadata",
        "PropertyColumn",
        "StateColumn",
        "convert_csv",
        "get_file",
    ],
    "idaes.dmf.propindex": [
        "index_property_metadata",
        "DMFVisitor",
    ],
    "idaes.dmf.tabular": [
        "Fields",
        "TabularObject",
        "Table",
        "TabularData",
        "Metadata",
        "Column",
        "get_file",
    ],
    "idaes.dmf.userapi": [
        "index_property_packages",
        "find_property_packages",
        "get_propertydb_table",
    ],
    "idaes.dmf.surrmod": [
        "SurrogateModel",
        "Predicates",
    ],
    "idaes.dmf.dmfbase": [
        "get_propertydb_table",
    ],
})


ui = ProxyModuleAttr.for_modules({
    "idaes.ui.icons": {
        "UnitModelIcon": "idaes.core.ui.icons.icons:UnitModelIcon",
    },
})


mea = ProxyModuleAttr.with_no_replacement({
    "idaes.power_generation.carbon_capture.mea_solvent_system.properties.liquid_prop": [
        "LiquidParameterBlock",
        "PhysicalParameterData",
        "LiquidStateBlockMethods",
        "LiquidStateBlock",
        "LiquidStateBlockData",
        "declare_process_block_class",
        "MaterialFlowBasis",
        "PhysicalParameterBlock",
        "StateBlockData",
        "StateBlock",
        "Component",
        "LiquidPhase",
        "fix_state_vars",
        "revert_state_vars",
        "solve_indexed_blocks",
        "degrees_of_freedom",
        "ProcessType",
        "get_solver",
    ],
    "idaes.power_generation.carbon_capture.mea_solvent_system.properties.vapor_prop": [
        "VaporParameterBlock",
        "PhysicalParameterData",
        "VaporStateBlockMethods",
        "VaporStateBlock",
        "VaporStateBlockData",
        "CONST",
        "declare_process_block_class",
        "MaterialFlowBasis",
        "PhysicalParameterBlock",
        "StateBlockData",
        "StateBlock",
        "Component",
        "VaporPhase",
        "fix_state_vars",
        "revert_state_vars",
        "solve_indexed_blocks",
        "degrees_of_freedom",
        "number_unfixed_variables",
        "ProcessType",
        "get_solver",
    ],
    "idaes.power_generation.carbon_capture.mea_solvent_system.unit_models.column": [
        "ProcessType",
        "PackedColumn",
        "PackedColumnData",
        "CONST",
        "ControlVolume1DBlock",
        "UnitModelBlockData",
        "declare_process_block_class",
        "MaterialBalanceType",
        "EnergyBalanceType",
        "MomentumBalanceType",
        "FlowDirection",
        "get_solver",
        "is_physical_parameter_block",
        "FlowPattern",
        "add_object_reference",
        "ConfigurationError",
        "DistributedVars",
    ],
})


generic = ProxyModuleAttr.with_no_replacement({
    "idaes.generic_models.control.pid_controller": [
        "PIDForm",
        "PIDBlock",
        "PIDBlockData",
        "ProcessBlockData",
        "declare_process_block_class",
        "smooth_max",
        "smooth_min",
        "ConfigurationError",
    ],
    "idaes.generic_models.control": [
        "PIDBlock",
        "PIDForm",
    ],
    "idaes.generic_models.properties.core.phase_equil.smooth_VLE": [
        "phase_equil",
        "calculate_scaling_factors",
        "phase_equil_initialization",
        "calculate_teq",
    ],
    "idaes.generic_models.unit_models.column_models.solvent_column": [
        "CONST",
        "degrees_of_freedom",
    ],
    "idaes.generic_models.unit_models.heat_exchanger_1D": [
        "WallConductionType",
        "c",
    ],
})

core_other = ProxyModuleAttr.for_modules({
    "idaes.core.unit_model": {
        "PropertyPackageError": None,
    },
    "idaes.core.property_meta": {
        "UnitNames": None,
    },
    "idaes.config": {
        "basic_platforms": None,
    },
    "idaes.core.solvers.petsc": {
        "_import_petsc_binary_io": None,
    },
    "idaes.core.property_base": {
        "Phase": "idaes.core.base.phases:Phase",
        "Component": "idaes.core.base.components:Component",
    }
})


helmholtz_iapws95_swco2 = ProxyModuleAttr.for_modules({
    "idaes.generic_models.properties.helmholtz.helmholtz": {
        "StateBlock": None,
        "StateBlockData": None,
        "PhysicalParameterBlock": None,
        "MaterialBalanceType": None,
        "EnergyBalanceType": None,
        "MaterialFlowBasis": None,
        "LiquidPhase": None,
        "VaporPhase": None,
        "Phase": None,
        "Component": None,
        "smooth_max": "idaes.core.util.math:smooth_max",
        "ConfigurationError": None,
        "_available": None,
        "_add_external_functions": None,
        "_htpx": None,
        "_StateBlock": None,
    },
    "idaes.generic_models.properties.iapws95": {
        "_available": None,
        "_htpx": None,
    },
    "idaes.generic_models.properties.swco2": {
        "StateBlock": None,
        "StateBlockData": None,
        "_available": None,
        "_htpx": None,
    },
    "idaes.generic_models.properties.tests.iapws95_plots": {
        "make_model": None,
        "plot_temperature_vapor_fraction": None,
        "plot_psat": None,
        "plot_Tsat": None,
        "plot_hpt": None,
    }
})


gas_solid_contactors = ProxyModuleAttr.for_modules({
    "idaes.gas_solid_contactors.properties.methane_iron_OC_reduction.gas_phase_thermo": {
        "smooth_max": "idaes.core.util.math:smooth_max",
    },
})


unused_imports= ProxyModuleAttr.for_modules({
    "idaes.core.solvers.petsc": {
        "degrees_of_freedom": "idaes.core.util.model_statistics:degrees_of_freedom",
        "get_solver": "idaes.core.solvers:get_solver",
    },
    "idaes.generic_models.control.controller": {
        "get_solver": "idaes.core.solvers:get_solver",
    },
    "idaes.generic_models.properties.core.eos.ceos": {
        "LiquidPhase":  "idaes.core:LiquidPhase",
        "VaporPhase":  "idaes.core:VaporPhase",
    },
    "idaes.generic_models.properties.core.eos.eos_base": {
        "PropertyNotSupportedError": "idaes.core.util.exceptions:PropertyNotSupportedError",
    },
    "idaes.generic_models.properties.core.examples.HC_PR_vap": {
        "LiquidPhase":  "idaes.core:LiquidPhase",
    },
    "daes.generic_models.properties.core.state_definitions.FTPx": {
        "UserModelError": "idaes.core.util.exceptions:UserModelError",
    },
    "idaes.generic_models.properties.cubic_eos.cubic_prop_pack": {
        "functions_lib": None,
    },
    "idaes.generic_models.unit_models.column_models.condenser": {
        "MomentumBalanceType": "idaes.core:MomentumBalanceType",
    },
    "idaes.generic_models.unit_models.column_models.tray_column": {
        "InitializationError": "idaes.core.util.exceptions:InitializationError",
    },
    "idaes.generic_models.unit_models.plug_flow_reactor": {
        "const": "idaes.core.util.constants:Constants",
    },
    "idaes.generic_models.unit_models.valve": {
        "from_json": "idaes.core.util.model_serializer:from_json",
        "to_json": "idaes.core.util.model_serializer:to_json",
        "StoreSpec": "idaes.core.util.model_serializer:StoreSpec",
        "degrees_of_freedom": "idaes.core.util.model_statistics:degrees_of_freedom",
    },
    "idaes.power_generation.flowsheets.supercritical_power_plant.SCPC_full_plant": {
        "delta_temperature_underwood_callback":
            "idaes.models.until_models.heat_exchanger:delta_temperature_underwood_callback",
        "ThermodynamicAssumption": "idaes.models.unit_models.pressure_changer:ThermodynamicAssumption",
    },
    "idaes.power_generation.flowsheets.supercritical_steam_cycle": {
        "create_stream_table_dataframe": "idaes.core.util.tables:create_stream_table_dataframe",
    },
    "idaes.power_generation.flowsheets.supercritical_steam_cycle.supercritical_steam_cycle": {
        "HeatExchanger": "idaes.models.unit_models:HeatExchanger",
        "create_stream_table_dataframe": "idaes.core.util.tables:create_stream_table_dataframe",
        "ThermodynamicAssumption": "idaes.models.unit_models.pressure_changer:ThermodynamicAssumption",
    },
    "idaes.power_generation.properties.natural_gas_PR": {
        "fugacity": "idaes.models.properties.modular_properties.phase_equil.forms:fugacity",
        "IdealBubbleDew": "idaes.models.properties.modular_properties.phase_equil.bubble_dew:IdealBubbleDew",
        "Perrys": "idaes.models.properties.modular_properties.pure:Perrys",
        "GenericReactionParameterBlock":
            "idaes.models.properties.modular_properties.base.generic_reaction:GenericReactionParameterBlock",
    },
    "idaes.power_generation.unit_models.helm.condenser_ntu": {
        "add_object_reference": "idaes.core.util.misc:add_object_reference",
    },
    "idaes.power_generation.unit_models.helm.turbine_outlet": {
        "degrees_of_freedom": "idaes.core.util.model_statistics:degrees_of_freedom",
    },
    "idaes.power_generation.unit_models.helm.turbine_stage": {
        "from_json": "idaes.core.util.model_serializer:from_json",
        "to_json": "idaes.core.util.model_serializer:to_json",
        "StoreSpec": "idaes.core.util.model_serializer:StoreSpec",
        "degrees_of_freedom": "idaes.core.util.model_statistics:degrees_of_freedom",
    },
    "idaes.surrogate.base.surrogate_base": {
        "compute_fit_metrics": "idaes.core.surrogate.metrics:compute_fit_metrics",
    },
})
