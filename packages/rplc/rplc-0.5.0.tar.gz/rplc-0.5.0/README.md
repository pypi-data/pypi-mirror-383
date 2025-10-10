# rplc

**rplc** (Replace Locally) is a CLI tool for managing file and directory mirroring in development workflows. It enables developers to swap between original and custom versions of files without polluting the main repository.

**Perfect for:**
- Managing personal configuration overrides during development
- Testing with different configuration files without git changes
- Maintaining custom versions of files across development sessions
- Creating isolated development environments

All operations are atomic and idempotent.


## Features

- **File/Directory Mirroring**: Swap between original and mirror versions of files and directories
- **Configuration-Driven**: Define mirror mappings in Markdown configuration files
- **Environment Variable Support**: Use environment variables in path configurations for flexible setups
- **Environment Configuration**: Configure CLI options via environment variables
- **Environment Integration**: Automatic `.envrc` management with swap state tracking
- **Atomic Operations**: Safe file operations with backup and restore capabilities
- **Selective Operations**: Target specific files or operate on entire configurations

## Installation

### From PyPI

```bash
pip install rplc
```

### From Source

```bash
git clone https://github.com/sysid/rplc.git
cd rplc
uv sync --dev  # Install with development dependencies
uv tool install -e .  # Install CLI globally
```

## Quick Start

### 1. Create a Configuration File

Create a configuration file (e.g., `rplc-config.md`):

```markdown
# Development

## rplc-config
main/resources/application.yml
main/src/class.java
scratchdir/
$HOME/.config/app/local-settings.yml
${PROJECT_ROOT}/temp/
# Lines starting with # are ignored as comments
```

### 2. Set up Mirror Directory Structure

```
project/
├── main/resources/application.yml    # Original files
├── main/src/class.java
└── scratchdir/
    └── file.txt

mirror_proj/
├── main/resources/application.yml    # Mirror versions
├── main/src/class.java
└── scratchdir/
    └── file.txt
```

### 3. Swap in Mirror Versions

```bash
# Swap all configured files
rplc swapin --config rplc-config.md

# Or swap specific files only
rplc swapin main/resources/application.yml main/src/class.java --config rplc-config.md
```

### 4. Swap Back to Originals

```bash
# Swap out all files
rplc swapout --config rplc-config.md

# Or swap out specific files only
rplc swapout main/resources/application.yml --config rplc-config.md
```

## Working Directory Requirements

**IMPORTANT:** `rplc` must be run from within your project directory (or any subdirectory).

The tool validates that your current working directory is within the project directory to prevent accidental operations on the wrong files.

### Project Detection

When no `RPLC_PROJ_DIR` is set, `rplc` looks for project markers in the current directory:
- `.git/` - Git repository
- `.envrc` - direnv configuration
- `.rplc` - rplc marker file (create this to mark your project root)
- `README.md`, `pyproject.toml`, `package.json` - Common project files

**If no markers are found**, you must either:
1. Set the `RPLC_PROJ_DIR` environment variable
2. Use the `--proj-dir` flag
3. Create a `.rplc` marker file in your project root

### Examples

```bash
# ✓ Running from project root
cd /path/to/myproject
rplc swapin

# ✓ Running from subdirectory
cd /path/to/myproject/src
rplc swapin

# ✗ Running from parent directory (will fail)
cd /path/to
rplc swapin --proj-dir myproject  # Error: not within project directory

# ✓ Using environment variable
export RPLC_PROJ_DIR=/path/to/myproject
cd /anywhere/within/myproject
rplc swapin
```

## Environment Variables

RPLC can be configured using environment variables, which serve as defaults when command-line options are not provided:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `RPLC_CONFIG` | Path to configuration file | `sample.md` |
| `RPLC_PROJ_DIR` | Project directory path | Auto-detected from cwd |
| `RPLC_MIRROR_DIR` | Mirror directory path | `../mirror_proj` |
| `RPLC_NO_ENV` | Disable .envrc management | `false` |

### Example Environment Setup

```bash
# In your .bashrc, .zshrc, or project .envrc
export RPLC_CONFIG="$HOME/.config/rplc/config.md"
export RPLC_PROJ_DIR="/workspace/myproject"
export RPLC_MIRROR_DIR="/workspace/mirror_myproject"
export RPLC_NO_ENV="false"

# Now you can use rplc without specifying options
rplc swapin
rplc info
```

## Usage

### Commands

#### `info`
Display configuration information and current swap status.

