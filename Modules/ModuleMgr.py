from typing import Callable

from Utils.Logger import Logger, LogLevel
from .ManagerTestModule import *
from .WorkerTestModule import *


class ModuleMgr:
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

        for module in BaseWorkerTestModule.WorkerTestModuleFactoryMethods.keys():
            if module not in BaseManagerTestModule.ManagerTestModuleFactoryMethods.keys():
                Logger().log_error(f"WorkerTestModule: {module} not found in ManagerTestModuleFactoryMethods",
                                   LogLevel.LOW_FREQ)
            else:
                rv.append(module)

        return rv

    def get_module_worker_part(self, module_name: str) -> Callable[[dict[str, str]], BaseWorkerTestModule]:
        if module_name not in BaseWorkerTestModule.WorkerTestModuleFactoryMethods:
            raise ValueError(f"Module {module_name} not found in WorkerTestModuleFactoryMethods")
        return BaseWorkerTestModule.WorkerTestModuleFactoryMethods[module_name]

    def get_module_manager_part(self, module_name: str) -> Callable[[dict[str, str]], BaseManagerTestModule]:
        if module_name not in BaseManagerTestModule.ManagerTestModuleFactoryMethods:
            raise ValueError(f"Module {module_name} not found in ManagerTestModuleFactoryMethods")
        return BaseManagerTestModule.ManagerTestModuleFactoryMethods[module_name]

    def validate_module(self, module_name: str) -> None:
        if module_name not in self.get_all_modules():
            raise ValueError(f"Module {module_name} not found")

    # ------------------------------
    # Private methods
    # ------------------------------
