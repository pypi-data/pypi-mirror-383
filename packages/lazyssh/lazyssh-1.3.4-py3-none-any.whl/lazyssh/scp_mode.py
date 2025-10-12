"""SCP mode interface for LazySSH using prompt_toolkit"""

import os
import shlex
import subprocess
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.prompt import Confirm, IntPrompt
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .logging_module import get_connection_logger  # noqa: F401
from .logging_module import (
    SCP_LOGGER,
    format_size,
    log_file_transfer,
    log_scp_command,
    update_transfer_stats,
)
from .models import SSHConnection
from .ssh import SSHManager
from .ui import display_error, display_info, display_success


class SCPModeCompleter(Completer):
    """Completer for prompt_toolkit with SCP mode commands"""

    def __init__(self, scp_mode: "SCPMode") -> None:
        self.scp_mode = scp_mode

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        text = document.text
        word_before_cursor = document.get_word_before_cursor()

        # Split the input into words
        try:
            words = shlex.split(text[: document.cursor_position])
        except ValueError:
            words = text[: document.cursor_position].split()

        if not words or (len(words) == 1 and not text.endswith(" ")):
            # Show base commands if at start
            for cmd in self.scp_mode.commands.keys():
                if not word_before_cursor or cmd.startswith(word_before_cursor):
                    yield Completion(cmd, start_position=-len(word_before_cursor))
            return

        command = words[0].lower()

        # Add command-specific completions based on first word
        if command in ["get", "ls", "mget", "tree"] and (len(words) == 1 or len(words) == 2):
            # Always offer completions after typing the command and a space
            if (len(words) == 1 and text.endswith(" ")) or len(words) == 2:
                # If we have an active connection, try to complete remote files
                if self.scp_mode.conn and self.scp_mode.socket_path:
                    try:
                        # Get partial path from what user typed so far
                        partial_path = words[1] if len(words) > 1 else ""
                        if partial_path:
                            base_dir = str(Path(partial_path).parent)
                        else:
                            base_dir = self.scp_mode.current_remote_dir

                        if not base_dir:
                            base_dir = self.scp_mode.current_remote_dir

                        # Get files in the directory
                        result = self.scp_mode._execute_ssh_command(f"ls -a {base_dir}")
                        if result and result.returncode == 0:
                            file_list = result.stdout.strip().split("\n")
                            file_list = [f for f in file_list if f and f not in [".", ".."]]

                            for f in file_list:
                                if not word_before_cursor or f.startswith(word_before_cursor):
                                    yield Completion(f, start_position=-len(word_before_cursor))
                    except Exception:
                        # Silently fail for completions
                        pass

        elif command == "put" and (len(words) == 1 or len(words) == 2):
            # Always offer completions after typing the command and a space
            if (len(words) == 1 and text.endswith(" ")) or len(words) == 2:
                # Complete local files from the upload directory
                try:
                    # Get partial path from what user typed so far
                    partial_path = words[1] if len(words) > 1 else ""
                    if partial_path:
                        base_dir = str(Path(partial_path).parent)
                    else:
                        base_dir = self.scp_mode.local_upload_dir or ""

                    if not base_dir:
                        base_dir = self.scp_mode.local_upload_dir or ""

                    # Get filename part for matching
                    filename_part = Path(partial_path).name if partial_path else ""

                    # List files in the local upload directory
                    for f in os.listdir(base_dir or "."):
                        if not filename_part or f.startswith(filename_part):
                            full_path = str(Path(base_dir) / f) if base_dir else f
                            yield Completion(full_path, start_position=-len(partial_path))
                except Exception:
                    # Silently fail for completions
                    pass

        elif command == "cd" and (len(words) == 1 or len(words) == 2):
            # Always offer completions after typing the command and a space
            if (len(words) == 1 and text.endswith(" ")) or len(words) == 2:
                # Complete remote directories
                if self.scp_mode.conn and self.scp_mode.socket_path:
                    try:
                        # Get partial path from what user typed so far
                        partial_path = words[1] if len(words) > 1 else ""
                        if partial_path:
                            base_dir = str(Path(partial_path).parent)
                        else:
                            base_dir = self.scp_mode.current_remote_dir

                        if not base_dir:
                            base_dir = self.scp_mode.current_remote_dir

                        # Get directories in the base directory
                        result = self.scp_mode._execute_ssh_command(
                            f"find {base_dir} -maxdepth 1 -type d -printf '%f\\n'"
                        )
                        if result and result.returncode == 0:
                            dir_list = result.stdout.strip().split("\n")
                            dir_list = [d for d in dir_list if d and d not in [".", ".."]]

                            for d in dir_list:
                                if not word_before_cursor or d.startswith(word_before_cursor):
                                    yield Completion(d, start_position=-len(word_before_cursor))
                    except Exception:
                        # Silently fail for completions
                        pass

        elif command == "local" and (len(words) == 1 or len(words) == 2 or len(words) == 3):
            # Handle different stages of local command completion
            if len(words) == 1 and text.endswith(" "):
                # After "local " - suggest ONLY download/upload options
                yield Completion("download", start_position=-len(word_before_cursor))
                yield Completion("upload", start_position=-len(word_before_cursor))
                # Don't show directory completions here
            elif len(words) == 2:
                if words[1] in ["download", "upload"] and text.endswith(" "):
                    # After "local download " or "local upload " - complete directories
                    try:
                        # List directories in the current directory
                        for d in os.listdir("."):
                            path_obj = Path(".") / d
                            if path_obj.is_dir():
                                result_path = str(path_obj)
                                yield Completion(result_path, start_position=0)
                    except Exception:
                        # Silently fail for completions
                        pass
                else:
                    # Complete local directories for backward compatibility
                    try:
                        # Get partial path from what user typed so far
                        partial_path = words[1]

                        if partial_path:
                            path_obj = Path(partial_path)
                            base_dir = str(path_obj.parent) if path_obj.name else str(path_obj)
                            dirname_part = path_obj.name
                        else:
                            base_dir = "."
                            dirname_part = ""

                        # List directories in the local directory
                        for d in os.listdir(base_dir or "."):
                            path_obj = Path(base_dir) / d
                            if (
                                not dirname_part or d.startswith(dirname_part)
                            ) and path_obj.is_dir():
                                result_path = str(path_obj) if base_dir else d
                                yield Completion(result_path, start_position=-len(partial_path))
                    except Exception:
                        # Silently fail for completions
                        pass
            elif len(words) == 3 and words[1] in ["download", "upload"] and not text.endswith(" "):
                # Complete directory path for "local download <path>" or "local upload <path>"
                try:
                    # Get partial path from what user typed so far
                    partial_path = words[2]

                    if partial_path:
                        path_obj = Path(partial_path)
                        base_dir = str(path_obj.parent) if path_obj.name else str(path_obj)
                        dirname_part = path_obj.name
                    else:
                        base_dir = "."
                        dirname_part = ""

                    # List directories in the local directory
                    for d in os.listdir(base_dir or "."):
                        dir_path_obj = Path(base_dir) / d
                        if (
                            not dirname_part or d.startswith(dirname_part)
                        ) and dir_path_obj.is_dir():
                            result_path = str(dir_path_obj) if base_dir else d
                            yield Completion(result_path, start_position=-len(partial_path))
                except Exception:
                    # Silently fail for completions
                    pass
        elif command == "lls" and (len(words) == 1 or len(words) == 2):
            # Always offer completions after typing the command and a space
            if (len(words) == 1 and text.endswith(" ")) or len(words) == 2:
                # Complete local directories
                partial_path = words[1] if len(words) > 1 else ""

                if partial_path:
                    path_obj = Path(partial_path)
                    base_dir = str(path_obj.parent) if path_obj.name else str(path_obj)
                    filename_part = path_obj.name
                else:
                    base_dir = "."
                    filename_part = ""

                if not base_dir:
                    base_dir = "."

                try:
                    # List files in the directory
                    files = os.listdir(base_dir)

                    for f in files:
                        if not filename_part or f.startswith(filename_part):
                            # Check if it's a directory and append / if it is
                            file_path_obj = Path(base_dir) / f
                            if file_path_obj.is_dir():
                                f = f + "/"
                            yield Completion(f, start_position=-len(filename_part))
                except (FileNotFoundError, PermissionError):
                    # Silently fail for completions
                    pass

        elif command == "lcd" and (len(words) == 1 or len(words) == 2):
            # Always offer completions after typing the command and a space
            if (len(words) == 1 and text.endswith(" ")) or len(words) == 2:
                # Complete local directories
                try:
                    # Get partial path from what user typed so far
                    partial_path = words[1] if len(words) > 1 else ""

                    if partial_path:
                        path_obj = Path(partial_path)
                        base_dir = str(path_obj.parent)
                        dirname_part = path_obj.name
                    else:
                        base_dir = "."
                        dirname_part = ""

                    # List directories in the local directory
                    for d in os.listdir(base_dir or "."):
                        lcd_path_obj = Path(base_dir) / d
                        if (
                            not dirname_part or d.startswith(dirname_part)
                        ) and lcd_path_obj.is_dir():
                            result_path = str(lcd_path_obj) if base_dir else d
                            yield Completion(result_path, start_position=-len(partial_path))
                except Exception:
                    # Silently fail for completions
                    pass


