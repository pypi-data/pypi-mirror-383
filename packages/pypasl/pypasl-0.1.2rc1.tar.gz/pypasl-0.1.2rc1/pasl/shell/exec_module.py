import subprocess
import os
from ..execsteps import add_step, finish_step, ExecutionStatus, getscr
import re as regex

class Flags:
    Sudo = 0b001
    Strict = 0b010
    IgnoreErrors = 0b100
    DontPrintErrors = 0b1000
    HideStdout = 0b10000

def execute(windows_sh, linux_sh, flags: int = 0) -> subprocess.Popen:
    Sudo = (flags & 0b001) != 0
    Strict = (flags & 0b010) != 0
    IgnoreErrors = (flags & 0b100) != 0
    DontPrintErrors = (flags & 0b1000) != 0
    HideStdout = (flags & 0b10000) != 0

    if os.name == "nt":  # Windows
        shell = "powershell"
        args = ["-Command", windows_sh]
    else:  # Linux / MacOS
        shell = "bash"
        args = ["-c", linux_sh]
        if Sudo:
            code = f"sudo {code}"

    sid = add_step(f"Executing command (flags: s={Sudo},st={Strict},ie={IgnoreErrors},de={DontPrintErrors})")

    r = subprocess.Popen([shell, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout_data, stderr_data = r.communicate()

    if stdout_data and not HideStdout:
        add_step(stdout_data, ExecutionStatus.Stdout)
    if stderr_data and not DontPrintErrors:
        add_step(stderr_data, ExecutionStatus.Stderr)

    if r.returncode == 0 or IgnoreErrors:
        finish_step(sid, ExecutionStatus.CompletedSuccessfully)
    else:
        finish_step(sid, ExecutionStatus.Failed)
        if Strict:
            raise Exception(f"Command failed with return code {r.returncode}")

    return r
