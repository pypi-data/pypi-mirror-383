"""
Python library for chroot functionality.

This library provides the ability to set up and manage chroot environments
using only Python standard library modules.
"""

import contextlib
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

__version__ = "0.1.0"

logger = logging.getLogger(__name__)

# Type alias for mount specifications
MountSpec = dict[str, Any]


class ChrootError(Exception):
    """Exception raised for chroot-related errors."""

    pass


class MountError(Exception):
    """Exception raised for mount-related errors."""

    pass


class MountManager:
    """Manages filesystem mounts for chroot environments."""

    def __init__(self):
        self.active_mounts: list[str] = []
        self.active_lazy: list[str] = []
        self.active_files: list[str] = []

    def mount(
        self, source: str, target: str, fstype: str | None = None, options: str | None = None, bind: bool = False
    ) -> None:
        """Mount a filesystem and track it for cleanup."""
        cmd = ["mount"]

        if bind:
            cmd.append("--bind")
        elif fstype:
            cmd.extend(["-t", fstype])

        if options:
            cmd.extend(["-o", options])

        cmd.extend([source, target])

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.active_mounts.insert(0, target)  # Insert at beginning for reverse order unmount
            logger.debug(f"Mounted {source} at {target}")
        except subprocess.CalledProcessError as e:
            raise MountError(f"Failed to mount {source} at {target}: {e.stderr}") from None

    def mount_lazy(self, source: str, target: str, bind: bool = False) -> None:
        """Mount with lazy unmount tracking."""
        self.mount(source, target, bind=bind)
        # Move from active_mounts to active_lazy
        if target in self.active_mounts:
            self.active_mounts.remove(target)
            self.active_lazy.insert(0, target)

    def bind_device(self, source: str, target: str) -> None:
        """Bind mount a device file."""
        # Create the target file
        Path(target).touch()
        self.active_files.insert(0, target)
        self.mount(source, target, bind=True)

    def create_symlink(self, source: str, target: str) -> None:
        """Create a symbolic link and track it for cleanup."""
        try:
            os.symlink(source, target)
            self.active_files.insert(0, target)
            logger.debug(f"Created symlink {target} -> {source}")
        except OSError as e:
            raise MountError(f"Failed to create symlink {target} -> {source}: {e}") from None

    def unmount_all(self) -> None:
        """Unmount all tracked mounts."""
        # Unmount regular mounts
        for mount_point in self.active_mounts:
            try:
                subprocess.run(["umount", mount_point], check=True, capture_output=True)
                logger.debug(f"Unmounted {mount_point}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to unmount {mount_point}: {e.stderr}")

        # Lazy unmount
        for mount_point in self.active_lazy:
            try:
                subprocess.run(["umount", "--lazy", mount_point], check=True, capture_output=True)
                logger.debug(f"Lazy unmounted {mount_point}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to lazy unmount {mount_point}: {e.stderr}")

        # Remove created files/symlinks
        for file_path in self.active_files:
            try:
                os.unlink(file_path)
                logger.debug(f"Removed {file_path}")
            except OSError as e:
                logger.warning(f"Failed to remove {file_path}: {e}")

        # Clear tracking lists
        self.active_mounts.clear()
        self.active_lazy.clear()
        self.active_files.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unmount_all()


