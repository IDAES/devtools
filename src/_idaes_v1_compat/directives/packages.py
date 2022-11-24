from bwcompat.patch.directives import ProxyModule


surr = ProxyModule.from_mapping({
    "idaes.surrogate": "idaes.core.surrogate",
    "idaes.surrogate.alamopy_depr": "idaes.apps.alamopy_depr",
    "idaes.surrogate.helmet": "idaes.apps.helmet",
    "idaes.surrogate.ripe": "idaes.apps.ripe",
    "idaes.surrogate.roundingRegression": "idaes.apps.roundingRegression",
})

generic = ProxyModule.from_mapping({
    "idaes.generic_models": "idaes.models",
    "idaes.generic_models.unit_models": "idaes.models.unit_models",
    "idaes.generic_models.unit_models.column_models": "idaes.models_extra.column_models",
    "idaes.gas_solid_contactors": "idaes.models_extra.gas_solid_contactors",
})


dmf_ui = ProxyModule.from_mapping({
    "idaes.dmf": "idaes.core.dmf",
    "idaes.dmf.surrmod": None,
    "idaes.dmf.tabular": None,
    "idaes.dmf.propdata": None,
    "idaes.dmf.propindex": None,
    "idaes.ui": "idaes.core.ui",
    "idaes.ui.icons": "idaes.core.ui.icons.icons",
})


core = ProxyModule.from_mapping({
    "idaes.core.components": "idaes.core.base.components",
    "idaes.core.control_volume0d": "idaes.core.base.control_volume0d",
    "idaes.core.control_volume1d": "idaes.core.base.control_volume1d",
    "idaes.core.control_volume_base": "idaes.core.base.control_volume_base",
    "idaes.core.flowsheet_model": "idaes.core.base.flowsheet_model",
    "idaes.core.phases": "idaes.core.base.phases",
    "idaes.core.process_base": "idaes.core.base.process_base",
    "idaes.core.process_block": "idaes.core.base.process_block",
    "idaes.core.property_base": "idaes.core.base.property_base",
    "idaes.core.property_meta": "idaes.core.base.property_meta",
    "idaes.core.reaction_base": "idaes.core.base.reaction_base",
    "idaes.core.unit_model": "idaes.core.base.unit_model",
})


properties = ProxyModule.from_mapping({
    "idaes.generic_models.properties.core": "idaes.models.properties.modular_properties",
    "idaes.generic_models.properties.core.generic": "idaes.models.properties.modular_properties.base",
    "idaes.generic_models.properties.iapws95": None,
    "idaes.generic_models.properties.swco2": None,
    "idaes.generic_models.properties.helmholtz.helmholtz": None,
    "idaes.generic_models.properties.tests.iapws95_plots": None,
})

powergen = ProxyModule.from_mapping({
    "idaes.power_generation": "idaes.models_extra.power_generation",
    "idaes.power_generation.carbon_capture": "idaes.models_extra.carbon_capture",
    "idaes.power_generation.carbon_capture.compression_system": None,
    "idaes.power_generation.carbon_capture.compression_system.compressor": "idaes.models_extra.carbon_capture.co2_compressor",
    "idaes.power_generation.carbon_capture.mea_solvent_system": "idaes.models_extra.column_models",
    "idaes.power_generation.carbon_capture.mea_solvent_system.properties": "idaes.models_extra.column_models.properties",
    "idaes.power_generation.carbon_capture.mea_solvent_system.properties.MEA_solvent": "idaes.models_extra.column_models.properties.MEA_solvent",
    "idaes.power_generation.carbon_capture.mea_solvent_system.properties.MEA_vapor": "idaes.models_extra.column_models.properties.MEA_vapor",
    "idaes.power_generation.carbon_capture.mea_solvent_system.properties.liquid_prop": None,
    "idaes.power_generation.carbon_capture.mea_solvent_system.properties.vapor_prop": None,
    "idaes.power_generation.carbon_capture.mea_solvent_system.unit_models": None,
    "idaes.power_generation.carbon_capture.mea_solvent_system.unit_models.plate_heat_exchanger": "idaes.models_extra.column_models.plate_heat_exchanger",
    "idaes.power_generation.carbon_capture.mea_solvent_system.unit_models.column": None,

    "idaes.power_generation.control": None,
    "idaes.power_generation.control.pid_controller": None,
    "idaes.power_generation.flowsheets.NGFC": None,
    "idaes.power_generation.flowsheets.NGFC.NGFC_flowsheet": None,
    "idaes.power_generation.flowsheets.gas_turbine": None,
    "idaes.power_generation.flowsheets.gas_turbine.gas_turbine": None,
    "idaes.power_generation.properties.NGFC": None,
    "idaes.power_generation.properties.NGFC.ROM": None,
    "idaes.power_generation.properties.NGFC.ROM.SOFC_ROM": None,

})

convergence = ProxyModule.from_mapping({
    "idaes.convergence": "idaes.models.convergence",
    "idaes.convergence.power_generation": None,
    "idaes.convergence.power_generation.compressor": None,
    "idaes.convergence.power_generation.heater": None,
    "idaes.convergence.power_generation.turbine": None,
    "idaes.convergence.generic_models": None,
    "idaes.convergence.generic_models.pressure_changer": "idaes.models.convergence.pressure_changer",
})

control = ProxyModule.from_mapping({
    "idaes.generic_models.control": None,
    "idaes.generic_models.control.pid_controller": None,
})

costing = ProxyModule.from_mapping({
    "idaes.power_generation.costing": None,
    "idaes.power_generation.costing.power_plant_costing": None,
    "idaes.core.util.unit_costing": None,
})

util = ProxyModule.from_mapping({
    "idaes.util": "idaes.core.util",
    "idaes.util.download_bin": "idaes.commands.util.download_bin",
    "idaes.util.system": None,

    "idaes.core.util.homotopy": "idaes.core.solvers.homotopy",
})