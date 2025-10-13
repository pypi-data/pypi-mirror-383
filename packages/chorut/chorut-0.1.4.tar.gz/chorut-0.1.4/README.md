# chorut

A Python library that provides chroot functionality inspired by arch-chroot with minimal dependencies, using only Python standard library modules.

## Features

- **Complete chroot setup**: Automatically mounts proc, sys, dev, devpts, shm, run, and tmp filesystems
- **Custom mounts**: Support for user-defined bind mounts and filesystem mounts
- **Unshare mode**: Support for running as non-root user using Linux namespaces
- **Context manager**: Clean automatic setup and teardown
- **resolv.conf handling**: Proper DNS configuration in chroot
- **String and list commands**: Execute commands using either list format or string format
- **Output capture**: Capture stdout and stderr from executed commands
- **Error handling**: Comprehensive error reporting and cleanup
- **Zero external dependencies**: Uses only Python standard library

## Installation

```bash
pip install chorut
```

## Usage

### As a Library

```python
from chorut import ChrootManager

# Basic usage as root
with ChrootManager('/path/to/chroot') as chroot:
    result = chroot.execute(['ls', '-la'])

# String commands (parsed with shlex.split)
with ChrootManager('/path/to/chroot') as chroot:
    result = chroot.execute('ls -la /etc')

# Output capture
with ChrootManager('/path/to/chroot') as chroot:
    result = chroot.execute('cat /etc/hostname', capture_output=True)
    if result.returncode == 0:
        hostname = result.stdout.strip()
        print(f"Hostname: {hostname}")

# Non-root usage with unshare mode (requires complete chroot environment)
with ChrootManager('/path/to/complete/chroot', unshare_mode=True) as chroot:
    result = chroot.execute(['whoami'])

# Manual setup/teardown
chroot = ChrootManager('/path/to/chroot')
chroot.setup()
try:
    result = chroot.execute(['bash', '-c', 'echo "Hello from chroot"'])
finally:
    chroot.teardown()

# With custom mounts
custom_mounts = [
    {
        "source": "/home",
        "target": "home",
        "bind": True,
        "options": "ro"  # Read-only bind mount
    },
    {
        "source": "tmpfs",
        "target": "workspace",
        "fstype": "tmpfs",
        "options": "size=1G"
    }
]

with ChrootManager('/path/to/chroot', custom_mounts=custom_mounts) as chroot:
    result = chroot.execute(['df', '-h'])
```

### String Commands and Shell Features

The `execute` method accepts both list and string commands:

```python
# List format (recommended for complex commands)
result = chroot.execute(['ls', '-la', '/etc'])

# String format (parsed with shlex.split or auto-wrapped with bash -c)
result = chroot.execute('ls -la /etc')

# Shell features now work automatically (auto_shell=True by default)
result = chroot.execute('ls | wc -l')           # Pipes
result = chroot.execute('echo hello && echo world')  # Logical operators
result = chroot.execute('echo `date`')          # Command substitution
result = chroot.execute('ls *.txt')             # Glob patterns
result = chroot.execute('echo $HOME')           # Variable expansion

# Manual shell invocation still works
result = chroot.execute("bash -c 'ls | wc -l'")

# Disable auto-detection by setting auto_shell=False
chroot_manual = ChrootManager('/path/to/chroot', auto_shell=False)
result = chroot_manual.execute("bash -c 'ls | wc -l'")  # Explicit bash -c needed
```

**Auto-Detection**: By default (`auto_shell=True`), string commands are automatically analyzed for shell metacharacters (pipes `|`, logical operators `&&`/`||`, redirects `<>`/`>`, command substitution `` `cmd` ``/`$(cmd)`, glob patterns `*`/`?`, variable expansion `$VAR`, etc.). When detected, the command is automatically wrapped with `bash -c`. Simple commands are still parsed with `shlex.split()` for security.

### Output Capture

Capture command output using the `capture_output` parameter:

```python
# Capture both stdout and stderr
result = chroot.execute('cat /etc/hostname', capture_output=True)
if result.returncode == 0:
    hostname = result.stdout.strip()

# Capture with error handling
result = chroot.execute('ls /nonexistent', capture_output=True)
if result.returncode != 0:
    error_msg = result.stderr.strip()

# Get raw bytes instead of text
result = chroot.execute('cat binary_file', capture_output=True, text=False)
binary_data = result.stdout
```

### Custom Mounts

You can specify additional mounts to be set up in the chroot environment. Each mount specification is a dictionary with the following keys:

- `source` (required): Source path, device, or filesystem type
- `target` (required): Target path relative to chroot root
- `fstype` (optional): Filesystem type (e.g., "tmpfs", "ext4")
- `options` (optional): Mount options (e.g., "ro", "size=1G")
- `bind` (optional): Whether this is a bind mount (default: False)
- `mkdir` (optional): Whether to create target directory (default: True)

#### Examples:

