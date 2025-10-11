"""Command mode interface for LazySSH using prompt_toolkit"""

import os
import shlex
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from .logging_module import (  # noqa: F401
    APP_LOGGER,
    CMD_LOGGER,
    DEBUG_MODE,
    log_ssh_command,
    set_debug_mode,
)
from .models import SSHConnection
from .scp_mode import SCPMode
from .ssh import SSHManager
from .ui import (
    display_error,
    display_info,
    display_ssh_status,
    display_success,
    display_tunnels,
    display_warning,
)


class LazySSHCompleter(Completer):
    """Completer for prompt_toolkit with LazySSH commands"""

    def __init__(self, command_mode: "CommandMode") -> None:
        self.command_mode = command_mode

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
            for cmd in self.command_mode.commands.keys():
                if not word_before_cursor or cmd.startswith(word_before_cursor):
                    yield Completion(cmd, start_position=-len(word_before_cursor))
            return

        command = words[0].lower()

        if command == "lazyssh":
            # Get used arguments and their positions
            used_args: dict[str, int] = {}
            expecting_value = False
            last_arg: str | None = None

            for i, word in enumerate(words[1:], 1):  # Start from 1 to skip the command
                if expecting_value and last_arg is not None:
                    # This word is a value for the previous argument
                    used_args[last_arg] = i
                    expecting_value = False
                    last_arg = None
                elif word.startswith("-"):
                    # This is an argument
                    if word in ["-proxy", "-no-term"]:
                        # -proxy and -no-term don't need a value
                        used_args[word] = i
                    else:
                        # Other arguments expect a value
                        expecting_value = True
                        last_arg = word
                else:
                    i += 1

            # Available arguments for lazyssh
            all_args = {
                "-ip",
                "-port",
                "-user",
                "-socket",
                "-proxy",
                "-ssh-key",
                "-shell",
                "-no-term",
            }
            remaining_args = all_args - set(used_args.keys())

            # Separate required and optional parameters
            required_args = ["-ip", "-port", "-user", "-socket"]
            optional_args = ["-proxy", "-ssh-key", "-shell", "-no-term"]

            # Check which required args are still needed
            required_remaining = [arg for arg in required_args if arg in remaining_args]
            optional_remaining = [arg for arg in optional_args if arg in remaining_args]

            # If we're expecting a value for an argument, don't suggest new arguments
            if expecting_value:
                return

            # If the last word is a partial argument, complete it
            if words[-1].startswith("-") and not text.endswith(" "):
                # Complete partial argument based on what the user has typed so far
                partial_arg = words[-1]

                # First prioritize required arguments
                for arg in required_remaining:
                    if arg.startswith(partial_arg):
                        yield Completion(arg, start_position=-len(partial_arg))

                # Then suggest optional arguments if all required ones are used
                if not required_remaining:
                    for arg in optional_remaining:
                        if arg.startswith(partial_arg):
                            yield Completion(arg, start_position=-len(partial_arg))

            # Otherwise suggest next argument if we're not in the middle of entering a value
            elif text.endswith(" ") and not expecting_value:
                # If we still have required arguments, suggest them first
                if required_remaining:
                    # Suggest the first remaining required argument
                    yield Completion(required_remaining[0], start_position=-len(word_before_cursor))
                # If all required arguments are provided, suggest all remaining optional arguments
                elif optional_remaining:
                    # Suggest all remaining optional arguments
                    for arg in optional_remaining:
                        yield Completion(arg, start_position=-len(word_before_cursor))

        elif command == "tunc":
            # For tunc command, we expect a specific sequence of arguments:
            # 1. SSH connection name
            # 2. Tunnel type (l/r)
            # 3. Local port
            # 4. Remote host
            # 5. Remote port

            # Determine which argument we're currently expecting
            arg_position = (
                len(words) - 1
            )  # -1 because we're 0-indexed and first word is the command

            # If we're at the end of a word, we're expecting the next argument
            if text.endswith(" "):
                arg_position += 1

            if arg_position == 1:  # First argument: SSH connection name
                # Show available connections
                for conn_name in self.command_mode._get_connection_completions():
                    if not word_before_cursor or conn_name.startswith(word_before_cursor):
                        yield Completion(conn_name, start_position=-len(word_before_cursor))
            elif arg_position == 2:  # Second argument: Tunnel type (l/r)
                # Suggest tunnel type
                for type_option in ["l", "r"]:
                    if not word_before_cursor or type_option.startswith(word_before_cursor):
                        yield Completion(type_option, start_position=-len(word_before_cursor))
            # For other positions (local port, remote host, remote port), no completions provided

        elif command == "tund":
            # For tund command, we only expect one argument: the tunnel ID
            arg_position = len(words) - 1

            # If we're at the end of a word, we're expecting the next argument
            if text.endswith(" ") or (len(words) == 2 and arg_position == 1):
                # Show available tunnel IDs
                for socket_path, conn in self.command_mode.ssh_manager.connections.items():
                    for tunnel in conn.tunnels:
                        if not word_before_cursor or tunnel.id.startswith(word_before_cursor):
                            yield Completion(tunnel.id, start_position=-len(word_before_cursor))

        elif command == "terminal" or command == "close":
            # For terminal and close commands, we only expect one argument: the SSH connection name
            arg_position = len(words) - 1

            # Only show completions if we're at the exact position to enter the connection name
            # and not if we've already typed something after the command
            if (len(words) == 1 and text.endswith(" ")) or (
                len(words) == 2 and not text.endswith(" ")
            ):
                # Show available connections
                for conn_name in self.command_mode._get_connection_completions():
                    if not word_before_cursor or conn_name.startswith(word_before_cursor):
                        yield Completion(conn_name, start_position=-len(word_before_cursor))

        elif command == "help":
            # For help command, we only expect one optional argument: the command to get help for
            arg_position = len(words) - 1

            # If we're at the end of a word, we're expecting the next argument
            # Or if we've just typed the command and a space, show completions
            if text.endswith(" ") or (len(words) == 2 and arg_position == 1):
                # Show available commands for help
                for cmd in self.command_mode.commands.keys():
                    if not word_before_cursor or cmd.startswith(word_before_cursor):
                        yield Completion(cmd, start_position=-len(word_before_cursor))

        # Handle completion for close command
        elif command == "close" and len(words) == 2:
            connections = self.command_mode._get_connection_completions()
            for conn_name in connections:
                if conn_name.startswith(word_before_cursor):
                    yield Completion(conn_name, start_position=-len(word_before_cursor))

        # Handle completion for scp command
        elif command == "scp":
            # Only suggest connection names if we either:
            # 1. Just typed "scp " and need the first connection name
            # 2. Are in the middle of typing the first connection name
            # Don't suggest anything if we already have a complete connection name
            if (len(words) == 1 and text.endswith(" ")) or (
                len(words) == 2 and not text.endswith(" ")
            ):
                connections = self.command_mode._get_connection_completions()
                for conn_name in connections:
                    if not word_before_cursor or conn_name.startswith(word_before_cursor):
                        yield Completion(conn_name, start_position=-len(word_before_cursor))