```bash
rplc info [OPTIONS]
```

Shows:
- Configuration paths and their sources (CLI option vs environment variable)
- Configured files/directories with their current status
- Overall swap state (SWAPPED IN / NORMAL STATE)
- Environment variable status

#### `swapin`
Replace original files with mirror versions.

```bash
rplc swapin [FILES...] [OPTIONS]
```

**Arguments:**
- `FILES...`: Specific files or directories to swap in (space-separated)

**Options:**
- `--pattern, -g`: Glob pattern for file selection (e.g., "*.yml", "main/**/*")
- `--exclude, -x`: Exclude patterns (can be used multiple times)
- `--proj-dir, -p`: Project directory (env: `RPLC_PROJ_DIR`)
- `--mirror-dir, -m`: Mirror directory (env: `RPLC_MIRROR_DIR`)
- `--config, -c`: Configuration file (env: `RPLC_CONFIG`)
- `--no-env`: Disable `.envrc` management (env: `RPLC_NO_ENV`)

**Examples:**
```bash
# Swap all configured files (using environment variables)
rplc swapin

# Swap specific files only
rplc swapin main/resources/application.yml main/src/class.java

# Swap using glob patterns
rplc swapin --pattern "*.yml"
rplc swapin --pattern "main/**/*"

# Swap all except certain files
rplc swapin --exclude "*.log" --exclude "temp/*"

# Combine specific files with exclusions
rplc swapin config/ src/ --exclude "*.backup"

# Swap with custom directories (overrides environment)
rplc swapin --proj-dir /path/to/project --mirror-dir /path/to/mirror

# Real-world examples
rplc swapin config/database.yml         # Override database config
rplc swapin --pattern "config/*.yml"    # All YAML configs
rplc swapin src/ --exclude "*/test/*"   # Source code except tests
```

#### `swapout`
Restore original files and move modified versions to mirror.

```bash
rplc swapout [FILES...] [OPTIONS]
```

Uses same arguments and options as `swapin`.

**Examples:**
```bash
# Swap out all configured files
rplc swapout

# Swap out specific files only
rplc swapout main/resources/application.yml

# Swap out using patterns
rplc swapout --pattern "*.yml"

# Swap out all except certain files
rplc swapout --exclude "*.log"
```

#### `delete`
Remove files/directories from rplc management.

```bash
rplc delete [FILES...] [OPTIONS]
```

**Important:** This command only works when files are swapped out (in their original state). Use `rplc swapout` first if files are currently swapped in.

**What it removes:**
- Mirror directory content
- Backup files (`.rplc.original`)
- Configuration file entries

**Arguments:**
- `FILES...`: Specific files or directories to remove from management (space-separated)

**Options:**
- `--pattern, -g`: Glob pattern for file selection
- `--exclude, -x`: Exclude patterns (can be used multiple times)
- `--proj-dir, -p`: Project directory (env: `RPLC_PROJ_DIR`)
- `--mirror-dir, -m`: Mirror directory (env: `RPLC_MIRROR_DIR`)
- `--config, -c`: Configuration file (env: `RPLC_CONFIG`)
- `--no-env`: Disable `.envrc` management (env: `RPLC_NO_ENV`)

**Examples:**
```bash
# Remove a specific file from management
rplc delete main/resources/application.yml

# Remove multiple files
rplc delete main/resources/application.yml main/src/class.java

# Remove using glob patterns
rplc delete --pattern "*.yml"

# Remove a directory
rplc delete scratchdir/

# Remove all except certain files
rplc delete --pattern "main/**/*" --exclude "*.log"

# If file is swapped in, you'll get an error:
# Error: Cannot delete - currently swapped in
# Run 'rplc swapout' first to restore original state
```

### Configuration Format

Configuration files use Markdown format with a specific structure. Only content under the `# Development` → `## rplc-config` section is processed:

```markdown
# Development

## rplc-config
path/to/file.txt
path/to/directory/
another/file.yml
$HOME/.config/app/settings.yml
${PROJECT_ROOT}/temp/cache/
# This is a comment and will be ignored
```

**Rules:**
- Paths ending with `/` are treated as directories
- Paths are relative to project root (unless using environment variables)
- Code blocks are ignored
- Only content under `# Development` → `## rplc-config` is processed
- Environment variables are resolved using `$VAR` or `${VAR}` syntax
    - Undefined environment variables are left as-is (no error thrown)
    - Tilde (`~`) expands to user's home directory
    - Variables can be combined: `~/${PROJECT}/config`
    - Trailing `/` still indicates directories after expansion


