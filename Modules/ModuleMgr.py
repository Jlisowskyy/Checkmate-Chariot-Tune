from Utils.GlobalObj import GlobalObj
from Utils.Logger import Logger, LogLevel
from .ManagerTestModule import *
from .ModuleBuilder import ModuleBuilder
from .WorkerTestModule import *


class ModuleMgr(metaclass=GlobalObj):
    # ------------------------------
    # Class fields
    # ------------------------------

    # ------------------------------
    # Class creation
    # ------------------------------

    def __init__(self) -> None:
        pass

    def destroy(self) -> None:
        pass

    # ------------------------------
    # Class interaction
    # ------------------------------

    def get_all_modules(self) -> list[str]:
        rv: list[str] = []

        for module in BaseWorkerTestModule.WorkerTestModuleBuilders.keys():
            if module not in BaseManagerTestModule.ManagerTestModuleBuilders.keys():
                Logger().log_error(f"WorkerTestModule: {module} not found in ManagerTestModuleFactoryMethods",
                                   LogLevel.LOW_FREQ)
            else:
                rv.append(module)

        return rv

    def get_module_worker_part(self, module_name: str) -> ModuleBuilder:
        if module_name not in BaseWorkerTestModule.WorkerTestModuleBuilders:
            raise ValueError(f"Module {module_name} not found in WorkerTestModuleFactoryMethods")
        return BaseWorkerTestModule.WorkerTestModuleBuilders[module_name]()

    def get_module_manager_part(self, module_name: str) -> ModuleBuilder:
        if module_name not in BaseManagerTestModule.ManagerTestModuleBuilders:
            raise ValueError(f"Module {module_name} not found in ManagerTestModuleFactoryMethods")
        return BaseManagerTestModule.ManagerTestModuleBuilders[module_name]()

    def validate_module(self, module_name: str) -> None:
        if module_name not in self.get_all_modules():
            raise ValueError(f"Module {module_name} not found")

    # ------------------------------
    # Private methods
    # ------------------------------
