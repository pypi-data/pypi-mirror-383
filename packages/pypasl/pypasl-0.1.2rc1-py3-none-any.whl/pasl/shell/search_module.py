import subprocess
import os
from ..execsteps import add_step, finish_step, ExecutionStatus, getscr
import re as regex

class Flags:
    Recursive = 0b0001
    FolderContent = 0b0010
    FileContent = 0b0100
    RegEx = 0b1000

def _search(path: str, _filter: str, flags: int):
    Recursive = (flags & Flags.Recursive) != 0
    Folder = (flags & Flags.FolderContent) != 0
    File = (flags & Flags.FileContent) != 0
    RegEx = (flags & Flags.RegEx) != 0

    if (RegEx):
        f = regex.compile(_filter)
    else:
        f = (lambda x: (_filter in x))

    sid = add_step(f"Searching {path} (flags: r={Recursive},fo={Folder},fi={File},re={RegEx})")

    file_paths = []

    if not Recursive:
        if os.path.isfile(path):
            file_paths.append(path)
        else:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isfile(full_path) and File:
                    file_paths.append(full_path)
                elif os.path.isdir(full_path) and Folder:
                    file_paths.append(full_path)
    else:
        def _walk(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if not File:
                        continue
                    file_paths.append(os.path.join(root, file))
                for dir in dirs:
                    _walk(os.path.join(root, dir))
                    if Folder:
                        file_paths.append(os.path.join(root, dir))
        _walk(path)
                    
    matches = []
    
    for path in file_paths:
        if os.path.isfile(path):
            if Folder:
                if f(os.path.basename(path)):
                    matches.append({'type': 'file', 'matchtype': 'name', 'path': path})
            if File:
                try:
                    with open(path, 'r', errors='ignore') as file:
                        for i, line in enumerate(file):
                            if f(line):
                                matches.append({'type': 'file', 'matchtype': 'content', 'path': path, 'line': i + 1, 'text': line.strip()})
                except Exception as e:
                    add_step(f"Error reading file {path}: {e}", ExecutionStatus.Stderr)
        elif os.path.isdir(path) and Folder:
            if f(os.path.basename(path)):
                matches.append({'type': 'dir', 'matchtype': 'name', 'path': path})
        
    for match in matches:
        if match['type'] == 'file' and match['matchtype'] == 'content':
            add_step(f"Match: {match['path']} [{match['type']}] (Line {match['line']}): {match['text']}", ExecutionStatus.Stdout)
        elif match['type'] == 'file' and match['matchtype'] == 'name':
            add_step(f"Match: {match['path']} [{match['type']}]", ExecutionStatus.Stdout)
        elif match['type'] == 'dir':
            add_step(f"Match: {match['path']} [{match['type']}]", ExecutionStatus.Stdout)
    
    finish_step(sid, ExecutionStatus.CompletedSuccessfully)

    return matches


def search(path: str, _filter: str, flags: int) -> list | None:
    try:
        return _search(path, _filter, flags)
    except Exception as e:
        add_step(f"Error during search: {e}", ExecutionStatus.Error)
        return