### Environment Integration

RPLC automatically manages the `RPLC_SWAPPED` environment variable in `.envrc` files:

- **swapin**: Sets `export RPLC_SWAPPED=1`
- **swapout**: Removes the variable

Disable with `--no-env` flag or `RPLC_NO_ENV=true` environment variable.

## How It Works

### Swap-In Process

1. **Backup Original**: Moves original file to `mirror_dir/path.rplc.original`
2. **Create Sentinel**: Copies mirror content to `mirror_dir/path.rplc_active`
3. **Replace Original**: Moves mirror file to original location
4. **Update Environment**: Sets `RPLC_SWAPPED=1` in `.envrc`

### Swap-Out Process

1. **Store Changes**: Moves modified file from original location to mirror
2. **Restore Original**: Moves backup from `mirror_dir/path.rplc.original` to original location
3. **Cleanup**: Removes sentinel files
4. **Update Environment**: Removes `RPLC_SWAPPED` from `.envrc`

### File Structure During Operation

```
project/
├── file.txt                          # Active file (mirror content during swap-in)
└── .envrc                            # Contains RPLC_SWAPPED=1 during swap-in

mirror_proj/
├── file.txt                          # Modified content after swap-out
├── file.txt.rplc.original             # Backup of original content
└── file.txt.rplc_active               # Sentinel marking active swap
```
### Swap State Tracking

rplc tracks swap state through two mechanisms:

#### 1. Sentinel Files (`.rplc_active`)
- **Purpose**: Track which files are currently swapped in
- **Location**: Mirror directory with `.rplc_active` suffix
- **Content**: Copy of the original mirror content
- **Check**: `sentinel.exists()` determines swap state
- **Cleanup**: Removed during `swap_out`

#### 2. Environment Variable (`RPLC_SWAPPED`)
- **Purpose**: Global state indicator in `.envrc`
- **Value**: `export RPLC_SWAPPED=1` when any files are swapped
- **Management**: Automatically added/removed during operations
- **Usage**: External tools can check this variable

**State Flow:**
```
Normal State:     No sentinel files, no RPLC_SWAPPED
Swapped State:    Sentinel files exist, RPLC_SWAPPED=1
```

## Troubleshooting

### Common Errors

**Error: "rplc must be run from within the project directory"**

This means you're trying to run `rplc` from a directory that's not within your project.

Solutions:
1. `cd` into your project directory or any subdirectory within it
2. Set `RPLC_PROJ_DIR` environment variable to your project path
3. Use `--proj-dir` flag (but still run from within that directory)

**Warning: "Current directory doesn't appear to be a project root"**

This occurs when no project markers are found in the current directory and `RPLC_PROJ_DIR` is not set.

Solutions:
1. Ensure you're in the correct project directory
2. Create a `.rplc` marker file: `touch .rplc`
3. Set `RPLC_PROJ_DIR` environment variable
4. Use `--proj-dir` flag explicitly

### General Troubleshooting

```bash
# Show detailed help for any command
rplc --help
rplc swapin --help

# Show current configuration and status
rplc info

# Enable verbose output
rplc -v swapin

# Check which directory rplc thinks is the project
rplc info  # Shows project directory in configuration table
```

## Development

### Setup

```bash
# Install dependencies
uv sync --dev

# Install pre-commit hooks
pre-commit install

# Run tests
make test

# Lint and format
make lint
make format
```

### Project Structure

```
src/rplc/
├── bin/
│   ├── __init__.py
│   └── cli.py              # CLI interface
└── lib/
    ├── __init__.py
    ├── config.py           # Configuration parsing
    └── mirror.py           # Core mirroring logic

tests/
├── bin/
│   └── test_cli.py         # CLI tests
├── lib/
│   ├── test_config.py      # Configuration tests
│   └── test_mirror.py      # Core logic tests
└── conftest.py             # Test fixtures
```

### Testing

```bash
# Run all tests with coverage
make test
```

### Building

```bash
# Build package
make build

# Create release
make bump-patch  # or bump-minor, bump-major
```

## Requirements

- Python 3.12 or higher
- typer>=0.15.1
- `uv` for faster dependency management
- `direnv` for automatic environment variable loading

## License

BSD 3-Clause License. See [LICENSE](LICENSE) for details.

Copyright © 2024, [sysid](https://sysid.github.io/). All rights reserved.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make lint` and `make test`
5. Submit a pull request
