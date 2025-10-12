import subprocess
import os
from ..execsteps import add_step, finish_step, ExecutionStatus, getscr

class Flags:
    Recursive = 0b01
    Force = 0b10
    IgnoreErrors = 0b1000

def rm(path: str, flags: int):
    Recursive = (flags & 0b01) != 0
    Force = (flags & 0b10) != 0
    ForceUseLinux = (flags & 0b100) != 0  # Debug Only
    IgnoreErrors = (flags & 0b1000) != 0
    if ForceUseLinux:
        print('ForceUseLinux active')

    sid = add_step(f"Deleting {path} (flags: r={Recursive},f={Force},fl={ForceUseLinux})")
    
    if os.name == "nt" and not ForceUseLinux:  # Windows
        args = []
        if Recursive: args.append("-Recurse")
        if Force: args.append("-Force")
        r = subprocess.Popen(["powershell", "-Command", f"Remove-Item {path} {' '.join(args)}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    else:
        args = []
        if Recursive: args.append("-r")
        if Force: args.append("-f")
        r =  subprocess.Popen(["rm", *args, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout_data, stderr_data = r.communicate()

    if stdout_data:
        add_step(stdout_data, ExecutionStatus.Stdout)
    if stderr_data and not IgnoreErrors:
        add_step(stderr_data, ExecutionStatus.Stderr)

    if r.returncode == 0:
        finish_step(sid, ExecutionStatus.CompletedSuccessfully)
    else:
        if not IgnoreErrors:
            finish_step(sid, ExecutionStatus.Failed)
        else:
            finish_step(sid, ExecutionStatus.Warning)

    return r
