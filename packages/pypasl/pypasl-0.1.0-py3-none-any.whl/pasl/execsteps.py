import curses
import enum
import threading
import time
import keyboard
import textwrap

def _init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) 
        curses.init_color(3, 13, 38, 79) # Dark Blue
        curses.init_pair(3, 3, curses.COLOR_BLACK)
        try:
            if curses.COLORS >= 256:
                curses.init_pair(2, 208, curses.COLOR_BLACK)
            else:
                curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        except curses.error:
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    return stdscr

class ExecutionStatus(enum.Enum):
    InProgress = 0
    CompletedSuccessfully = 1
    Failed = -1
    NoStatus = 2
    Warning = 3
    Error = 4
    Stdout = -2
    Stderr = -3

__window = _init_curses()

__steps = []

__windowpad = curses.newpad(65535, __window.getmaxyx()[1])
__pad = 0
__padlock = threading.RLock()

def __threaded_main_loop():
    global __pad, __offset_lock
    pause = False
    while True:
        if keyboard.is_pressed('up'):
            if pause: continue
            with __padlock:
                if __pad > 0:
                    __pad -= 1
            pause = True
        elif keyboard.is_pressed('down'):
            if pause: continue
            with __padlock:
                if __pad < 65535:
                    __pad += 1
            pause = True
        else:
            pause = False

def add_step(message: str, start_status = ExecutionStatus.InProgress):
    __steps.append(
        {
            'message': message,
            'status': start_status.value
        }
    )
    _output()
    return len(__steps) - 1

def finish_step(id: int, status: ExecutionStatus):
    __steps[id]['status'] = status.value
    _output()

_TO_REFRESH_OUTPUT = False

def _output():
    global __steps, __windowpad, __pad, __padlock

    __windowpad.clear()
    line = 0
    height, width = __window.getmaxyx()

    rows = height \
           -23   # Bottom four lines
    
    start_index = max(0, len(__steps) - rows)
    visible_steps = __steps[start_index:]
    
    for i, step in enumerate(visible_steps):
        if step['status'] == ExecutionStatus.InProgress.value:
            __windowpad.addstr(line, 0, f'[/] {step["message"]}')
        elif step['status'] == ExecutionStatus.CompletedSuccessfully.value:
            __windowpad.addstr(line, 0, f'[+] {step["message"]}')
        elif step['status'] == ExecutionStatus.Failed.value:
            __windowpad.addstr(line, 0, f'[-] {step["message"]}')
        elif step['status'] == ExecutionStatus.NoStatus.value:
            __windowpad.addstr(line, 0, f'[*] {step["message"]}')
        elif step['status'] == ExecutionStatus.Warning.value:
            __windowpad.addstr(line, 0, f'[!] {step["message"]}', curses.color_pair(2))
        elif step['status'] == ExecutionStatus.Error.value:
            __windowpad.addstr(line, 0, f'[!!] {step["message"]}', curses.color_pair(1) | curses.A_BOLD)
        elif step['status'] == ExecutionStatus.Stdout.value:
            lines = textwrap.wrap(step["message"].strip(), width - 1)
            for wrapped_line in lines:
                __windowpad.addstr(line, 0, f'    # {wrapped_line}', curses.color_pair(3) | curses.A_DIM)
                if len(visible_steps) - 1 == i:
                    continue
                if visible_steps[i+1]['status'] not in [ExecutionStatus.Stdout.value, ExecutionStatus.Stderr.value]:
                    line += 1
        elif step['status'] == ExecutionStatus.Stderr.value:
            lines = textwrap.wrap(step["message"].strip(), width - 1)
            for wrapped_line in lines:
                __windowpad.addstr(line, 0, f'    # {wrapped_line}', curses.color_pair(1) | curses.A_DIM)
                if len(visible_steps) - 1 == i:
                    continue
                if visible_steps[i+1]['status'] not in [ExecutionStatus.Stdout.value, ExecutionStatus.Stderr.value]:
                    line += 1
        
        line += 1

    __windowpad.addstr(line + 1, 0, '-' * (width - 1), curses.A_DIM)
    __windowpad.addstr(line + 2, 0, 'Press Ctrl+C to exit.', curses.A_DIM)
    if len(__steps) == 0:
        tmp = "0/0"
    else:
        end_index = min(len(__steps), start_index + rows)
        tmp = f"{start_index + 1}-{end_index}/{len(__steps)}"
    __windowpad.addstr(line + 3, 0, f'{tmp: ^{width}}', curses.A_DIM)

    with __padlock:
        __windowpad.refresh(__pad, 0, 0, 0, height - 1, width - 1)
    time.sleep(0.01)

def getscr():
    global __window, __windowpad
    return __windowpad


import atexit

def _cleanup_curses():
    global __window
    if __window:
        curses.nocbreak()
        __window.keypad(False)
        curses.echo()
        curses.endwin()

atexit.register(_cleanup_curses)

t = threading.Thread(target=__threaded_main_loop, daemon=True)
t.start()
