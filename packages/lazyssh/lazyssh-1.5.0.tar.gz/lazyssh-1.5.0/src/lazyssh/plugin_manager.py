"""Plugin manager for LazySSH - Discover, validate and execute plugins"""

import os
import select
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

from .logging_module import APP_LOGGER
from .models import SSHConnection


@dataclass
class PluginMetadata:
    """Metadata extracted from a plugin file"""

    name: str
    description: str
    version: str
    requirements: str
    file_path: Path
    plugin_type: str  # 'python' or 'shell'
    is_valid: bool
    validation_errors: list[str]


class PluginManager:
    """Manages plugin discovery, validation and execution"""

    def __init__(self, plugins_dir: Path | None = None):
        """Initialize the plugin manager

        Args:
            plugins_dir: Path to plugins directory. Defaults to src/lazyssh/plugins/
        """
        if plugins_dir is None:
            # Default to the plugins directory in the package
            self.plugins_dir = Path(__file__).parent / "plugins"
        else:
            self.plugins_dir = Path(plugins_dir)

        self._plugins_cache: dict[str, PluginMetadata] | None = None

        if APP_LOGGER:
            APP_LOGGER.debug(f"PluginManager initialized with directory: {self.plugins_dir}")

    def discover_plugins(self, force_refresh: bool = False) -> dict[str, PluginMetadata]:
        """Discover all plugins in the plugins directory

        Args:
            force_refresh: If True, bypass cache and re-scan directory

        Returns:
            Dictionary mapping plugin names to their metadata
        """
        if not force_refresh and self._plugins_cache is not None:
            return self._plugins_cache

        plugins: dict[str, PluginMetadata] = {}

        if not self.plugins_dir.exists():
            if APP_LOGGER:
                APP_LOGGER.warning(f"Plugins directory does not exist: {self.plugins_dir}")
            self._plugins_cache = plugins
            return plugins

        # Scan for .py and .sh files, ensuring we don't follow symlinks outside plugins_dir
        base_dir = self.plugins_dir.resolve()
        for entry in self.plugins_dir.iterdir():
            if entry.name.startswith("_") or entry.name.startswith("."):
                # Skip private files, __init__.py, and hidden files
                continue

            # Resolve the candidate path while safely handling broken symlinks
            try:
                resolved_path = entry.resolve(strict=False)
            except Exception as e:
                if APP_LOGGER:
                    APP_LOGGER.debug(
                        f"Skipping plugin entry due to resolution failure: {entry} ({e})"
                    )
                continue

            # Ensure the resolved path is within the plugins directory to avoid path traversal via symlinks
            try:
                is_within = resolved_path == base_dir or resolved_path.is_relative_to(base_dir)
            except Exception:
                # Fallback conservative behavior if any unexpected error occurs
                is_within = False

            if not is_within:
                if APP_LOGGER:
                    APP_LOGGER.debug(
                        f"Skipping plugin entry outside plugins_dir: {resolved_path} (base: {base_dir})"
                    )
                continue

            if resolved_path.suffix in [".py", ".sh"]:
                metadata = self._extract_metadata(resolved_path)
                if metadata:
                    plugins[metadata.name] = metadata

        self._plugins_cache = plugins

        if APP_LOGGER:
            APP_LOGGER.debug(f"Discovered {len(plugins)} plugins")

        return plugins

    def _extract_metadata(self, plugin_file: Path) -> PluginMetadata | None:
        """Extract metadata from a plugin file

        Args:
            plugin_file: Path to the plugin file

        Returns:
            PluginMetadata object or None if file cannot be read
        """
        validation_errors = []
        plugin_type = "python" if plugin_file.suffix == ".py" else "shell"

        # Default values
        name = plugin_file.stem
        description = "No description available"
        version = "1.0.0"
        requirements = "python3" if plugin_type == "python" else "bash"

        # Try to read metadata from file
        try:
            with open(plugin_file, encoding="utf-8") as f:
                # Read first 50 lines to find metadata
                for _ in range(50):
                    line = f.readline()
                    if not line:
                        break

                    line = line.strip()

                    # Parse metadata comments
                    if line.startswith("#"):
                        if "PLUGIN_NAME:" in line:
                            name = line.split("PLUGIN_NAME:", 1)[1].strip()
                        elif "PLUGIN_DESCRIPTION:" in line:
                            description = line.split("PLUGIN_DESCRIPTION:", 1)[1].strip()
                        elif "PLUGIN_VERSION:" in line:
                            version = line.split("PLUGIN_VERSION:", 1)[1].strip()
                        elif "PLUGIN_REQUIREMENTS:" in line:
                            requirements = line.split("PLUGIN_REQUIREMENTS:", 1)[1].strip()
        except Exception as e:
            validation_errors.append(f"Failed to read file: {e}")

        # Validate plugin
        is_valid = self._validate_plugin(plugin_file, validation_errors)

        return PluginMetadata(
            name=name,
            description=description,
            version=version,
            requirements=requirements,
            file_path=plugin_file,
            plugin_type=plugin_type,
            is_valid=is_valid,
            validation_errors=validation_errors,
        )

    def _validate_plugin(self, plugin_file: Path, validation_errors: list[str]) -> bool:
        """Validate a plugin file

        Args:
            plugin_file: Path to the plugin file
            validation_errors: List to append validation errors to

        Returns:
            True if plugin is valid, False otherwise
        """
        # Check if file exists
        if not plugin_file.exists():
            validation_errors.append("File does not exist")
            return False

        # Require executability and a shebang for all plugins (including .py)
        if not os.access(plugin_file, os.X_OK):
            validation_errors.append("File is not executable")
            return False

        # Check for shebang
        try:
            with open(plugin_file, "rb") as f:
                first_bytes = f.read(2)
                if first_bytes != b"#!":
                    validation_errors.append("Missing shebang (#!)")
                    return False
        except Exception as e:
            validation_errors.append(f"Failed to check shebang: {e}")
            return False

        return True

    def get_plugin(self, plugin_name: str) -> PluginMetadata | None:
        """Get metadata for a specific plugin

        Args:
            plugin_name: Name of the plugin

        Returns:
            PluginMetadata object or None if plugin not found
        """
        plugins = self.discover_plugins()
        return plugins.get(plugin_name)

    def execute_plugin(
        self, plugin_name: str, connection: SSHConnection, args: list[str] | None = None
    ) -> tuple[bool, str, float]:
        """Execute a plugin with the given SSH connection context

        Args:
            plugin_name: Name of the plugin to execute
            connection: SSHConnection object with connection details
            args: Optional additional arguments to pass to plugin

        Returns:
            Tuple of (success: bool, output: str, execution_time: float)
        """
        # Get plugin metadata
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return False, f"Plugin '{plugin_name}' not found", 0.0

        if not plugin.is_valid:
            errors = "\n".join(plugin.validation_errors)
            return False, f"Plugin '{plugin_name}' is invalid:\n{errors}", 0.0

        # Prepare environment variables
        env = os.environ.copy()
        env.update(self._prepare_plugin_env(connection))

        # Prepare command
        plugin_type = getattr(plugin, "plugin_type", None)
        if plugin_type is None:
            # Infer from file extension when not provided by mocked objects
            plugin_type = "python" if str(plugin.file_path).endswith(".py") else "shell"

        if plugin_type == "python":
            cmd = [sys.executable, str(plugin.file_path)]
        else:
            cmd = [str(plugin.file_path)]
        if args:
            cmd.extend(args)

        if APP_LOGGER:
            APP_LOGGER.debug(f"Executing plugin: {plugin_name} with command: {' '.join(cmd)}")

        # Execute plugin (streaming under the hood, while preserving combined output return)
        start_time = time.time()
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            stdout_buffer: list[str] = []
            stderr_buffer: list[str] = []

            # File descriptors for select
            assert process.stdout is not None
            assert process.stderr is not None
            stdout_fd = process.stdout.fileno()
            stderr_fd = process.stderr.fileno()

            # Global timeout of 5 minutes
            timeout_seconds = 300
            deadline = start_time + timeout_seconds

            # Read until process terminates and pipes are exhausted
            while True:
                now = time.time()
                remaining = max(0, deadline - now)
                if remaining == 0:
                    process.kill()
                    execution_time = time.time() - start_time
                    error_msg = (
                        f"Plugin '{plugin_name}' timed out after {execution_time:.0f} seconds"
                    )
                    if APP_LOGGER:
                        APP_LOGGER.error(error_msg)
                    # Ensure we reap the process
                    try:
                        process.wait(timeout=5)
                    except Exception:
                        pass
                    return False, error_msg, execution_time

                rlist, _, _ = select.select([stdout_fd, stderr_fd], [], [], min(0.2, remaining))

                read_any = False
                if stdout_fd in rlist:
                    line = process.stdout.readline()
                    if line:
                        stdout_buffer.append(line)
                        read_any = True
                if stderr_fd in rlist:
                    line = process.stderr.readline()
                    if line:
                        stderr_buffer.append(line)
                        read_any = True

                # Break if process ended and no more data to read
                if process.poll() is not None:
                    # Drain any remaining data quickly
                    remaining_out = process.stdout.read()
                    if remaining_out:
                        stdout_buffer.append(remaining_out)
                    remaining_err = process.stderr.read()
                    if remaining_err:
                        stderr_buffer.append(remaining_err)
                    break

                # If nothing read this loop and process still running, continue until timeout or data
                if not read_any:
                    continue

            execution_time = time.time() - start_time
            returncode = process.returncode if process.returncode is not None else 1
            success = returncode == 0

            if APP_LOGGER:
                APP_LOGGER.debug(
                    f"Plugin {plugin_name} completed with exit code {returncode} in {execution_time:.2f}s"
                )

            # Preserve existing behavior: combine stdout and stderr
            output = "".join(stdout_buffer)
            if stderr_buffer:
                output += "\n" + "".join(stderr_buffer)

            return success, output, execution_time

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Failed to execute plugin '{plugin_name}': {e}"
            if APP_LOGGER:
                APP_LOGGER.error(error_msg)
            return False, error_msg, execution_time

    def execute_plugin_streaming(
        self,
        plugin_name: str,
        connection: SSHConnection,
        args: list[str] | None = None,
        *,
        timeout: int = 300,
        on_chunk: Callable[[tuple[str, str]], None] | None = None,
    ) -> Iterator[tuple[str, str]]:
        """Stream a plugin's stdout and stderr in real time.

        Yields tuples of ("stdout"|"stderr", line) if no callback is provided.
        If `on_chunk` is provided, it will be called for each tuple and the
        generator will yield nothing.

        The method enforces a total execution timeout and keeps stdout/stderr
        separated internally for callers that want to aggregate.
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            message = f"Plugin '{plugin_name}' not found"
            if on_chunk is None:
                # Emit as stderr-style line
                yield ("stderr", message + "\n")
            else:
                on_chunk(("stderr", message + "\n"))
            return

        if not plugin.is_valid:
            errors = "\n".join(plugin.validation_errors)
            message = f"Plugin '{plugin_name}' is invalid:\n{errors}"
            if on_chunk is None:
                yield ("stderr", message + "\n")
            else:
                on_chunk(("stderr", message + "\n"))
            return

        env = os.environ.copy()
        env.update(self._prepare_plugin_env(connection))

        plugin_type = getattr(plugin, "plugin_type", None)
        if plugin_type is None:
            plugin_type = "python" if str(plugin.file_path).endswith(".py") else "shell"

        if plugin_type == "python":
            cmd = [sys.executable, str(plugin.file_path)]
        else:
            cmd = [str(plugin.file_path)]
        if args:
            cmd.extend(args)

        if APP_LOGGER:
            APP_LOGGER.debug(f"Streaming plugin: {plugin_name} with command: {' '.join(cmd)}")

        start_time = time.time()
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            assert process.stdout is not None
            assert process.stderr is not None

            stdout_fd = process.stdout.fileno()
            stderr_fd = process.stderr.fileno()

            deadline = start_time + timeout

            def emit(kind: str, data: str) -> None:
                if not data:
                    return
                if on_chunk is None:
                    # yield from inside nested fn is not allowed; we buffer and signal via outer scope
                    nonlocal_yields.append((kind, data))
                else:
                    on_chunk((kind, data))

            while True:
                now = time.time()
                remaining = max(0, deadline - now)
                if remaining == 0:
                    process.kill()
                    break

                rlist, _, _ = select.select([stdout_fd, stderr_fd], [], [], min(0.2, remaining))

                nonlocal_yields: list[tuple[str, str]] = []
                if stdout_fd in rlist:
                    line = process.stdout.readline()
                    if line:
                        emit("stdout", line)
                if stderr_fd in rlist:
                    line = process.stderr.readline()
                    if line:
                        emit("stderr", line)

                # Flush any pending yields for this iteration
                if on_chunk is None and nonlocal_yields:
                    yield from nonlocal_yields

                if process.poll() is not None:
                    # Drain remaining
                    remaining_out = process.stdout.read()
                    if remaining_out:
                        if on_chunk is None:
                            yield ("stdout", remaining_out)
                        else:
                            on_chunk(("stdout", remaining_out))
                    remaining_err = process.stderr.read()
                    if remaining_err:
                        if on_chunk is None:
                            yield ("stderr", remaining_err)
                        else:
                            on_chunk(("stderr", remaining_err))
                    break

        except Exception as e:
            message = f"Failed to execute plugin '{plugin_name}': {e}\n"
            if on_chunk is None:
                yield ("stderr", message)
            else:
                on_chunk(("stderr", message))
            return

        finally:
            execution_time = time.time() - start_time
            if APP_LOGGER:
                rc = None
                try:
                    rc = process.returncode  # type: ignore[name-defined]
                except Exception:
                    pass
                APP_LOGGER.debug(
                    f"Streaming plugin {plugin_name} finished (rc={rc}) in {execution_time:.2f}s"
                )

    def _prepare_plugin_env(self, connection: SSHConnection) -> dict[str, str]:
        """Prepare environment variables for plugin execution

        Args:
            connection: SSHConnection object

        Returns:
            Dictionary of environment variables
        """
        # Get socket name from socket path
        socket_name = Path(connection.socket_path).name

        env = {
            "LAZYSSH_SOCKET": socket_name,
            "LAZYSSH_HOST": connection.host,
            "LAZYSSH_PORT": str(connection.port),
            "LAZYSSH_USER": connection.username,
            "LAZYSSH_SOCKET_PATH": connection.socket_path,
            "LAZYSSH_PLUGIN_API_VERSION": "1",
        }

        # Add optional fields
        if connection.identity_file:
            env["LAZYSSH_SSH_KEY"] = connection.identity_file

        if connection.shell:
            env["LAZYSSH_SHELL"] = connection.shell

        return env