```python
# Bind mount home directory as read-only
{
    "source": "/home",
    "target": "home",
    "bind": True,
    "options": "ro"
}

# Create a tmpfs workspace
{
    "source": "tmpfs",
    "target": "tmp/workspace",
    "fstype": "tmpfs",
    "options": "size=512M,mode=1777"
}

# Bind mount a specific directory
{
    "source": "/var/cache/pacman",
    "target": "var/cache/pacman",
    "bind": True
}
```

### Command Line

```bash
# Basic chroot (requires root)
sudo chorut /path/to/chroot

# Run specific command
sudo chorut /path/to/chroot ls -la

# Non-root mode (requires proper chroot environment)
chorut -N /path/to/complete/chroot

# Specify user
sudo chorut -u user:group /path/to/chroot

# Verbose output
chorut -v -N /path/to/chroot

# Custom mounts
chorut -m "/home:home:bind,ro" -m "tmpfs:workspace:size=1G" /path/to/chroot

# Multiple custom mounts
chorut -N \
  -m "/var/cache:var/cache:bind" \
  -m "tmpfs:tmp/build:size=2G" \
  /path/to/chroot make -j4
```

#### Command Line Mount Format

The `-m/--mount` option accepts mount specifications in the format:

```
SOURCE:TARGET[:OPTIONS]
```

- **SOURCE**: Source path, device, or filesystem type
- **TARGET**: Target path relative to chroot (without leading slash)
- **OPTIONS**: Comma-separated mount options (optional)

Special options:
- `bind` - Creates a bind mount
- Other options are passed to the mount command

Examples:
- `-m "/home:home:bind,ro"` - Read-only bind mount of /home
- `-m "tmpfs:workspace:size=1G"` - 1GB tmpfs at /workspace
- `-m "/dev/sdb1:mnt/data:rw"` - Mount device with read-write access

### Command Line Options

- `-h, --help`: Show help message
- `-N, --unshare`: Run in unshare mode as regular user
- `-u USER[:GROUP], --userspec USER[:GROUP]`: Specify user/group to run as
- `-v, --verbose`: Enable verbose logging
- `-m SOURCE:TARGET[:OPTIONS], --mount SOURCE:TARGET[:OPTIONS]`: Add custom mount (can be used multiple times)

## API Reference

### ChrootManager

The main class for managing chroot environments.

#### Constructor

```python
ChrootManager(chroot_dir, unshare_mode=False, custom_mounts=None, auto_shell=True)
```

- `chroot_dir`: Path to the chroot directory
- `unshare_mode`: Whether to use unshare mode for non-root operation
- `custom_mounts`: Optional list of custom mount specifications
- `auto_shell`: Whether to automatically detect shell features in string commands and wrap them with 'bash -c' (default: True)

#### Methods

- `setup()`: Set up the chroot environment
- `teardown()`: Clean up the chroot environment
- `execute(command=None, userspec=None, capture_output=False, text=True)`: Execute a command in the chroot

##### execute() Parameters

- `command`: Command to execute. Can be:
  - `list[str]`: List of command and arguments (e.g., `['ls', '-la']`)
  - `str`: String command parsed with `shlex.split()` (e.g., `'ls -la'`)
  - `None`: Start interactive shell
- `userspec`: User specification in format "user" or "user:group"
- `capture_output`: If `True`, capture stdout and stderr (default: `False`)
- `text`: If `True`, decode output as text; if `False`, return bytes (default: `True`)

##### execute() Return Value

Returns a `subprocess.CompletedProcess` object with:
- `returncode`: Exit code of the command
- `stdout`: Command output (if `capture_output=True`)
- `stderr`: Command error output (if `capture_output=True`)

##### execute() Examples

```python
# List command
result = chroot.execute(['ls', '-la'])

# String command
result = chroot.execute('ls -la')

# With output capture
result = chroot.execute('cat /etc/hostname', capture_output=True)
hostname = result.stdout.strip()

# Shell features require explicit bash
result = chroot.execute("bash -c 'ls | wc -l'", capture_output=True)
line_count = int(result.stdout.strip())

# Interactive shell (command=None)
chroot.execute()  # Starts bash shell
```

### Exceptions

- `ChrootError`: Raised for chroot-related errors
- `MountError`: Raised for mount-related errors

## Requirements

- Python 3.12+
- Linux system with mount/umount utilities
- Root privileges (unless using unshare mode)

### Unshare Mode Requirements

When using unshare mode (`-N` flag), the following additional requirements apply:

- `unshare` command must be available
- The chroot directory must contain a complete filesystem with:
  - Essential binaries in `/bin`, `/usr/bin`, etc.
  - Required libraries in `/lib`, `/lib64`, `/usr/lib`, etc.
  - Proper directory structure (`/etc`, `/proc`, `/sys`, `/dev`, etc.)

**Note**: Unshare mode performs all mount operations within an unshared mount namespace, allowing non-root users to create chroot environments. However, the target directory must still contain a complete, functional filesystem for the chroot to work properly.

For example, trying to chroot into `/tmp` will fail because it lacks the necessary binaries and libraries. You need a proper root filesystem (like those created by `debootstrap`, `pacstrap`, or similar tools).

## License

This project is in the public domain.
