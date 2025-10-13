import subprocess, os

import os
import subprocess
import sys

def run_command_live(command, cwd=None):
    """
    Run a command in a given working directory, stream stdout + stderr live (UTF-8 decoded),
    and gracefully handle characters that cannot be printed on Windows consoles.

    :param command: The command to run (str or list of str)
    :param cwd: Directory to run the command in (str or Path), optional
    :return: Full combined stdout/stderr as a string
    """
    # Ensure command is a list
    if isinstance(command, str):
        cmd = command.split()
    else:
        cmd = list(command)

    # Set Windows console to UTF-8 if on Windows
    if os.name == "nt":
        os.system("chcp 65001 >nul")
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    cwd_str = str(cwd) if cwd else os.getcwd()

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # merge stderr into stdout
        bufsize=1,
        text=True,                # decode to text
        encoding="utf-8",
        errors="replace",         # replace unprintable chars
        cwd=cwd_str
    )

    output_lines = []

    try:
        for line in process.stdout:
            # Replace characters that cannot be printed on this console
            safe_line = line.encode(sys.stdout.encoding, errors="replace").decode(sys.stdout.encoding)
            print(safe_line, end="")
            output_lines.append(line)

        process.stdout.close()
        returncode = process.wait()

        full_output = ''.join(output_lines)

        if returncode != 0:
            raise RuntimeError(
                f"Command '{' '.join(cmd)}' failed!\n"
                f"Return code: {returncode}\n"
                f"Output:\n{full_output}"
            )

        return full_output

    except Exception as e:
        if process.poll() is None:
            process.kill()
        raise e