class SCPMode:
    """SCP mode for file transfers through established SSH connections"""

    def __init__(self, ssh_manager: SSHManager, selected_connection: str | None = None):
        """Initialize SCP mode"""
        self.ssh_manager = ssh_manager
        self.console = Console()

        # State tracking
        self.socket_path: str | None = None
        self.conn: SSHConnection | None = None
        self.connections = ssh_manager.connections

        # Connection name (for logging)
        self.connection_name = selected_connection

        # Stats tracking
        self.download_count = 0
        self.download_bytes = 0
        self.upload_count = 0
        self.upload_bytes = 0

        # Log directory setup
        self.log_dir = Path("/tmp/lazyssh/logs")
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.log_dir.chmod(0o700)  # Secure permissions

        # Set up history file
        self.history_dir = Path.home() / ".lazyssh"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "scp_history"

        # Initialize directories
        self.current_remote_dir = "~"  # Default to user's home dir
        self.local_download_dir: str | None = None  # Set dynamically on connection
        self.local_upload_dir: str | None = None  # Set dynamically on connection

        # Initialize prompt_toolkit components
        self.completer = SCPModeCompleter(self)
        self.session: PromptSession = PromptSession(
            history=FileHistory(str(self.history_file)),
            completer=self.completer,
            complete_while_typing=True,
        )
        self.style = Style.from_dict(
            {
                "prompt": "ansicyan bold",
                "path": "ansigreen",
                "dir1": "ansiyellow",
                "dir2": "ansimagenta",
                "brackets": "ansigreen",
            }
        )

        # Available commands
        self.commands = {
            "get": self.cmd_get,
            "put": self.cmd_put,
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "pwd": self.cmd_pwd,
            "mget": self.cmd_mget,
            "local": self.cmd_local,
            "lls": self.cmd_lls,
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "tree": self.cmd_tree,
            "lcd": self.cmd_lcd,
        }

        # Try to connect to selected connection if provided
        if selected_connection:
            self.socket_path = f"/tmp/{selected_connection}"
            self.connect()

        # Log initialization
        if SCP_LOGGER:
            SCP_LOGGER.debug("SCPMode initialized")

    def connect(self) -> bool:
        """Verify the SSH connection is active via control socket"""
        if not self.socket_path:
            return False

        if self.socket_path not in self.connections:
            display_error(f"SSH connection not found: {self.socket_path}")
            return False

        self.conn = self.connections[self.socket_path]

        # Extract connection name from socket path
        if not self.connection_name:
            self.connection_name = Path(self.socket_path).name

        # Set default directories
        conn_download_dir = self.conn.downloads_dir
        conn_upload_dir = f"/tmp/lazyssh/{self.connection_name}.d/uploads"

        self.local_download_dir = str(conn_download_dir)
        self.local_upload_dir = str(conn_upload_dir)

        # Create upload directory if it doesn't exist
        conn_upload_path = Path(conn_upload_dir)
        if not conn_upload_path.exists():
            try:
                conn_upload_path.mkdir(parents=True, exist_ok=True)
            except OSError:
                display_error(f"Failed to create uploads directory: {conn_upload_dir}")
                return False

        # Get initial remote directory
        try:
            cmd = [
                "ssh",
                "-o",
                f"ControlPath={self.socket_path}",
                f"{self.conn.username}@{self.conn.host}",
                "pwd",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.current_remote_dir = result.stdout.strip()
            else:
                self.current_remote_dir = "~"
        except Exception:
            self.current_remote_dir = "~"

        display_success(f"Connected to {self.conn.host} as {self.conn.username}")
        display_info(f"Local download directory: {self.local_download_dir}")
        display_info(f"Local upload directory: {self.local_upload_dir}")
        display_info(f"Current remote directory: {self.current_remote_dir}")
        if SCP_LOGGER:
            SCP_LOGGER.info(f"SCP mode connected to {self.conn.host} via {self.socket_path}")

        # Create connection-specific logs directory
        conn_log_dir = Path(f"/tmp/lazyssh/{self.connection_name}.d/logs")
        if not conn_log_dir.exists():
            conn_log_dir.mkdir(parents=True, exist_ok=True)
            conn_log_dir.chmod(0o700)

        return True

    def _execute_ssh_command(self, remote_command: str) -> subprocess.CompletedProcess | None:
        """Execute a command on the remote host via SSH and return the result"""
        if not self.conn or not self.connection_name:
            display_error("No active connection")
            return None

        try:
            cmd = [
                "ssh",
                "-o",
                f"ControlPath={self.socket_path}",
                f"{self.conn.username}@{self.conn.host}",
                remote_command,
            ]

            # Log the command execution with connection name
            log_scp_command(self.connection_name, remote_command)

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result
        except Exception as e:
            display_error(f"SSH command error: {str(e)}")
            return None

    def get_prompt_text(self) -> HTML:
        """Get the prompt text with HTML formatting"""
        conn_name = self.connection_name or "none"
        return HTML(
            f"<prompt>scp {conn_name}</prompt>:<path>{self.current_remote_dir}</path>"
            f" <brackets>[</brackets><brackets>↓</brackets><dir1>{self.local_download_dir}</dir1> <brackets>|</brackets> <brackets>↑</brackets><dir2>{self.local_upload_dir}</dir2><brackets>]</brackets><brackets>></brackets> "
        )

    def run(self) -> None:
        """Run the SCP mode interface"""
        # If no connection is selected, prompt for selection
        if not self.connection_name:
            if not self._select_connection():
                return
            # Set socket path after successful connection selection
            self.socket_path = f"/tmp/{self.connection_name}"

        # Connect to the selected SSH session if not already connected
        if not self.conn:
            if not self.connect():
                return

        while True:
            try:
                user_input = self.session.prompt(
                    self.get_prompt_text(),
                    completer=self.completer,
                    style=self.style,
                    complete_while_typing=True,
                )

                # Split the input into command and args
                args = shlex.split(user_input)
                if not args:
                    continue

                cmd = args[0].lower()
                if cmd in self.commands:
                    result = self.commands[cmd](args[1:])
                    if cmd == "exit" and result:
                        break
                else:
                    display_error(f"Unknown command: {cmd}")
                    self.cmd_help([])
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                display_error(f"Error: {str(e)}")

    def _select_connection(self) -> bool:
        """Prompt user to select an SSH connection"""
        connections = []
        connection_map = {}

        # Build a map of connection names to actual connections
        for socket_path, conn in self.connections.items():
            conn_name = Path(socket_path).name
            connections.append(conn_name)
            connection_map[conn_name] = conn

        if not connections:
            display_error("No active SSH connections available")
            display_info("Create an SSH connection first using 'lazyssh' command")
            return False

        display_info("Select an SSH connection for SCP mode:")
        for i, name in enumerate(connections, 1):
            conn = connection_map[name]
            display_info(f"{i}. {name} ({conn.username}@{conn.host})")

        # Use Rich's prompt for the connection selection
        try:
            choice = IntPrompt.ask("Enter selection (number)", default=1)
            if 1 <= choice <= len(connections):
                self.connection_name = connections[choice - 1]
                return True
            else:
                display_error("Invalid selection")
                return False
        except (KeyboardInterrupt, EOFError):
            return False

    def _resolve_remote_path(self, path: str) -> str:
        """Resolve a remote path relative to the current remote directory"""
        if not path:
            return self.current_remote_dir or ""

        # Handle absolute paths as is
        if path.startswith("/"):
            return path

        # Handle paths with ~ for home directory
        if path.startswith("~"):
            # Execute command to expand ~ on the remote server
            result = self._execute_ssh_command(f"echo {path}")
            if result and result.returncode == 0:
                expanded_path = result.stdout.strip()
                return expanded_path if expanded_path else path
            return path

        # Join with current directory
        if self.current_remote_dir:
            return str(Path(self.current_remote_dir) / path)
        return path

    def _resolve_local_path(self, path: str, for_upload: bool = False) -> str:
        """Resolve a local path relative to the local download or upload directory"""
        if not path:
            base_dir = self.local_upload_dir if for_upload else self.local_download_dir
            return base_dir if base_dir else ""
        if Path(path).is_absolute():
            return path

        # Join with local download or upload directory
        base_dir = self.local_upload_dir if for_upload else self.local_download_dir
        if base_dir:
            return str(Path(base_dir) / path)
        return path

    def _get_scp_command(self, source: str, destination: str) -> list[str]:
        """Build the SCP command"""
        return ["scp", "-q", "-o", f"ControlPath={self.socket_path}", source, destination]

    def _get_file_size(self, path: str, is_remote: bool = False) -> int:
        """Get the size of a file in bytes"""
        try:
            if is_remote and self.conn:
                # Get size of remote file
                result = self._execute_ssh_command(f"stat -c %s {path}")
                if result and result.returncode == 0:
                    return int(result.stdout.strip())
                return 0
            else:
                # Get size of local file
                return Path(path).stat().st_size
        except Exception:
            return 0

    def cmd_put(self, args: list[str]) -> None:
        """Upload a file to the remote host"""
        if not self.conn or not self.check_connection():
            display_error("No active connection")
            return

        if len(args) < 1:
            display_error("Usage: put <local_file_path> [remote_file_path]")
            return

        local_path = args[0]

        # Check if the local file exists
        local_file = Path(local_path)
        if not local_file.exists():
            display_error(f"Local file not found: {local_path}")
            return

        # Get the file size before upload
        file_size = local_file.stat().st_size

        # Determine the remote path
        remote_path = args[1] if len(args) > 1 else None

        if not remote_path:
            # Use the filename from the local path
            filename = Path(local_path).name
            remote_path = f"{self.current_remote_dir}/{filename}"

        try:
            # Execute the SCP command
            remote_dest = f"{self.conn.username}@{self.conn.host}:{remote_path}"
            cmd = self._get_scp_command(local_path, remote_dest)

            # Show a progress bar for upload
            display_info(f"Uploading {local_path} to {remote_path}")

            # Start timing the upload
            start_time = time.time()

            # Create a progress bar
            with Progress(
                TextColumn("[bold blue]{task.description}", justify="right"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                TextColumn("[bold green]{task.completed:.2f}/{task.total:.2f} MB", justify="right"),
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
            ) as progress:
                # Convert bytes to MB for display
                file_size_mb = file_size / (1024 * 1024)
                upload_task = progress.add_task(
                    f"[cyan]Uploading {Path(local_path).name}", total=file_size_mb
                )

                # Start the upload process
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                # Since SCP doesn't provide progress feedback, we monitor remote file size
                # We'll poll for completion instead
                while process.poll() is None:
                    # Just update time-based progress as an approximation
                    # Actual progress can't be determined for uploads without server feedback
                    elapsed = time.time() - start_time
                    # Estimate progress based on time and file size
                    # Using a reasonable upload rate estimate (10MB/s)
                    est_progress = min(elapsed * 10, file_size_mb)  # Cap at total size
                    progress.update(upload_task, completed=est_progress)
                    time.sleep(0.1)

                # Process is complete, set to 100%
                progress.update(upload_task, completed=file_size_mb)

                # Get result
                result = process.wait()
                stderr = process.stderr.read() if process.stderr else ""

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            elapsed_str = f"{elapsed_time:.1f} seconds"
            if elapsed_time > 60:
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                elapsed_str = f"{minutes}m {seconds}s"

            if result == 0:
                # Log the file transfer with size
                if self.connection_name:
                    log_file_transfer(
                        connection_name=str(self.connection_name) if self.connection_name else "",
                        source=local_path,
                        destination=remote_path,
                        size=file_size,
                        operation="upload",
                    )
                    # Update transfer stats
                    update_transfer_stats(self.connection_name, 1, file_size)
                display_success(
                    f"Uploaded {local_path} ({format_size(file_size)}) in {elapsed_str}"
                )
            else:
                display_error(f"Upload failed: {stderr}")
        except Exception as e:
            display_error(f"Upload error: {str(e)}")

    def cmd_get(self, args: list[str]) -> None:
        """Download a file from the remote host"""
        if not self.conn or not self.check_connection():
            display_error("No active connection")
            return

        if len(args) < 1:
            display_error("Usage: get <remote_file_path> [local_file_path]")
            return

        remote_path = args[0]

        # If remote path is relative, make it absolute based on current remote dir
        if not remote_path.startswith("/"):
            remote_path = f"{self.current_remote_dir}/{remote_path}"

        # Determine the local path
        local_path = args[1] if len(args) > 1 else None

        if not local_path and self.local_download_dir:
            # Use the filename from the remote path
            filename = Path(remote_path).name
            local_path = str(Path(self.local_download_dir) / filename)
        elif not local_path:
            display_error("Local download directory not set")
            return

        # Create parent directory if it doesn't exist
        local_dir = Path(str(local_path)).parent if local_path else None
        if local_dir and not local_dir.exists():
            try:
                local_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                display_error(f"Failed to create directory {local_dir}: {str(e)}")
                return

        try:
            # Get file size before download to log it properly
            size_cmd = f"stat -c %s '{remote_path}'"
            size_result = self._execute_ssh_command(size_cmd)
            file_size = 0
            if size_result and size_result.returncode == 0:
                file_size = int(size_result.stdout.strip())

            # Execute the SCP command
            remote_source = f"{self.conn.username}@{self.conn.host}:{remote_path}"
            cmd = self._get_scp_command(remote_source, str(local_path))

            # Show a progress bar for download
            display_info(f"Downloading {remote_path} to {local_path}")

            # Start timing the download
            start_time = time.time()

            # Create a progress bar
            with Progress(
                TextColumn("[bold blue]{task.description}", justify="right"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                TextColumn("[bold green]{task.completed:.2f}/{task.total:.2f} MB", justify="right"),
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
            ) as progress:
                # Convert bytes to MB for display
                file_size_mb = file_size / (1024 * 1024)
                download_task = progress.add_task(
                    f"[cyan]Downloading {Path(remote_path).name}", total=file_size_mb
                )

                # Start the download process
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                # Poll the local file size to show progress
                local_size = 0
                while process.poll() is None:
                    local_file_path = Path(str(local_path)) if local_path else None
                    if local_file_path and local_file_path.exists():
                        try:
                            new_size = local_file_path.stat().st_size
                            if new_size > local_size:
                                local_size = new_size
                                # Convert to MB for the progress bar
                                progress.update(download_task, completed=local_size / (1024 * 1024))
                        except (OSError, FileNotFoundError):
                            pass  # Ignore file access errors during download
                    time.sleep(0.1)

                # Process is complete, set to 100% if we know the file size
                if file_size > 0:
                    progress.update(download_task, completed=file_size_mb)
                else:
                    # If we didn't know the file size in advance, get it now
                    try:
                        final_size = (
                            file_size  # Default to file_size if local file can't be accessed
                        )
                        if local_file_path and local_file_path.exists():
                            final_size = local_file_path.stat().st_size
                            progress.update(
                                download_task,
                                completed=final_size / (1024 * 1024),
                                total=final_size / (1024 * 1024),
                            )
                            file_size = final_size  # Update file_size for logging
                    except (OSError, FileNotFoundError):
                        pass

                # Get result
                result = process.wait()
                stderr = process.stderr.read() if process.stderr else ""

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            elapsed_str = f"{elapsed_time:.1f} seconds"
            if elapsed_time > 60:
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                elapsed_str = f"{minutes}m {seconds}s"

            if result == 0:
                # Calculate final file size for display and logging
                final_size = file_size  # Default to file_size if local file can't be accessed
                if local_file_path and local_file_path.exists():
                    final_size = local_file_path.stat().st_size
                    file_size = final_size

                # Log the file transfer
                if self.connection_name:
                    log_file_transfer(
                        connection_name=str(self.connection_name) if self.connection_name else "",
                        source=remote_path,
                        destination=str(local_path) if local_path else "",
                        size=file_size,
                        operation="download",
                    )
                    # Update transfer stats
                    update_transfer_stats(self.connection_name, 1, file_size)

                display_success(
                    f"Downloaded {remote_path} ({format_size(file_size)}) in {elapsed_str}"
                )
            else:
                display_error(f"Download failed: {stderr}")
        except Exception as e:
            display_error(f"Download error: {str(e)}")

    def cmd_ls(self, args: list[str]) -> bool:
        """List contents of a remote directory"""
        path = self.current_remote_dir
        if args:
            path = self._resolve_remote_path(args[0])

        try:
            # Use ls -la command via SSH for detailed listing
            result = self._execute_ssh_command(f"ls -la {path}")

            if not result or result.returncode != 0:
                display_error(
                    f"Error listing directory: {result.stderr if result else 'Unknown error'}"
                )
                return False

            # Format and display the output
            output = result.stdout.strip()
            if not output:
                display_info(f"Directory [bold blue]{path}[/] is empty")
                return True

            display_info(f"Contents of [bold blue]{path}[/]:")

            # Create a Rich table
            table = Table(
                show_header=True, header_style="bold cyan", box=None, padding=(0, 1, 0, 1)
            )

            # Add columns
            table.add_column("Permissions", style="dim")
            table.add_column("Links", justify="right", style="dim")
            table.add_column("Owner")
            table.add_column("Group")
            table.add_column("Size", justify="right")
            table.add_column("Modified")
            table.add_column("Name")

            # Parse ls output and add rows
            lines = output.split("\n")
            for line in lines:
                # Skip total line
                if line.startswith("total "):
                    continue

                # Parse the ls -la output, which follows a standard format
                # Example: -rw-r--r-- 1 username group 12345 Jan 01 12:34 filename
                parts = line.split(maxsplit=8)
                if len(parts) < 9:
                    continue

                perms, links, owner, group, size_str, date1, date2, date3, name = parts

                # Format the size to be human readable
                try:
                    size_bytes = int(size_str)
                    human_size = self._format_file_size(size_bytes)
                except ValueError:
                    human_size = size_str

                # Format the date in a consistent way - attempt to convert to a standard format
                try:
                    # Try to parse the date parts into a consistent format
                    # Handle different date formats from ls
                    date_str = f"{date1} {date2} {date3}"

                    # Parse the date - try different formats
                    date_formats = [
                        "%b %d %Y",  # Jan 01 2023
                        "%b %d %H:%M",  # Jan 01 12:34
                        "%Y-%m-%d %H:%M",  # 2023-01-01 12:34
                    ]

                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = time.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue

                    if parsed_date:
                        # Format in a consistent way
                        date = time.strftime("%b %d %Y %H:%M", parsed_date)
                    else:
                        # Fall back to original if parsing fails
                        date = date_str
                except Exception:
                    # If any error, just use the original
                    date = f"{date1} {date2} {date3}"

                # Color the filename based on type
                name_text = Text(name)
                if perms.startswith("d"):  # Directory
                    name_text.stylize("bold blue")
                elif perms.startswith("l"):  # Symlink
                    name_text.stylize("cyan")
                elif perms.startswith("-") and (
                    "x" in perms[1:4] or "x" in perms[4:7] or "x" in perms[7:10]
                ):  # Executable
                    name_text.stylize("green")

                table.add_row(perms, links, owner, group, human_size, date, name_text)

            # Display the table
            console = Console()
            console.print(table)

            return True
        except Exception as e:
            display_error(f"Error listing directory: {str(e)}")
            return False

    def cmd_cd(self, args: list[str]) -> bool:
        """Change remote directory"""
        if not args:
            display_error("Usage: cd <remote_path>")
            return False

        target_dir = self._resolve_remote_path(args[0])

        try:
            # Check if directory exists and is accessible
            result = self._execute_ssh_command(f"cd {target_dir} && pwd")

            if not result or result.returncode != 0:
                display_error(
                    f"Failed to change directory: {result.stderr if result else 'Directory may not exist'}"
                )
                return False

            # Update current directory
            self.current_remote_dir = result.stdout.strip()
            display_success(f"Changed to directory: {self.current_remote_dir}")
            return True
        except Exception as e:
            display_error(f"Failed to change directory: {str(e)}")
            return False

    def cmd_pwd(self, args: list[str]) -> bool:
        """Print current remote directory"""
        display_info(f"Current remote directory: {self.current_remote_dir}")
        return True

    def cmd_mget(self, args: list[str]) -> bool:
        """Download multiple files from the remote server using wildcards"""
        if not args:
            display_error("Usage: mget <pattern>")
            return False

        if not self.conn:
            display_error("Not connected to an SSH server")
            return False

        pattern = args[0]

        try:
            # Find files matching pattern
            result = self._execute_ssh_command(
                f"find {self.current_remote_dir} -maxdepth 1 -type f -name '{pattern}' -printf '%f\\n'"
            )

            if not result or result.returncode != 0:
                display_error(
                    f"Error finding files: {result.stderr if result else 'Unknown error'}"
                )
                return False

            matched_files = [f for f in result.stdout.strip().split("\n") if f]

            if not matched_files:
                display_error(f"No files match pattern: {pattern}")
                return False

            # Calculate total size of all files
            total_size = 0
            file_sizes = {}

            # Display matched files in a Rich table instead of simple list
            display_info(f"Found {len(matched_files)} matching files:")

            # Create a Rich table for listing the files
            table = Table(
                show_header=True, header_style="bold cyan", box=None, padding=(0, 1, 0, 1)
            )

            # Add columns
            table.add_column("Filename", style="cyan")
            table.add_column("Size", justify="right")

            # Add files to table
            for filename in matched_files:
                # Get file size
                size_result = self._execute_ssh_command(
                    f"stat -c %s {self.current_remote_dir}/{filename}"
                )
                if size_result and size_result.returncode == 0:
                    try:
                        size = int(size_result.stdout.strip())
                        file_sizes[filename] = size
                        total_size += size

                        # Format size in human-readable format
                        human_size = self._format_file_size(size)
                        table.add_row(filename, human_size)
                    except ValueError:
                        table.add_row(filename, "unknown size")
                else:
                    table.add_row(filename, "unknown size")

            # Display the table
            console = Console()
            console.print(table)

            # Format total size in human-readable format
            human_total = self._format_file_size(total_size)
            display_info(f"Total download size: [bold green]{human_total}[/]")

            # Confirm download using Rich's Confirm.ask for a color-coded prompt
            if not Confirm.ask(
                f"Download [bold cyan]{len(matched_files)}[/] files to [bold blue]{self.local_download_dir}[/]?"
            ):
                display_info("Download cancelled")
                return False

            # Ensure download directory exists with proper permissions
            download_dir_path = (
                Path(self.local_download_dir) if self.local_download_dir else Path(".")
            )
            if not download_dir_path.exists():
                download_dir_path.mkdir(parents=True, exist_ok=True)
                download_dir_path.chmod(0o755)

            # Download files with progress tracking
            success_count = 0
            total_downloaded_bytes = 0

            # Start timing the download
            start_time = time.time()

            with Progress(
                TextColumn("[bold blue]{task.description}", justify="right"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                DownloadColumn(),
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
            ) as progress:
                # Create a task for overall progress based on total bytes, not file count
                overall_task = progress.add_task("Overall progress", total=total_size)

                for idx, filename in enumerate(matched_files):
                    remote_file = str(Path(self.current_remote_dir) / filename)
                    local_file = (
                        str(Path(str(self.local_download_dir)) / filename)
                        if self.local_download_dir
                        else filename
                    )
                    file_size = file_sizes.get(filename, 0)

                    try:
                        # Create a task for this file
                        file_task = progress.add_task(
                            f"[cyan]Downloading {filename}", total=file_size
                        )

                        # Get the SCP command
                        remote_path = f"{self.conn.username}@{self.conn.host}:{remote_file}"
                        cmd = self._get_scp_command(remote_path, local_file)

                        # Start the download process
                        process = subprocess.Popen(
                            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                        )

                        # Monitor progress
                        downloaded_file = Path(local_file)
                        last_size = 0
                        while process.poll() is None:
                            if downloaded_file.exists():
                                current_size = downloaded_file.stat().st_size
                                # Update file progress
                                progress.update(file_task, completed=current_size)

                                # Update overall progress with the delta from last check
                                if current_size > last_size:
                                    progress.update(overall_task, advance=current_size - last_size)
                                    last_size = current_size
                            time.sleep(0.1)

                        # Complete the progress bar for this file
                        final_size = file_size
                        if downloaded_file.exists():
                            final_size = downloaded_file.stat().st_size

                        # Update file task to completion
                        progress.update(file_task, completed=final_size)

                        # Update overall progress with any remaining bytes
                        if final_size > last_size:
                            progress.update(overall_task, advance=final_size - last_size)

                        process_result = process.wait()
                        stderr = process.stderr.read() if process.stderr else ""

                        if process_result != 0:
                            display_error(f"Failed to download {filename}: {stderr}")
                        else:
                            success_count += 1
                            # Log each successful file transfer individually
                            log_file_transfer(
                                connection_name=(
                                    str(self.connection_name) if self.connection_name else ""
                                ),
                                source=remote_file,
                                destination=local_file,
                                size=final_size,
                                operation="download",
                            )
                            total_downloaded_bytes += final_size

                    except Exception as e:
                        display_error(f"Failed to download {filename}: {str(e)}")

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            elapsed_str = f"{elapsed_time:.1f} seconds"
            if elapsed_time > 60:
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                elapsed_str = f"{minutes}m {seconds}s"

            if success_count > 0:
                # Update the total transfer stats only after all downloads are complete
                if self.connection_name:
                    update_transfer_stats(
                        str(self.connection_name), success_count, total_downloaded_bytes
                    )

                # Include file size and elapsed time in success message
                display_success(
                    f"Successfully downloaded [bold cyan]{success_count}[/] of [bold cyan]{len(matched_files)}[/] files ([bold green]{self._format_file_size(total_downloaded_bytes)}[/] in [bold]{elapsed_str}[/])"
                )

            return success_count > 0
        except Exception as e:
            display_error(f"Error during mget: {str(e)}")
            return False

    def cmd_local(self, args: list[str]) -> bool:
        """Set or display local download and upload directories"""
        if not args:
            display_info(f"Current local download directory: {self.local_download_dir}")
            display_info(f"Current local upload directory: {self.local_upload_dir}")
            return True

        if len(args) >= 2 and args[0] in ["download", "upload"]:
            # Handle specific directory type
            dir_type = args[0]
            new_path = args[1]

            try:
                # Resolve path (make absolute if needed)
                path_obj = Path(new_path)
                if not path_obj.is_absolute():
                    path_obj = path_obj.absolute()

                new_path = str(path_obj)

                # Create directory if it doesn't exist
                if not path_obj.exists():
                    display_info(f"Local directory does not exist, creating: {new_path}")
                    path_obj.mkdir(parents=True, exist_ok=True)
                    # Ensure proper permissions
                    path_obj.chmod(0o755)
                elif not path_obj.is_dir():
                    display_error(f"Path exists but is not a directory: {new_path}")
                    return False

                # Set the appropriate directory
                if dir_type == "download":
                    self.local_download_dir = new_path
                    display_success(f"Local download directory set to: {new_path}")
                else:  # upload
                    self.local_upload_dir = new_path
                    display_success(f"Local upload directory set to: {new_path}")

                return True
            except Exception as e:
                display_error(f"Failed to set local directory: {str(e)}")
                return False
        else:
            # Legacy behavior - set download directory for backward compatibility
            new_path = args[0]

            try:
                # Resolve path (make absolute if needed)
                path_obj = Path(new_path)
                if not path_obj.is_absolute():
                    path_obj = path_obj.absolute()

                new_path = str(path_obj)

                # Create directory if it doesn't exist
                if not path_obj.exists():
                    display_info(f"Local directory does not exist, creating: {new_path}")
                    path_obj.mkdir(parents=True, exist_ok=True)
                    # Ensure proper permissions
                    path_obj.chmod(0o755)
                elif not path_obj.is_dir():
                    display_error(f"Path exists but is not a directory: {new_path}")
                    return False

                self.local_download_dir = new_path
                display_success(f"Local download directory set to: {new_path}")
                display_info(
                    "Note: Use 'local download <path>' or 'local upload <path>' to set specific directories"
                )
                return True
            except Exception as e:
                display_error(f"Failed to set local directory: {str(e)}")
                return False

    def cmd_help(self, args: list[str]) -> bool:
        """Display help information"""
        if args:
            cmd = args[0].lower()
            if cmd == "put":
                display_info("[bold cyan]\nUpload a file to the remote server:[/bold cyan]")
                display_info(
                    "[yellow]Usage:[/yellow] [cyan]put[/cyan] [yellow]<local_file>[/yellow] [[yellow]<remote_file>[/yellow]]"
                )
                display_info(
                    "If [yellow]<remote_file>[/yellow] is not specified, the file will be uploaded with the same name"
                )
                display_info(
                    "[dim]Local files are read from the upload directory shown in the prompt[/dim]"
                )
                display_info(
                    "[dim]Use tab completion to see available files in the upload directory[/dim]"
                )
            elif cmd == "get":
                display_info("[bold cyan]\nDownload a file from the remote server:[/bold cyan]")
                display_info(
                    "[yellow]Usage:[/yellow] [cyan]get[/cyan] [yellow]<remote_file>[/yellow] [[yellow]<local_file>[/yellow]]"
                )
                display_info(
                    "If [yellow]<local_file>[/yellow] is not specified, the file will be downloaded to the current local directory"
                )
            elif cmd == "ls":
                display_info("[bold cyan]\nList files in a remote directory:[/bold cyan]")
                display_info(
                    "[yellow]Usage:[/yellow] [cyan]ls[/cyan] [[yellow]<remote_path>[/yellow]]"
                )
                display_info(
                    "If [yellow]<remote_path>[/yellow] is not specified, lists the current remote directory"
                )
            elif cmd == "pwd":
                display_info("[bold cyan]\nShow current remote working directory:[/bold cyan]")
                display_info("[yellow]Usage:[/yellow] [cyan]pwd[/cyan]")
            elif cmd == "cd":
                display_info("[bold cyan]\nChange remote working directory:[/bold cyan]")
                display_info(
                    "[yellow]Usage:[/yellow] [cyan]cd[/cyan] [yellow]<remote_path>[/yellow]"
                )
            elif cmd == "local":
                display_info(
                    "[bold cyan]\nSet or display local download and upload directories:[/bold cyan]"
                )
                display_info(
                    "[yellow]Usage:[/yellow] [cyan]local[/cyan] [[yellow]<local_path>[/yellow]]"
                )
                display_info(
                    "If [yellow]<local_path>[/yellow] is not specified, displays both the download and upload directories"
                )
                display_info("[magenta bold]To set a specific directory type:[/magenta bold]")
                display_info(
                    "  [cyan]local download[/cyan] [yellow]<path>[/yellow] - Set the download directory"
                )
                display_info(
                    "  [cyan]local upload[/cyan] [yellow]<path>[/yellow]   - Set the upload directory"
                )
            elif cmd == "lcd":
                display_info("[bold cyan]\nChange local download directory:[/bold cyan]")
                display_info(
                    "[yellow]Usage:[/yellow] [cyan]lcd[/cyan] [yellow]<local_path>[/yellow]"
                )
                display_info("Change the directory where files are downloaded to")
            elif cmd == "exit":
                display_info("[bold cyan]\nExit SCP mode and return to lazyssh prompt:[/bold cyan]")
                display_info("[yellow]Usage:[/yellow] [cyan]exit[/cyan]")
            elif cmd == "lls":
                display_info(
                    "[bold cyan]\nList contents of the local download directory:[/bold cyan]"
                )
                display_info(
                    "[yellow]Usage:[/yellow] [cyan]lls[/cyan] [[yellow]<local_path>[/yellow]]"
                )
                display_info(
                    "If [yellow]<local_path>[/yellow] is not specified, lists the current local download directory"
                )
                display_info("Shows file sizes and directory summary information")
            elif cmd == "tree":
                display_info(
                    "[bold cyan]\nDisplay a tree view of the remote directory structure:[/bold cyan]"
                )
                display_info(
                    "[yellow]Usage:[/yellow] [cyan]tree[/cyan] [[yellow]<remote_path>[/yellow]]"
                )
                display_info(
                    "If [yellow]<remote_path>[/yellow] is not specified, displays the current remote directory"
                )
            else:
                display_error(f"Unknown command: {cmd}")
                self.cmd_help([])
            return True

        display_info("[bold cyan]\nAvailable SCP mode commands:[/bold cyan]")
        display_info("  [cyan]put[/cyan]     - Upload a file to the remote server")
        display_info("  [cyan]get[/cyan]     - Download a file from the remote server")
        display_info("  [cyan]ls[/cyan]      - List files in a remote directory")
        display_info("  [cyan]lls[/cyan]     - List files in the local download directory")
        display_info(
            "  [cyan]tree[/cyan]    - Display a tree view of the remote directory structure"
        )
        display_info("  [cyan]pwd[/cyan]     - Show current remote working directory")
        display_info("  [cyan]cd[/cyan]      - Change remote working directory")
        display_info("  [cyan]lcd[/cyan]     - Change local download directory")
        display_info("  [cyan]local[/cyan]   - Set or display local download directory")
        display_info("  [cyan]exit[/cyan]    - Exit SCP mode")
        display_info(
            "  [cyan]help[/cyan]    - Show this help message or help for a specific command"
        )
        display_info(
            "\n[dim]Use 'help [yellow]<command>[/yellow]' for detailed help on a specific command[/dim]"
        )
        return True

    def cmd_exit(self, args: list[str]) -> bool:
        """Exit SCP mode"""
        return True

    def _format_file_size(self, size_bytes: int) -> str:
        """Format a file size in bytes to a human-readable string"""
        return format_size(size_bytes)

    def cmd_lls(self, args: list[str]) -> bool:
        """List contents of the local download directory with total size and file count"""
        try:
            # Determine which directory to list
            target_dir_path = (
                Path(str(self.local_download_dir)) if self.local_download_dir else Path(".")
            )
            if args:
                # Allow listing other directories relative to the download dir
                path = args[0]
                path_obj = Path(path)
                if path_obj.is_absolute():
                    target_dir_path = path_obj
                else:
                    target_dir_path = (
                        Path(str(self.local_download_dir) if self.local_download_dir else ".")
                        / path
                    )

            # Check if directory exists
            if not target_dir_path.exists() or not target_dir_path.is_dir():
                display_error(f"Directory not found: {target_dir_path}")
                return False

            display_info(f"Contents of [bold blue]{target_dir_path}[/]:")

            # Create a Rich table
            table = Table(
                show_header=True, header_style="bold cyan", box=None, padding=(0, 1, 0, 1)
            )

            # Add columns - removed Type column
            table.add_column("Permissions", style="dim")
            table.add_column("Size", justify="right")
            table.add_column("Modified")
            table.add_column("Name")

            # Get directory contents
            total_size = 0
            file_count = 0
            dir_count = 0

            # List directory contents in a table format
            for item in sorted(target_dir_path.iterdir()):
                # Get file stat info
                stat = item.stat()

                # Format permission bits similar to Unix ls
                mode = stat.st_mode
                perms = ""
                for who in [0o700, 0o70, 0o7]:  # User, group, other
                    perms += "r" if mode & (who >> 2) else "-"
                    perms += "w" if mode & (who >> 1) else "-"
                    perms += "x" if mode & who else "-"

                # Format modification time - more concise format
                mtime = time.strftime("%b %d %Y %H:%M", time.localtime(stat.st_mtime))

                if item.is_dir():
                    dir_count += 1
                    name_text = Text(f"{item.name}/")
                    name_text.stylize("bold blue")
                    size_text = "--"
                    table.add_row(perms, size_text, mtime, name_text)
                else:
                    # Get file size
                    size = item.stat().st_size
                    file_count += 1
                    total_size += size

                    # Format size for display
                    human_size = self._format_file_size(size)

                    # Create name text with styling
                    name_text = Text(item.name)

                    # Colorize based on file type and permissions
                    if item.suffix.lower() in [".py", ".js", ".sh", ".bash", ".zsh"]:
                        name_text.stylize("green")  # Script files
                    elif item.suffix.lower() in [
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".bmp",
                        ".tif",
                        ".tiff",
                    ]:
                        name_text.stylize("magenta")  # Image files
                    elif item.suffix.lower() in [".mp4", ".avi", ".mov", ".mkv", ".wmv"]:
                        name_text.stylize("cyan")  # Video files
                    elif item.suffix.lower() in [".tar", ".gz", ".zip", ".rar", ".7z", ".bz2"]:
                        name_text.stylize("yellow")  # Archive files

                    # Check if executable and style if needed
                    if (mode & 0o100) or (mode & 0o010) or (mode & 0o001):
                        if not name_text.style:
                            name_text.stylize("green")

                    table.add_row(perms, human_size, mtime, name_text)

            # Display the table
            console = Console()
            console.print(table)

            # Show summary footer
            human_total = self._format_file_size(total_size)
            console.print(
                f"\nTotal: [bold cyan]{file_count}[/] files, [bold cyan]{dir_count}[/] directories, [bold green]{human_total}[/] total size"
            )

            return True

        except Exception as e:
            display_error(f"Error listing directory: {str(e)}")
            return False

    def cmd_tree(self, args: list[str]) -> bool:
        """Display a tree view of the remote directory structure"""
        try:
            # Determine which remote directory to show
            if args:
                remote_path = self._resolve_remote_path(args[0])
            else:
                remote_path = self.current_remote_dir

            # First check if the path exists and is a directory
            check_cmd = f"[ -d {shlex.quote(remote_path)} ] && echo 'DIR_EXISTS' || echo 'NOT_DIR'"
            result = self._execute_ssh_command(check_cmd)
            if not result or result.returncode != 0 or "NOT_DIR" in result.stdout:
                display_error(f"Remote path is not a directory: {remote_path}")
                return False

            # Get listing of files recursively with find, including file type information
            # The format string will give us: <type><path> where type is 'd' for directory, 'f' for file
            find_cmd = f"""find {shlex.quote(remote_path)} \\( -type f -printf "f%p\\n" , -type d -printf "d%p\\n" \\) | sort"""
            result = self._execute_ssh_command(find_cmd)

            if not result or result.returncode != 0:
                display_error(
                    f"Failed to list directory contents: {result.stderr if result else 'Unknown error'}"
                )
                return False

            # Create the root tree node
            tree = Tree(f"[bold cyan]{remote_path}[/]")
            path_to_node = {remote_path: tree}

            # Track statistics
            file_count = 0
            dir_count = 1  # Start with 1 for the root directory

            # Process each entry from the find results, which already includes type information
            for line in result.stdout.strip().split("\n"):
                if not line or len(line) <= 1:
                    continue

                # Extract type and path
                entry_type = line[0]
                path = line[1:]

                # Skip the root path itself
                if path == remote_path:
                    continue

                # Determine the parent path
                parent_path = str(Path(path).parent)

                # Skip if parent not found (shouldn't happen with sorted find output)
                if parent_path not in path_to_node:
                    continue

                # Get the parent node
                parent_node = path_to_node[parent_path]

                # Create a node for this path
                filename = Path(path).name

                if entry_type == "d":  # Directory
                    dir_count += 1
                    node = parent_node.add(f"[bold blue]{filename}/[/]")
                    path_to_node[path] = node
                else:  # File
                    file_count += 1
                    # Style based on file extension
                    if any(
                        filename.endswith(ext) for ext in [".py", ".js", ".sh", ".bash", ".zsh"]
                    ):
                        node = parent_node.add(f"[green]{filename}[/]")
                    elif any(
                        filename.endswith(ext)
                        for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff"]
                    ):
                        node = parent_node.add(f"[magenta]{filename}[/]")
                    elif any(
                        filename.endswith(ext) for ext in [".mp4", ".avi", ".mov", ".mkv", ".wmv"]
                    ):
                        node = parent_node.add(f"[cyan]{filename}[/]")
                    elif any(
                        filename.endswith(ext)
                        for ext in [".tar", ".gz", ".zip", ".rar", ".7z", ".bz2"]
                    ):
                        node = parent_node.add(f"[yellow]{filename}[/]")
                    else:
                        node = parent_node.add(filename)

            # Display the tree
            console = Console()
            console.print(tree)
            console.print(
                f"\nTotal: [bold cyan]{file_count}[/] files, [bold cyan]{dir_count}[/] directories"
            )

            return True

        except Exception as e:
            display_error(f"Error displaying directory tree: {str(e)}")
            return False

    def cmd_lcd(self, args: list[str]) -> bool:
        """Change local download directory"""
        if not args:
            display_error("Usage: lcd <local_path>")
            return False

        try:
            # Resolve path (make absolute if needed)
            path = args[0]
            path_obj = Path(path)
            if not path_obj.is_absolute():
                path_obj = path_obj.absolute()

            new_path = str(path_obj)

            # Create directory if it doesn't exist
            if not path_obj.exists():
                display_info(f"Local directory does not exist, creating: {new_path}")
                path_obj.mkdir(parents=True, exist_ok=True)
                # Ensure proper permissions
                path_obj.chmod(0o755)
            elif not path_obj.is_dir():
                display_error(f"Path exists but is not a directory: {new_path}")
                return False

            # Set the local download directory
            self.local_download_dir = new_path
            display_success(f"Local download directory set to: {new_path}")
            return True
        except Exception as e:
            display_error(f"Failed to change local directory: {str(e)}")
            return False

    def check_connection(self) -> bool:
        """Check if the SSH connection is still active"""
        if not self.socket_path or not self.conn:
            return False

        # Check if the socket file exists
        if not Path(self.socket_path).exists():
            return False

        # Try a simple command to check connection
        try:
            cmd = [
                "ssh",
                "-o",
                f"ControlPath={self.socket_path}",
                f"{self.conn.username}@{self.conn.host}",
                "echo connected",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except Exception:
            return False
