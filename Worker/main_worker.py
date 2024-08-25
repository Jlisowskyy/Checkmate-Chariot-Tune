import daemon
from WorkerLib.WorkerProcess import worker_process_init

with daemon.DaemonContext():
    worker_process_init()