class CommandMode:
    def __init__(self, ssh_manager: SSHManager) -> None:
        """Initialize Command Mode interface"""
        # Initialize the SSH Manager
        self.ssh_manager = ssh_manager

        # Define available commands
        self.commands = {
            "connect": self.cmd_lazyssh,  # Alias for lazyssh
            "list": self.cmd_list,
            "lazyssh": self.cmd_lazyssh,
            "help": self.cmd_help,
            "terminal": self.cmd_terminal,
            "debug": self.cmd_debug,
            "scp": self.cmd_scp,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "tunc": self.cmd_tunc,
            "tund": self.cmd_tund,
            "close": self.cmd_close,
            "clear": self.cmd_clear,
            "mode": self.cmd_mode,
        }

        # Initialize history
        self.history_dir = Path.home() / ".lazyssh"
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "command_history"

        # Log initialization
        if CMD_LOGGER:
            CMD_LOGGER.debug("CommandMode initialized")

    def _get_connection_completions(self) -> list[str]:
        """Get list of connection names for completion"""
        conn_completions = []
        for socket_path in self.ssh_manager.connections:
            conn_name = Path(socket_path).name
            conn_completions.append(conn_name)
        return conn_completions

    def get_prompt_text(self) -> HTML:
        """Get the prompt text with HTML formatting"""
        return HTML("<prompt>lazyssh></prompt> ")

    def show_status(self) -> None:
        """Display current connections and tunnels"""
        if self.ssh_manager.connections:
            display_ssh_status(self.ssh_manager.connections)
            for socket_path, conn in self.ssh_manager.connections.items():
                if conn.tunnels:
                    display_tunnels(socket_path, conn)

    def run(self) -> str | None:
        """Run the command mode interface"""
        # Create the session
        try:
            session: PromptSession = PromptSession(
                history=FileHistory(str(self.history_file)),
                completer=LazySSHCompleter(self),
                style=Style.from_dict(
                    {
                        "prompt": "ansicyan bold",
                    }
                ),
            )

            if CMD_LOGGER:
                CMD_LOGGER.info("Starting command mode interface")

            # Display the banner and help
            # self.show_available_commands()  # Remove this line to prevent auto-showing commands

            # Main loop
            while True:
                try:
                    # Get user input
                    text = session.prompt(lambda: self.get_prompt_text())

                    # Skip if empty
                    if not text.strip():
                        continue

                    # Parse the command and arguments
                    try:
                        parts = shlex.split(text)
                    except ValueError as e:
                        display_error(f"Invalid command syntax: {e}")
                        if CMD_LOGGER:
                            CMD_LOGGER.error(f"Invalid command syntax: {e}")
                        continue

                    # Get the command and arguments
                    cmd = parts[0].lower() if parts else ""
                    args = parts[1:] if len(parts) > 1 else []

                    # Check if the command exists
                    if cmd not in self.commands:
                        display_error(f"Unknown command: {cmd}")
                        display_info("Type 'help' to see available commands")
                        if CMD_LOGGER:
                            CMD_LOGGER.warning(f"Unknown command attempted: {cmd}")
                        continue

                    # Log the command
                    if CMD_LOGGER:
                        CMD_LOGGER.info(f"Executing command: {cmd} {' '.join(args)}")

                    # Execute the command
                    result = self.commands[cmd](args)

                    # Handle the result
                    if result == "mode":
                        # Special case for switching modes
                        if CMD_LOGGER:
                            CMD_LOGGER.info("Switching to prompt mode")
                        return "mode"

                    elif result:
                        # Success
                        if not cmd == "list":  # Don't show status after list command
                            self.show_status()
                    # else handled by the command method

                except (KeyboardInterrupt, EOFError):
                    # Handle Ctrl+C and Ctrl+D
                    if CMD_LOGGER:
                        CMD_LOGGER.info("User interrupted command mode (Ctrl+C or Ctrl+D)")
                    break

        except Exception as e:
            display_error(f"Error in command mode: {str(e)}")
            if CMD_LOGGER:
                CMD_LOGGER.exception(f"Unhandled error in command mode: {str(e)}")
            return None

        return None

    def show_available_commands(self) -> None:
        """Show available commands when user enters an unknown command"""
        display_info("Available commands:")
        for cmd in sorted(self.commands.keys()):
            display_info(f"  {cmd}")

        display_info("  exit    : Exit lazyssh")
        display_info("  quit    : Alias for exit")
        display_info("  scp     : Enter SCP mode for file transfers")

    # Command implementations
    def cmd_lazyssh(self, args: list[str]) -> bool:
        """Handle lazyssh command for creating new connections"""
        try:
            # Parse arguments into dictionary
            params = {}
            i = 0
            while i < len(args):
                if args[i].startswith("-"):
                    param_name = args[i][1:]  # Remove the dash

                    # Handle flag parameters that don't need a value
                    if param_name == "proxy" or param_name == "no-term":
                        if i + 1 < len(args) and not args[i + 1].startswith("-"):
                            # If there's a value after the flag, use it
                            params[param_name] = args[i + 1]
                            i += 2
                        else:
                            # Otherwise, just set it to True to indicate it's present
                            params[param_name] = "true"  # Use string "true" instead of boolean
                            i += 1
                    elif i + 1 < len(args):
                        params[param_name] = args[i + 1]
                        i += 2
                    else:
                        raise ValueError(f"Missing value for argument {args[i]}")
                else:
                    i += 1

            # Check required parameters
            required = ["ip", "port", "user", "socket"]
            missing = [f"-{param}" for param in required if param not in params]
            if missing:
                display_error(f"Missing required parameters: {', '.join(missing)}")
                display_info(
                    "Usage: lazyssh -ip <ip> -port <port> -user <username> -socket <n> "
                    "[-proxy [port]] [-ssh-key <identity_file>] [-shell <shell>] [-no-term]"
                )
                if CMD_LOGGER:
                    CMD_LOGGER.error(f"Missing required parameters: {', '.join(missing)}")
                return False

            # Check if the socket name already exists
            socket_path = f"/tmp/{params['socket']}"
            if socket_path in self.ssh_manager.connections:
                display_warning(f"Socket name '{params['socket']}' is already in use.")
                # Use Rich's Confirm.ask for a color-coded prompt (same as prompt mode)
                from rich.prompt import Confirm

                if not Confirm.ask("Do you want to use a different name?", default=True):
                    display_info("Proceeding with the existing socket name.")
                else:
                    new_socket = input("Enter a new socket name: ")
                    if not new_socket:
                        display_error("Socket name cannot be empty.")
                        return False
                    params["socket"] = new_socket
                    socket_path = f"/tmp/{params['socket']}"

            # Create the connection object
            conn = SSHConnection(
                host=params["ip"],
                port=int(params["port"]),
                username=params["user"],
                socket_path=socket_path,
            )

            # Set identity file if provided
            if "ssh-key" in params:
                conn.identity_file = params["ssh-key"]

            # Set shell if provided
            if "shell" in params:
                conn.shell = params["shell"]

            # Set no-term flag if provided
            if "no-term" in params:
                conn.no_term = True

            # Handle dynamic proxy port if specified
            if "proxy" in params:
                if params["proxy"] == "true":
                    # If -proxy was specified without a value, use a default port
                    conn.dynamic_port = 9050
                    display_info(f"Using default dynamic proxy port: {conn.dynamic_port}")
                else:
                    # Otherwise use the specified port
                    try:
                        conn.dynamic_port = int(params["proxy"])
                    except ValueError:
                        display_error("Proxy port must be a number")
                        if CMD_LOGGER:
                            CMD_LOGGER.error(f"Invalid proxy port: {params['proxy']}")
                        return False

            # Log connection attempt
            if CMD_LOGGER:
                CMD_LOGGER.info(
                    f"Creating SSH connection: {conn.username}@{conn.host}:{conn.port} "
                    f"(socket: {params['socket']})"
                )

            # Create the connection
            if self.ssh_manager.create_connection(conn):
                display_success(f"Connection '{params['socket']}' established")
                if conn.dynamic_port:
                    display_success(f"Dynamic proxy created on port {conn.dynamic_port}")
                return True
            return False
        except ValueError as e:
            display_error(str(e))
            if CMD_LOGGER:
                CMD_LOGGER.error(f"Error in lazyssh command: {str(e)}")
            return False

    def cmd_tunc(self, args: list[str]) -> bool:
        """Handle tunnel command for creating tunnels"""
        if len(args) != 5:
            display_error("Usage: tunc <ssh_id> <l|r> <local_port> <remote_host> <remote_port>")
            display_info("Example: tunc ubuntu l 8080 localhost 80")
            return False

        ssh_id, tunnel_type, local_port, remote_host, remote_port = args
        socket_path = f"/tmp/{ssh_id}"

        try:
            local_port_int = int(local_port)
            remote_port_int = int(remote_port)
            is_reverse = tunnel_type.lower() == "r"

            # Build the command for display
            if is_reverse:
                tunnel_args = f"-O forward -R {local_port}:{remote_host}:{remote_port}"
                tunnel_type_str = "reverse"
            else:
                tunnel_args = f"-O forward -L {local_port}:{remote_host}:{remote_port}"
                tunnel_type_str = "forward"

            cmd = f"ssh -S {socket_path} {tunnel_args} dummy"

            # Display the command that will be executed
            display_info("The following SSH command will be executed:")
            display_info(cmd)

            if self.ssh_manager.create_tunnel(
                socket_path, local_port_int, remote_host, remote_port_int, is_reverse
            ):
                display_success(
                    f"{tunnel_type_str.capitalize()} tunnel created: "
                    f"{local_port} -> {remote_host}:{remote_port}"
                )
                return True
            return False
        except ValueError:
            display_error("Port numbers must be integers")
            return False

    def cmd_tund(self, args: list[str]) -> bool:
        """Handle tunnel delete command for removing tunnels"""
        if len(args) != 1:
            display_error("Usage: tund <tunnel_id>")
            display_info("Example: tund 1")
            return False

        tunnel_id = args[0]

        # Find the connection that has this tunnel
        for socket_path, conn in self.ssh_manager.connections.items():
            for tunnel in conn.tunnels:
                if tunnel.id == tunnel_id:
                    # Build the command for display
                    if tunnel.type == "reverse":
                        tunnel_args = (
                            f"-O cancel -R {tunnel.local_port}:"
                            f"{tunnel.remote_host}:{tunnel.remote_port}"
                        )
                    else:
                        tunnel_args = (
                            f"-O cancel -L {tunnel.local_port}:"
                            f"{tunnel.remote_host}:{tunnel.remote_port}"
                        )

                    cmd = f"ssh -S {socket_path} {tunnel_args} dummy"

                    # Display the command that will be executed
                    display_info("The following SSH command will be executed:")
                    display_info(cmd)

                    if self.ssh_manager.close_tunnel(socket_path, tunnel_id):
                        display_success(f"Tunnel {tunnel_id} closed")
                        return True
                    return False

        display_error(f"Tunnel with ID {tunnel_id} not found")
        return False

    def cmd_list(self, args: list[str]) -> bool:
        """Handle list command for showing connections"""
        if not self.ssh_manager.connections:
            display_info("No active connections")
            return True

        # Connections are already shown by show_status() before each prompt
        return True

    def cmd_help(self, args: list[str]) -> bool:
        """Handle help command"""
        if not args:
            display_info("[bold cyan]\nLazySSH Command Mode - Available Commands:[/bold cyan]\n")
            display_info("[magenta bold]SSH Connection:[/magenta bold]")
            display_info(
                "  [cyan]lazyssh[/cyan] -ip [yellow]<ip>[/yellow] -port [yellow]<port>[/yellow] -user [yellow]<username>[/yellow] -socket [yellow]<n>[/yellow] "
                "[-proxy [yellow]<port>[/yellow]] [-ssh-key [yellow]<path>[/yellow]] [-shell [yellow]<shell>[/yellow]] [-no-term]"
            )
            display_info("  [cyan]close[/cyan] [yellow]<ssh_id>[/yellow]")
            display_info(
                "  [dim]Example:[/dim] [green]lazyssh -ip 192.168.10.50 -port 22 -user ubuntu -socket ubuntu[/green]"
            )
            display_info(
                "  [dim]Example:[/dim] [green]lazyssh -ip 192.168.10.50 -port 22 -user ubuntu -socket ubuntu -proxy 8080 -shell /bin/sh[/green]"
            )
            display_info("  [dim]Example:[/dim] [green]close ubuntu[/green]\n")

            display_info("[magenta bold]Tunnel Management:[/magenta bold]")
            display_info(
                "  [cyan]tunc[/cyan] [yellow]<ssh_id>[/yellow] [yellow]<l|r>[/yellow] [yellow]<local_port>[/yellow] [yellow]<remote_host>[/yellow] [yellow]<remote_port>[/yellow]"
            )
            display_info(
                "  [dim]Example (forward):[/dim] [green]tunc ubuntu l 8080 localhost 80[/green]"
            )
            display_info(
                "  [dim]Example (reverse):[/dim] [green]tunc ubuntu r 3000 127.0.0.1 3000[/green]\n"
            )

            display_info("  [cyan]tund[/cyan] [yellow]<tunnel_id>[/yellow]")
            display_info("  [dim]Example:[/dim] [green]tund 1[/green]\n")

            display_info("[magenta bold]Terminal:[/magenta bold]")
            display_info("  [cyan]terminal[/cyan] [yellow]<ssh_id>[/yellow]")
            display_info("  [dim]Example:[/dim] [green]terminal ubuntu[/green]\n")

            display_info("[magenta bold]File Transfer:[/magenta bold]")
            display_info("  [cyan]scp[/cyan] [[yellow]<ssh_id>[/yellow]]")
            display_info("  [dim]Example:[/dim] [green]scp ubuntu[/green]\n")

            display_info("[magenta bold]System Commands:[/magenta bold]")
            display_info("  [cyan]list[/cyan]    - Show all connections and tunnels")
            display_info("  [cyan]mode[/cyan]    - Switch mode (command/prompt)")
            display_info("  [cyan]debug[/cyan]   - Toggle debug logging to console")
            display_info("  [cyan]help[/cyan]    - Show this help")
            display_info("  [cyan]exit[/cyan]    - Exit the program")
            return True

        cmd = args[0]
        if cmd == "lazyssh":
            display_info("[bold cyan]\nCreate new SSH connection:[/bold cyan]")
            display_info(
                "[yellow]Usage:[/yellow] [cyan]lazyssh[/cyan] -ip [yellow]<ip>[/yellow] -port [yellow]<port>[/yellow] -user [yellow]<username>[/yellow] -socket [yellow]<n>[/yellow] "
                "[-proxy [port]] [-ssh-key [yellow]<identity_file>[/yellow]] [-shell [yellow]<shell>[/yellow]] [-no-term]"
            )
            display_info("[magenta bold]Required parameters:[/magenta bold]")
            display_info("  [cyan]-ip[/cyan]     : IP address or hostname of the SSH server")
            display_info("  [cyan]-port[/cyan]   : SSH port number")
            display_info("  [cyan]-user[/cyan]   : SSH username")
            display_info("  [cyan]-socket[/cyan] : Name for the connection (used as identifier)")
            display_info("[magenta bold]Optional parameters:[/magenta bold]")
            display_info(
                "  [cyan]-proxy[/cyan]  : Create a dynamic SOCKS proxy (default port: 9050)"
            )
            display_info("  [cyan]-ssh-key[/cyan]: Path to an SSH identity file")
            display_info("  [cyan]-shell[/cyan]  : Specify the shell to use (e.g., /bin/sh)")
            display_info("  [cyan]-no-term[/cyan]: Do not automatically open a terminal")
            display_info("\n[magenta bold]Examples:[/magenta bold]")
            display_info(
                "  [green]lazyssh -ip 192.168.10.50 -port 22 -user ubuntu -socket ubuntu[/green]"
            )
            display_info(
                "  [green]lazyssh -ip 192.168.10.50 -port 22 -user ubuntu -socket ubuntu -proxy[/green]"
            )
            display_info(
                "  [green]lazyssh -ip 192.168.10.50 -port 22 -user ubuntu -socket ubuntu -proxy 8080[/green]"
            )
            display_info(
                "  [green]lazyssh -ip 192.168.10.50 -port 22 -user ubuntu -socket ubuntu -shell /bin/sh[/green]"
            )
            display_info(
                "  [green]lazyssh -ip 192.168.10.50 -port 22 -user ubuntu -socket ubuntu -shell /bin/sh -no-term[/green]"
            )
        elif cmd == "tunc":
            display_info("[bold cyan]\nCreate a new tunnel:[/bold cyan]")
            display_info(
                "[yellow]Usage:[/yellow] [cyan]tunc[/cyan] [yellow]<ssh_id>[/yellow] [yellow]<l|r>[/yellow] [yellow]<local_port>[/yellow] [yellow]<remote_host>[/yellow] [yellow]<remote_port>[/yellow]"
            )
            display_info("[magenta bold]Parameters:[/magenta bold]")
            display_info("  [cyan]ssh_id[/cyan]      : The identifier of the SSH connection")
            display_info(
                "  [cyan]l|r[/cyan]         : 'l' for local (forward) tunnel, 'r' for remote (reverse) tunnel"
            )
            display_info("  [cyan]local_port[/cyan]  : The local port to use for the tunnel")
            display_info("  [cyan]remote_host[/cyan] : The remote host to connect to")
            display_info("  [cyan]remote_port[/cyan] : The remote port to connect to")
            display_info("\n[magenta bold]Examples:[/magenta bold]")
            display_info(
                "  [green]tunc ubuntu l 8080 localhost 80[/green]    [dim]# Forward local port 8080 to "
                "localhost:80 on the remote server[/dim]"
            )
            display_info(
                "  [green]tunc ubuntu r 3000 127.0.0.1 3000[/green]  [dim]# Reverse tunnel from remote port 3000 "
                "to local 127.0.0.1:3000[/dim]"
            )
        elif cmd == "tund":
            display_info("[bold cyan]\nDelete a tunnel:[/bold cyan]")
            display_info("[yellow]Usage:[/yellow] [cyan]tund[/cyan] [yellow]<tunnel_id>[/yellow]")
            display_info("[magenta bold]Parameters:[/magenta bold]")
            display_info(
                "  [cyan]tunnel_id[/cyan] : The ID of the tunnel to delete (shown in the list command)"
            )
            display_info("\n[magenta bold]Example:[/magenta bold]")
            display_info("  [green]tund 1[/green]")
        elif cmd == "terminal":
            display_info("[bold cyan]\nOpen a terminal for an SSH connection:[/bold cyan]")
            display_info("[yellow]Usage:[/yellow] [cyan]terminal[/cyan] [yellow]<ssh_id>[/yellow]")
            display_info("[magenta bold]Parameters:[/magenta bold]")
            display_info("  [cyan]ssh_id[/cyan] : The identifier of the SSH connection")
            display_info("\n[magenta bold]Example:[/magenta bold]")
            display_info("  [green]terminal ubuntu[/green]")
        elif cmd == "mode":
            display_info("[bold cyan]\nSwitch between command and interactive modes:[/bold cyan]")
            display_info("[yellow]Usage:[/yellow] [cyan]mode[/cyan]")
        elif cmd == "clear":
            display_info("[bold cyan]\nClear the terminal screen:[/bold cyan]")
            display_info("[yellow]Usage:[/yellow] [cyan]clear[/cyan]")
        elif cmd == "scp":
            display_info("[bold cyan]\nEnter SCP mode for file transfers:[/bold cyan]")
            display_info(
                "[yellow]Usage:[/yellow] [cyan]scp[/cyan] [[yellow]<connection_name>[/yellow]]"
            )
            display_info("[magenta bold]Parameters:[/magenta bold]")
            display_info(
                "  [cyan]connection_name[/cyan] : The identifier of the SSH connection to use (optional)"
            )
            display_info("\nSCP mode leverages your existing SSH connection's master socket")
            display_info(
                "to perform secure file transfers without requiring additional authentication."
            )
            display_info("\n[magenta bold]SCP mode commands:[/magenta bold]")
            display_info(
                "  [cyan]put[/cyan] [yellow]<local_file>[/yellow] [[yellow]<remote_file>[/yellow]]  - Upload file to remote server"
            )
            display_info(
                "  [cyan]get[/cyan] [yellow]<remote_file>[/yellow] [[yellow]<local_file>[/yellow]]  - Download file from remote server"
            )
            display_info(
                "  [cyan]ls[/cyan] [[yellow]<remote_path>[/yellow]]                - List files in remote directory"
            )
            display_info(
                "  [cyan]cd[/cyan] [yellow]<remote_path>[/yellow]                  - Change remote working directory"
            )
            display_info(
                "  [cyan]pwd[/cyan]                               - Show current remote directory"
            )
            display_info(
                "  [cyan]mget[/cyan] [yellow]<pattern>[/yellow]                    - Download multiple files matching pattern"
            )
            display_info(
                "  [cyan]local[/cyan] [[yellow]<path>[/yellow]]                    - Set or show local download directory"
            )
            display_info("  [cyan]exit[/cyan]                              - Exit SCP mode")
            display_info("\n[magenta bold]Examples:[/magenta bold]")
            display_info(
                "  [green]scp ubuntu[/green]                        [dim]# Enter SCP mode with the 'ubuntu' connection[/dim]"
            )
            display_info(
                "  [green]scp[/green]                               [dim]# Enter SCP mode and select a connection interactively[/dim]"
            )
        elif cmd == "debug":
            display_info("[bold cyan]\nToggle debug logging to console:[/bold cyan]")
            display_info(
                "[yellow]Usage:[/yellow] [cyan]debug[/cyan] [[yellow]off|disable|false|0[/yellow]]"
            )
            display_info("\n[magenta bold]Description:[/magenta bold]")
            display_info("  Toggles debug logging output to the console.")
            display_info("  Logs are always saved to /tmp/lazyssh/logs regardless of this setting.")
            display_info("  When enabled, all log messages will be displayed in the console.")
            display_info("\n[magenta bold]Examples:[/magenta bold]")
            display_info(
                "  [green]debug[/green]      [dim]# Toggle debug mode (on if off, off if on)[/dim]"
            )
            display_info("  [green]debug off[/green]  [dim]# Explicitly disable debug mode[/dim]")
        else:
            display_error(f"Unknown command: {cmd}")
            self.cmd_help([])
        return True

    def cmd_exit(self, args: list[str]) -> bool:
        """Exit lazyssh and close all connections"""
        display_info("Exiting lazyssh...")

        # Check if there are active connections and prompt for confirmation
        if self.ssh_manager.connections:
            # Use Rich's Confirm.ask for a color-coded prompt (same as prompt mode)
            from rich.prompt import Confirm

            if not Confirm.ask("You have active connections. Close them and exit?"):
                display_info("Exit cancelled")
                return True

            # User confirmed, proceed with closing connections
            display_info("Closing all connections...")
            successful_closures = 0
            total_connections = len(self.ssh_manager.connections)

            # Create a copy of the connections to avoid modification during iteration
            for socket_path in list(self.ssh_manager.connections.keys()):
                try:
                    if self.ssh_manager.close_connection(socket_path):
                        successful_closures += 1
                except Exception as e:
                    display_warning(f"Failed to close connection for {socket_path}: {str(e)}")

            # Report closure results
            if successful_closures == total_connections:
                display_success(f"Successfully closed all {total_connections} connections")
            else:
                display_warning(
                    f"Closed {successful_closures} out of {total_connections} connections"
                )
                display_info("Some connections may require manual cleanup")

        # Now exit
        display_success("Goodbye!")
        sys.exit(0)

    def cmd_mode(self, args: list[str]) -> str:
        """Switch to prompt mode"""
        # Switch to prompt mode
        display_info("Switching to prompt mode...")
        return "mode"

    def cmd_clear(self, args: list[str]) -> bool:
        """Clear the terminal screen"""
        # Implementation for clearing the screen
        os.system("clear")
        return True

    def cmd_terminal(self, args: list[str]) -> bool:
        """Handle terminal command for opening a terminal"""
        if len(args) != 1:
            display_error("Usage: terminal <ssh_id>")
            display_info("Example: terminal ubuntu")
            return False

        conn_name = args[0]
        socket_path = f"/tmp/{conn_name}"

        if socket_path not in self.ssh_manager.connections:
            display_error(f"SSH connection '{conn_name}' not found")
            if CMD_LOGGER:
                CMD_LOGGER.error(f"Connection not found for terminal: {conn_name}")
            return False

        try:
            conn = self.ssh_manager.connections[socket_path]

            # Build the SSH command for display
            ssh_cmd = f"ssh -tt -S {socket_path} {conn.username}@{conn.host}"
            if conn.shell:
                ssh_cmd += f" {conn.shell}"

            # Display the command that will be executed
            display_info("Opening terminal with command:")
            display_info(ssh_cmd)
            if CMD_LOGGER:
                CMD_LOGGER.info(f"Opening terminal for connection: {conn_name}")

            self.ssh_manager.open_terminal(socket_path)
            display_success(f"Terminal opened for connection '{conn_name}'")
            return True
        except ValueError:
            display_error("Invalid SSH ID")
            return False

    def cmd_close(self, args: list[str]) -> bool:
        """Handle close command for closing an SSH connection"""
        if len(args) != 1:
            display_error("Usage: close <ssh_id>")
            display_info("Example: close ubuntu")
            return False

        conn_name = args[0]
        socket_path = f"/tmp/{conn_name}"

        if socket_path not in self.ssh_manager.connections:
            display_error(f"SSH connection '{conn_name}' not found")
            return False

        try:
            if self.ssh_manager.close_connection(socket_path):
                display_success(f"Connection '{conn_name}' closed")
                return True
            return False
        except ValueError:
            display_error("Invalid SSH ID")
            return False

    def cmd_scp(self, args: list[str]) -> bool:
        """Enter SCP mode for file transfers"""
        selected_connection = None

        # If a connection name is provided, use it
        if args:
            selected_connection = args[0]

            # Validate the connection exists
            socket_path = f"/tmp/{selected_connection}"
            if socket_path not in self.ssh_manager.connections:
                display_error(f"Connection '{selected_connection}' not found")
                return False

        # Start SCP mode
        display_info("Entering SCP mode...")
        scp_mode = SCPMode(self.ssh_manager, selected_connection)
        scp_mode.run()
        display_info("Exited SCP mode")
        return True

    def cmd_debug(self, args: list[str]) -> bool:
        """Enable or disable debug logging"""
        if args and args[0].lower() in ("off", "disable", "false", "0"):
            set_debug_mode(False)
            display_info("Debug logging disabled")
            if CMD_LOGGER:
                CMD_LOGGER.info("Debug logging disabled")
        else:
            set_debug_mode(True)
            display_info("Debug logging enabled")
            if CMD_LOGGER:
                CMD_LOGGER.info("Debug logging enabled")
        return True

    def cmd_disconnectall(self, args: list[str]) -> bool:
        """Close all connections"""
        # Implementation for disconnecting all connections
        if not self.ssh_manager.connections:
            display_info("No active connections to close")
            return True

        display_info(f"Closing {len(self.ssh_manager.connections)} connections...")

        # Make a copy of the connections to avoid modification during iteration
        connections = self.ssh_manager.connections.copy()
        for socket_path in list(connections.keys()):
            self.ssh_manager.close_connection(socket_path)

        display_success("All connections closed")
        return True