class ChrootManager:
    """Manages chroot environments with proper mount setup and cleanup."""

    def __init__(
        self,
        chroot_dir: str | Path,
        unshare_mode: bool = False,
        custom_mounts: list[MountSpec] | None = None,
        auto_shell: bool = True,
    ):
        """
        Initialize the chroot manager.

        Args:
            chroot_dir: Path to the chroot directory
            unshare_mode: Whether to use unshare mode (for non-root users)
            custom_mounts: Optional list of custom mount specifications
                Each mount spec is a dict with keys:
                - source: Source path/device (required)
                - target: Target path relative to chroot (required)
                - fstype: Filesystem type (optional, defaults to auto-detect)
                - options: Mount options (optional)
                - bind: Whether this is a bind mount (optional, defaults to False)
                - mkdir: Whether to create target directory (optional, defaults to True)
            auto_shell: Whether to automatically detect shell features in string commands
                and wrap them with 'bash -c' (default: True)
        """
        self.chroot_dir = Path(chroot_dir).resolve()
        self.unshare_mode = unshare_mode
        self.custom_mounts = custom_mounts or []
        self.auto_shell = auto_shell
        self.mount_manager = MountManager()
        self._is_setup = False

    def _check_root(self) -> None:
        """Check if running as root (required for normal mode)."""
        if not self.unshare_mode and os.getuid() != 0:
            raise ChrootError("This operation requires root privileges. Use unshare_mode=True for non-root operation.")

    def _check_chroot_dir(self) -> None:
        """Validate the chroot directory."""
        if not self.chroot_dir.is_dir():
            raise ChrootError(f"Chroot directory does not exist: {self.chroot_dir}")

    def _setup_standard_mounts(self) -> None:
        """Set up standard filesystem mounts for chroot."""
        proc_dir = self.chroot_dir / "proc"
        sys_dir = self.chroot_dir / "sys"
        dev_dir = self.chroot_dir / "dev"

        # Create directories if they don't exist
        proc_dir.mkdir(exist_ok=True)
        sys_dir.mkdir(exist_ok=True)
        dev_dir.mkdir(exist_ok=True)

        # Mount proc
        self.mount_manager.mount("proc", str(proc_dir), fstype="proc", options="nosuid,noexec,nodev")

        # Mount sys
        self.mount_manager.mount("sys", str(sys_dir), fstype="sysfs", options="nosuid,noexec,nodev,ro")

        # Mount efivarfs if available
        efivarfs_dir = sys_dir / "firmware/efi/efivars"
        if efivarfs_dir.exists():
            with contextlib.suppress(MountError):
                self.mount_manager.mount(
                    "efivarfs", str(efivarfs_dir), fstype="efivarfs", options="nosuid,noexec,nodev"
                )

        # Mount dev
        self.mount_manager.mount("udev", str(dev_dir), fstype="devtmpfs", options="mode=0755,nosuid")

        # Mount devpts
        devpts_dir = dev_dir / "pts"
        devpts_dir.mkdir(exist_ok=True)
        self.mount_manager.mount("devpts", str(devpts_dir), fstype="devpts", options="mode=0620,gid=5,nosuid,noexec")

        # Mount shm
        shm_dir = dev_dir / "shm"
        shm_dir.mkdir(exist_ok=True)
        self.mount_manager.mount("shm", str(shm_dir), fstype="tmpfs", options="mode=1777,nosuid,nodev")

        # Mount run
        run_dir = self.chroot_dir / "run"
        run_dir.mkdir(exist_ok=True)
        self.mount_manager.mount("run", str(run_dir), fstype="tmpfs", options="nosuid,nodev,mode=0755")

        # Mount tmp
        tmp_dir = self.chroot_dir / "tmp"
        tmp_dir.mkdir(exist_ok=True)
        self.mount_manager.mount("tmp", str(tmp_dir), fstype="tmpfs", options="mode=1777,strictatime,nodev,nosuid")

    def _setup_unshare_mounts(self) -> None:
        """Set up mounts for unshare mode."""
        # Bind mount the chroot directory to itself
        self.mount_manager.mount_lazy(str(self.chroot_dir), str(self.chroot_dir), bind=True)

        # Mount proc
        proc_dir = self.chroot_dir / "proc"
        proc_dir.mkdir(exist_ok=True)
        self.mount_manager.mount("proc", str(proc_dir), fstype="proc", options="nosuid,noexec,nodev")

        # Recursive bind mount sys
        sys_dir = self.chroot_dir / "sys"
        sys_dir.mkdir(exist_ok=True)
        self.mount_manager.mount_lazy("/sys", str(sys_dir), bind=True)

        # Create device symlinks
        dev_dir = self.chroot_dir / "dev"
        dev_dir.mkdir(exist_ok=True)

        self.mount_manager.create_symlink("/proc/self/fd", str(dev_dir / "fd"))
        self.mount_manager.create_symlink("/proc/self/fd/0", str(dev_dir / "stdin"))
        self.mount_manager.create_symlink("/proc/self/fd/1", str(dev_dir / "stdout"))
        self.mount_manager.create_symlink("/proc/self/fd/2", str(dev_dir / "stderr"))

        # Bind mount essential devices
        for device in ["full", "null", "random", "tty", "urandom", "zero"]:
            self.mount_manager.bind_device(f"/dev/{device}", str(dev_dir / device))

        # Mount run and tmp
        run_dir = self.chroot_dir / "run"
        run_dir.mkdir(exist_ok=True)
        self.mount_manager.mount("run", str(run_dir), fstype="tmpfs", options="nosuid,nodev,mode=0755")

        tmp_dir = self.chroot_dir / "tmp"
        tmp_dir.mkdir(exist_ok=True)
        self.mount_manager.mount("tmp", str(tmp_dir), fstype="tmpfs", options="mode=1777,strictatime,nodev,nosuid")

    def _resolve_link(self, path: str, root: str | None = None) -> str:
        """Resolve symbolic links, similar to the bash version."""
        target = path
        if root and not root.endswith("/"):
            root = root + "/"

        while os.path.islink(target):
            target = os.readlink(target)
            if not os.path.isabs(target):
                target = os.path.join(os.path.dirname(path), target)
            target = os.path.normpath(target)

            if root and not target.startswith(root):
                target = root + target.lstrip("/")

        return target

    def _needs_shell(self, command_str: str) -> bool:
        """
        Detect if a command string contains shell metacharacters that require bash -c wrapping.

        Returns True if the command contains shell features like pipes, redirects,
        command substitution, logical operators, etc.
        """
        import re

        # Shell metacharacters that require shell interpretation
        shell_patterns = [
            r"\|",  # Pipes: cmd1 | cmd2
            r"&&",  # Logical AND: cmd1 && cmd2
            r"\|\|",  # Logical OR: cmd1 || cmd2
            r"[;&]",  # Command separators: cmd1; cmd2 or cmd1 & cmd2
            r"[<>]",  # Redirects: cmd > file, cmd < file
            r"`[^`]*`",  # Command substitution: `cmd`
            r"\$\([^)]*\)",  # Command substitution: $(cmd)
            r"\*",  # Glob patterns: *.txt
            r"\?",  # Glob patterns: file?.txt
            r"~",  # Home directory expansion
            r"\$\w+",  # Variable expansion: $VAR
            r"\{[^}]*\}",  # Brace expansion: {a,b,c}
        ]

        # Skip detection if already wrapped with bash -c
        if command_str.strip().startswith(("bash -c", "sh -c")):
            return False

        # Check for any shell metacharacters outside of quotes
        # This is a simplified approach - a more robust version would need
        # proper quote-aware parsing
        return any(re.search(pattern, command_str) for pattern in shell_patterns)

    def _setup_custom_mounts(self) -> None:
        """Set up user-defined custom mounts."""
        for mount_spec in self.custom_mounts:
            try:
                # Validate required fields
                if "source" not in mount_spec:
                    raise MountError("Mount specification missing required 'source' field")
                if "target" not in mount_spec:
                    raise MountError("Mount specification missing required 'target' field")

                source = mount_spec["source"]
                target_rel = mount_spec["target"].lstrip("/")  # Remove leading slash for relative path
                target = str(self.chroot_dir / target_rel)

                # Get optional parameters
                fstype = mount_spec.get("fstype")
                options = mount_spec.get("options")
                bind = mount_spec.get("bind", False)
                mkdir = mount_spec.get("mkdir", True)

                # Create target directory if requested
                if mkdir:
                    Path(target).mkdir(parents=True, exist_ok=True)

                # Perform the mount
                self.mount_manager.mount(source, target, fstype=fstype, options=options, bind=bind)
                logger.debug(f"Custom mount: {source} -> {target}")

            except Exception as e:
                logger.error(f"Failed to setup custom mount {mount_spec}: {e}")
                raise MountError(f"Failed to setup custom mount: {e}") from None

    def _setup_resolv_conf(self) -> None:
        """Set up resolv.conf in the chroot."""
        host_resolv = "/etc/resolv.conf"
        chroot_resolv = self.chroot_dir / "etc/resolv.conf"

        # Resolve symbolic links
        src = self._resolve_link(host_resolv)
        dest = self._resolve_link(str(chroot_resolv), str(self.chroot_dir))

        if not os.path.exists(src):
            return  # No source resolv.conf

        if not os.path.exists(dest):
            if dest == str(chroot_resolv):
                return  # No resolv.conf needed in chroot

            # Create dummy file for binding
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            Path(dest).touch()

        try:
            self.mount_manager.mount(src, dest, bind=True)
        except MountError as e:
            logger.warning(f"Failed to setup resolv.conf: {e}")

    def setup(self) -> None:
        """Set up the chroot environment."""
        if self._is_setup:
            return

        self._check_chroot_dir()

        # For unshare mode, skip mount setup as it will be done in the unshared namespace
        if not self.unshare_mode:
            self._check_root()

            try:
                self._setup_standard_mounts()
                self._setup_resolv_conf()
                self._setup_custom_mounts()

                # Check if chroot_dir is a mountpoint
                try:
                    result = subprocess.run(
                        ["mountpoint", "-q", str(self.chroot_dir)], check=False, capture_output=True
                    )
                    if result.returncode != 0:
                        logger.warning(
                            f"{self.chroot_dir} is not a mountpoint. This may have undesirable side effects."
                        )
                except FileNotFoundError:
                    pass  # mountpoint command not available

            except Exception as e:
                self.teardown()
                raise ChrootError(f"Failed to setup chroot: {e}") from None

        self._is_setup = True

    def teardown(self) -> None:
        """Tear down the chroot environment."""
        if self._is_setup:
            self.mount_manager.unmount_all()
            self._is_setup = False

    def _create_unshare_script(self, command: list[str], userspec: str | None = None) -> str:
        """Create a script to run within the unshared namespace."""
        # Check if verbose logging is enabled
        verbose = logger.isEnabledFor(logging.DEBUG)

        script_lines = [
            "#!/bin/bash",
            "set -e",
            "",
        ]

        if verbose:
            script_lines.extend(
                [
                    "echo 'Setting up unshare chroot environment...'",
                    "echo 'Target directory: " + str(self.chroot_dir) + "'",
                    "",
                ]
            )

        script_lines.extend(
            [
                "# Set up basic directories",
                f"cd '{self.chroot_dir}'",
            ]
        )

        if verbose:
            script_lines.append("echo 'Creating directory structure...'")

        script_lines.extend(
            [
                "mkdir -p proc sys dev dev/pts dev/shm run tmp",
                "",
            ]
        )

        if verbose:
            script_lines.append("echo 'Mounting essential filesystems...'")

        script_lines.extend(
            [
                "# Mount essential filesystems",
                "mount -t proc proc proc",
                "mount --bind /sys sys 2>/dev/null || mkdir -p sys",
                "mount -t tmpfs udev dev",
                "mkdir -p dev/pts dev/shm",
                "mount -t devpts devpts dev/pts -o mode=0620,gid=5,nosuid,noexec",
                "mount -t tmpfs shm dev/shm -o mode=1777,nosuid,nodev",
                "mount -t tmpfs run run -o nosuid,nodev,mode=0755",
                "mount -t tmpfs tmp tmp -o mode=1777,strictatime,nodev,nosuid",
                "",
            ]
        )

        if verbose:
            script_lines.append("echo 'Setting up device files...'")

        script_lines.extend(
            [
                "# Create device symlinks",
                "ln -sf /proc/self/fd dev/fd",
                "ln -sf /proc/self/fd/0 dev/stdin",
                "ln -sf /proc/self/fd/1 dev/stdout",
                "ln -sf /proc/self/fd/2 dev/stderr",
                "",
                "# Create essential device files",
            ]
        )

        for device in ["full", "null", "random", "tty", "urandom", "zero"]:
            script_lines.append(f"touch dev/{device}")
            script_lines.append(f"mount --bind /dev/{device} dev/{device}")

        script_lines.extend(
            [
                "",
                "# Set up resolv.conf if available",
                "if [ -f /etc/resolv.conf ] && [ -d etc ]; then",
                "    mkdir -p etc",
                "    if [ ! -f etc/resolv.conf ]; then",
                "        touch etc/resolv.conf",
                "    fi",
                "    mount --bind /etc/resolv.conf etc/resolv.conf 2>/dev/null || true",
                "fi",
                "",
            ]
        )

        # Add custom mounts
        if self.custom_mounts and verbose:
            script_lines.append("echo 'Setting up custom mounts...'")

        for mount_spec in self.custom_mounts:
            source = mount_spec["source"]
            target_rel = mount_spec["target"].lstrip("/")
            fstype = mount_spec.get("fstype")
            options = mount_spec.get("options")
            bind = mount_spec.get("bind", False)
            mkdir = mount_spec.get("mkdir", True)

            if verbose:
                script_lines.append(f"echo 'Mounting {source} -> {target_rel}'")

            if mkdir:
                script_lines.append(f"mkdir -p '{target_rel}'")

            mount_cmd = ["mount"]
            if bind:
                mount_cmd.append("--bind")
            elif fstype:
                mount_cmd.extend(["-t", fstype])

            if options:
                mount_cmd.extend(["-o", options])

            mount_cmd.extend([f"'{source}'", f"'{target_rel}'"])
            script_lines.append(" ".join(mount_cmd))

        script_lines.extend(
            [
                "",
            ]
        )

        if verbose:
            script_lines.append("echo 'Entering chroot and executing command...'")

        script_lines.append("# Execute the command in chroot")

        chroot_cmd = ["chroot"]
        if userspec:
            chroot_cmd.extend(["--userspec", userspec])
        chroot_cmd.append(".")
        chroot_cmd.extend(f"'{arg}'" for arg in command)

        script_lines.append(" ".join(chroot_cmd))

        return "\n".join(script_lines)

    def execute(
        self,
        command: list[str] | str | None = None,
        userspec: str | None = None,
        capture_output: bool = False,
        text: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Execute a command in the chroot environment.

        Args:
            command: Command to execute (defaults to ['/bin/bash']). Can be a list of strings or a single string.
                    When auto_shell=True (default), string commands containing shell metacharacters
                    (pipes |, logical operators &&/||, redirects <>, command substitution `cmd`/$(cmd),
                    glob patterns *, variable expansion $VAR, etc.) are automatically wrapped with 'bash -c'.
                    Simple commands are parsed with shlex.split().
                    Set auto_shell=False during initialization to disable this behavior and require explicit 'bash -c' wrapping.
            userspec: User specification in format 'user' or 'user:group'
            capture_output: If True, capture stdout and stderr. If False, output goes to the terminal (default: False)
            text: If True, decode output as text. If False, return bytes (default: True)

        Returns:
            CompletedProcess object with the result. When capture_output=True, the stdout and stderr
            attributes will contain the captured output.

        Examples:
            # Simple commands (both formats work identically):
            result = chroot.execute(["echo", "hello"])
            result = chroot.execute("echo hello")

            # Capture output:
            result = chroot.execute("echo hello", capture_output=True)
            print(f"Output: {result.stdout}")
            print(f"Errors: {result.stderr}")

            # Commands with quoted arguments:
            result = chroot.execute("echo 'hello world'", capture_output=True)

            # Shell features now work automatically (when auto_shell=True):
            result = chroot.execute("ls | wc -l", capture_output=True)                    # Pipes
            result = chroot.execute("echo hello && echo world", capture_output=True)     # Logical operators
            result = chroot.execute("echo `date`", capture_output=True)                  # Command substitution
            result = chroot.execute("ls *.txt", capture_output=True)                     # Glob patterns

            # Manual shell invocation still works:
            result = chroot.execute("bash -c 'echo hello && echo world'", capture_output=True)

            # Disable auto-detection by setting auto_shell=False during initialization:
            chroot_manual = ChrootManager('/path', auto_shell=False)
            result = chroot_manual.execute("bash -c 'ls | wc -l'")  # Explicit bash -c needed
        """
        if not self._is_setup:
            raise ChrootError("Chroot environment not set up. Call setup() first.")

        if command is None:
            command = ["/bin/bash"]
        elif isinstance(command, str):
            import shlex

            # Auto-detect shell features and wrap with bash -c if needed
            if self.auto_shell and self._needs_shell(command):
                logger.debug(f"Auto-detected shell features in command: {command}")
                command = ["bash", "-c", command]
            else:
                command = shlex.split(command)

        if self.unshare_mode:
            # For unshare mode, create a script and run it in unshared namespace
            logger.debug("Creating unshare script for command: %s", command)
            script_content = self._create_unshare_script(command, userspec)

            # Write script to a temporary file
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
                f.write(script_content)
                script_path = f.name

            logger.debug("Unshare script written to: %s", script_path)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Script content:\n%s", script_content)

            try:
                # Make script executable
                os.chmod(script_path, 0o755)

                # Run the script in unshared namespace
                unshare_cmd = ["unshare", "--fork", "--pid", "--mount", "--map-auto", "--map-root-user", script_path]

                logger.debug("Executing unshare command: %s", " ".join(unshare_cmd))

                env = os.environ.copy()
                env["SHELL"] = "/bin/bash"

                return subprocess.run(unshare_cmd, check=False, env=env, capture_output=capture_output, text=text)
            finally:
                # Clean up script file
                try:
                    os.unlink(script_path)
                    logger.debug("Cleaned up script file: %s", script_path)
                except OSError:
                    pass
        else:
            # Standard chroot mode
            chroot_cmd = ["chroot"]
            if userspec:
                chroot_cmd.extend(["--userspec", userspec])

            chroot_cmd.append(str(self.chroot_dir))
            chroot_cmd.extend(command)

            env = os.environ.copy()
            env["SHELL"] = "/bin/bash"

            return subprocess.run(chroot_cmd, check=False, env=env, capture_output=capture_output, text=text)

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()


# Main entry point for command-line usage
def main():
    """Command-line interface for chorut."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Python wrapper of chroot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
If 'command' is unspecified, chorut will launch /bin/bash.

Note that when using chorut, the target chroot directory *should* be a
mountpoint. This ensures that tools such as pacman(8) or findmnt(8) have an
accurate hierarchy of the mounted filesystems within the chroot.

If your chroot target is not a mountpoint, you can bind mount the directory on
itself to make it a mountpoint, i.e. 'mount --bind /your/chroot /your/chroot'.
        """,
    )

    parser.add_argument("chroot_dir", help="chroot directory")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command and arguments to execute")
    parser.add_argument("-N", "--unshare", action="store_true", help="Run in unshare mode as a regular user")
    parser.add_argument(
        "-u", "--userspec", metavar="USER[:GROUP]", help="Specify non-root user and optional group to use"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "-m",
        "--mount",
        action="append",
        metavar="SOURCE:TARGET[:OPTIONS]",
        help="Add custom mount (can be used multiple times). Format: source:target[:options]",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # Parse custom mounts
    custom_mounts = []
    if args.mount:
        for mount_spec in args.mount:
            parts = mount_spec.split(":")
            if len(parts) < 2:
                print(
                    f"Error: Invalid mount specification '{mount_spec}'. Format: source:target[:options]",
                    file=sys.stderr,
                )
                return 1

            mount_dict = {
                "source": parts[0],
                "target": parts[1],
            }

            # Parse options if provided
            if len(parts) > 2:
                options = parts[2]
                if "bind" in options:
                    mount_dict["bind"] = True
                mount_dict["options"] = options

            custom_mounts.append(mount_dict)

    try:
        with ChrootManager(args.chroot_dir, unshare_mode=args.unshare, custom_mounts=custom_mounts) as chroot:
            result = chroot.execute(args.command if args.command else None, userspec=args.userspec)
            return result.returncode
    except ChrootError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())

__all__ = [
    "ChrootError",
    "ChrootManager",
    "MountError",
    "MountManager",
]
