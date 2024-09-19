#!/bin/python

from Modules.ModuleMgr import ModuleMgr
from Utils.Logger import Logger, LogLevel

if __name__ == "__main__":
    Logger("/tmp/tmp_log.txt", True, LogLevel.HIGH_FREQ)

    print(ModuleMgr().get_all_modules())

    Logger().destroy()