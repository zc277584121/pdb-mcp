"""PDB session management"""

import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from queue import Empty, Queue
from typing import Dict, Optional


class PdbSession:
    """Manages a persistent pdb debugging session"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.output_queue: Queue = Queue()
        self.reader_thread: Optional[threading.Thread] = None
        self.running = False

    def _get_python_path(self, python_path: Optional[str] = None) -> str:
        """Get the Python interpreter path

        Note: We don't use sys.executable because the MCP server may be running
        in a different environment than the client's project being debugged.
        """
        if python_path:
            return python_path

        # Check for virtual environment in the working directory (client's project)
        venv_paths = [
            Path(".venv/bin/python"),
            Path("venv/bin/python"),
            Path(".venv/Scripts/python.exe"),  # Windows
            Path("venv/Scripts/python.exe"),  # Windows
        ]

        for venv_path in venv_paths:
            if venv_path.exists():
                return str(venv_path.absolute())

        # Default to 'python' command (let system PATH determine which Python)
        return "python"

    def start(
        self,
        script_path: str,
        args: str = "",
        python_path: Optional[str] = None,
        timeout: float = 5.0,
        working_directory: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> str:
        """Start a pdb debugging session

        Args:
            script_path: Path to the Python script to debug
            args: Command-line arguments to pass to the script
            python_path: Optional path to Python interpreter
            timeout: Time to wait without new output before returning (seconds). Default: 5.0
            working_directory: Directory to run the command in (defaults to current directory)
            env: Optional environment variables to set (will be added to existing environment)
        """
        if self.process is not None:
            return "Error: A debugging session is already running. Please quit the current session first."

        try:
            # Get Python interpreter path
            python_cmd = self._get_python_path(python_path)

            # Construct command
            cmd = f"{python_cmd} -m pdb {script_path}"
            if args:
                cmd += f" {args}"

            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)

            # Start process
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=working_directory,  # Run in specified directory
                env=process_env,  # Set environment variables
            )

            self.running = True

            # Start output reader thread
            self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self.reader_thread.start()

            # Get initial output (wait for pdb to start)
            output = self._get_output(timeout=timeout)

            # Build result message
            result = (
                f"Debug session started for: {script_path}\nUsing Python: {python_cmd}"
            )
            if working_directory:
                result += f"\nWorking directory: {working_directory}"
            result += f"\n\n{output}"
            return result

        except Exception as e:
            self.cleanup()
            return f"Error starting debug session: {str(e)}"

    def start_pytest(
        self,
        args: str = "",
        python_path: Optional[str] = None,
        timeout: float = 10.0,
        working_directory: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> str:
        """Start a pytest debugging session with --pdb flag

        Args:
            args: Arguments to pass after 'pytest --pdb' (e.g., 'test_module.py', '-k test_login', etc.)
            python_path: Optional path to Python interpreter
            timeout: Time to wait without new output before returning (seconds). Default: 10.0
            working_directory: Directory to run the command in (defaults to current directory)
            env: Optional environment variables to set (will be added to existing environment)
        """
        if self.process is not None:
            return "Error: A debugging session is already running. Please quit the current session first."

        try:
            # Get Python interpreter path
            python_cmd = self._get_python_path(python_path)

            # Construct pytest command with --pdb
            cmd = f"{python_cmd} -m pytest --pdb"
            if args:
                cmd += f" {args}"

            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)

            # Start process
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=working_directory,  # Run in specified directory
                env=process_env,  # Set environment variables
            )

            self.running = True

            # Start output reader thread
            self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self.reader_thread.start()

            # Get initial output (wait for pytest to run and potentially enter pdb)
            output = self._get_output(timeout=timeout)

            # Build result message
            result = f"Pytest debug session started\nCommand: {cmd}"
            if working_directory:
                result += f"\nWorking directory: {working_directory}"
            result += f"\n\n{output}"
            return result

        except Exception as e:
            self.cleanup()
            return f"Error starting pytest debug session: {str(e)}"

    def execute_command(self, command: str, timeout: float = 5.0) -> str:
        """Execute a pdb command in the active session

        Args:
            command: The pdb command to execute
            timeout: Time to wait without new output before returning (seconds). Default: 5.0
        """
        if self.process is None or self.process.poll() is not None:
            return "Error: No active debugging session. Please start a session first using start_debug tool."

        try:
            # Clear queue
            while not self.output_queue.empty():
                try:
                    self.output_queue.get_nowait()
                except Empty:
                    break

            # Send command
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

            # Get output (wait until no new output for timeout seconds)
            output = self._get_output(timeout=timeout)

            # For quit commands, give the process a moment to exit
            if command.strip() in ["q", "quit", "exit"]:
                time.sleep(0.1)
                # Force cleanup for quit commands
                self.cleanup()
                return output + "\n\n[Debug session has ended]"

            # Check if process ended
            if self.process.poll() is not None:
                self.cleanup()
                return output + "\n\n[Debug session has ended]"

            return output if output else "[Command executed, no output]"

        except Exception as e:
            return f"Error executing command: {str(e)}"

    def _read_output(self):
        """Read output from process in background thread"""
        while self.running and self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    self.output_queue.put(line)
                else:
                    break
            except Exception:
                break

    def _get_output(self, timeout: float = 5.0) -> str:
        """Get accumulated output from queue

        Waits for output and returns when there's no new output for 'timeout' seconds.
        As long as there's new output, it will keep waiting (no total time limit).

        If pdb prompt is detected, returns immediately without waiting for timeout.

        Args:
            timeout: Time to wait without new output before returning (seconds).
                    Default: 5.0 seconds

        Returns:
            Accumulated output as string
        """
        lines = []
        last_output_time = time.time()

        while True:
            try:
                # Use a short timeout to check frequently
                line = self.output_queue.get(timeout=0.1)
                lines.append(line)
                last_output_time = time.time()  # Reset timer on new output

                # Check if we've reached a pdb prompt - if so, return immediately
                current_output = "".join(lines)
                if self._has_pdb_prompt(current_output):
                    # Wait a tiny bit more to catch any trailing output
                    time.sleep(0.05)
                    # Check for any more output
                    while not self.output_queue.empty():
                        try:
                            lines.append(self.output_queue.get_nowait())
                        except Empty:
                            break
                    return "".join(lines).rstrip()

            except Empty:
                # If we have output and no new output for timeout seconds, return
                if lines and (time.time() - last_output_time) >= timeout:
                    break
                # If no output yet, keep waiting (but check timeout)
                if not lines and (time.time() - last_output_time) >= timeout:
                    break
                continue

        return "".join(lines).rstrip()

    def _has_pdb_prompt(self, output: str) -> bool:
        """Check if output indicates pdb is ready for input

        Args:
            output: The output string to check

        Returns:
            True if pdb is ready for input, False otherwise
        """
        if not output:
            return False

        # Check for common pdb ready patterns at the end of output
        output_stripped = output.rstrip()
        lines = output_stripped.split("\n")

        # Pattern 1: Current code line indicator "-> code"
        # This appears when pdb shows current position
        if "\n-> " in output_stripped:
            last_line = lines[-1].strip()
            # Last line should be the code line after "-> "
            if last_line and not last_line.startswith(">"):
                return True

        # Pattern 2: [EOF] marker (when listing code)
        if output_stripped.endswith("[EOF]"):
            return True

        # Pattern 3: Code listing that starts with line numbers
        # Like: "(Pdb)   1  ->  code"
        if "(Pdb)" in output_stripped:
            # Check if it looks like a code listing
            for line in lines[-3:]:  # Check last few lines
                if line.strip() and (
                    "[EOF]" in line
                    or (line.strip()[0].isdigit() if line.strip() else False)
                ):
                    return True

        # Pattern 4: Short output with (Pdb) prefix
        # Like: "(Pdb) 10" or "(Pdb) True" (from print commands)
        # If output is short (1-2 lines) and starts with (Pdb), it's likely complete
        if len(lines) <= 2 and output_stripped.startswith("(Pdb)"):
            return True

        return False

    def cleanup(self):
        """Clean up the debugging session"""
        self.running = False
        if self.process:
            try:
                self.process.stdin.close()
                self.process.stdout.close()
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
        self.reader_thread = None
