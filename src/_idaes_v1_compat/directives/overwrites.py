from bwcompat.patch.directives import OverwriteModuleAttr


enable_process_block_kwargs_through_default = OverwriteModuleAttr(
    module="idaes.core.base.process_block", name="_process_kwargs",
    replacement="_idaes_v1_compat.definitions.internals:_process_kwargs_supporting_default"
)


convergence_base = OverwriteModuleAttr(
    module="idaes.core.util.convergence.convergence_base", name="register_convergence_class",
    replacement="_idaes_v1_compat.definitions.internals:register_convergence_class_with_disambiguation"
)
