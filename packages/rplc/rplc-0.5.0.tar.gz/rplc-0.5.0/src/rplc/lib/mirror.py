# src/rplc/lib/mirror.py
import logging
import shutil
import subprocess
import fnmatch
from pathlib import Path
from typing import List, Optional

from rich import print

from rplc.lib.config import MirrorConfig, ConfigParser

logger = logging.getLogger(__name__)


class MirrorManager:
    """Manage mirroring of files and directories"""
    SENTINEL_SUFFIX = ".rplc_active"
    ORIGINAL_SUFFIX = ".rplc.original"
    MIRROR_BKP_SUFFIX = ".rplc_active.backup"
    ENVRC_FILE = ".envrc"
    RPLC_ENV_VAR = "RPLC_SWAPPED"

    def __init__(
        self,
        config_file: Path,
        *,
        proj_dir: Path,
        mirror_dir: Path,
        manage_env: bool = True
    ) -> None:
        self.config_file = config_file.resolve()
        self.proj_dir = proj_dir.resolve()
        self.mirror_dir = mirror_dir.resolve()
        self.configs = ConfigParser.parse_config(config_file)
        self.manage_env = manage_env
        # Convert paths to absolute with correct bases
        for config in self.configs:
            config.source_path = (self.proj_dir / config.source_path).resolve()
            rel_path = config.source_path.relative_to(self.proj_dir)
            config.mirror_path = (self.mirror_dir / rel_path).resolve()

    def _update_envrc(self, set_var: bool = True) -> None:
        """Update .envrc file with RPLC_SWAPPED variable"""
        if not self.manage_env:
            return

        envrc_path = self.proj_dir / self.ENVRC_FILE
        if not envrc_path.exists():
            return

        content = envrc_path.read_text()
        lines = content.splitlines()

        # Remove existing RPLC_SWAPPED line if present
        lines = [line for line in lines if not line.startswith("export RPLC_SWAPPED=1")]

        # Add new RPLC_SWAPPED line if setting
        if set_var:
            lines.append(f"export {self.RPLC_ENV_VAR}=1")

        # Write back to file
        envrc_path.write_text("\n".join(lines) + "\n")

    def swap_in(self, files: Optional[List[str]] = None, pattern: Optional[str] = None, exclude: Optional[List[str]] = None) -> None:
        """Swap in mirror versions of files/directories"""
        configs = self._filter_configs(files=files, pattern=pattern, exclude=exclude)
        logger.debug(f"Swapping in: {configs}")

        # Only update envrc if we're actually swapping something
        if configs:
            self._update_envrc(set_var=True)

        for config in configs:
            if not config.mirror_path.exists():
                print(f"[yellow]Warning: Mirror path does not exist: {config.mirror_path}[/yellow]")
                continue

            sentinel = self._get_sentinel_path(config)
            if sentinel.exists():
                print(f"[yellow]Already swapped in: {config.source_path}[/yellow]")
                continue

            # Create sentinel file first to mark the start of the operation
            # self._create_sentinel(config)
            self._copy_path(config.mirror_path, sentinel)

            # Backup original if it exists to .rplc.original
            if config.source_path.exists():
                backup_path = self._get_backup_path(config)
                self._move_path(config.source_path, backup_path)

            # Move mirror content to source
            self._move_path(config.mirror_path, config.source_path)

            print(f"[green]Swapped in: {config.source_path}[/green]")

    def swap_out(self, files: Optional[List[str]] = None, pattern: Optional[str] = None, exclude: Optional[List[str]] = None) -> None:
        """
        Swap out mirror versions and restore originals.
        If this is the first swap-out (mirror directory empty), moves project files to mirror.
        """
        configs = self._filter_configs(files=files, pattern=pattern, exclude=exclude)
        logger.debug(f"Swapping out: {configs}")

        # Only update envrc if we're actually swapping something
        if configs:
            self._update_envrc(set_var=False)

        for config in configs:
            sentinel = self._get_sentinel_path(config)
            backup_path = self._get_backup_path(config)

            # If no sentinel exists, this path hasn't been swapped in
            if not sentinel.exists():
                # Special case: Initialize mirror directory if target doesn't exist
                if not config.mirror_path.exists() and config.source_path.exists():
                    logger.debug(f"Initializing mirror for: {config.source_path}")
                    self._move_path(config.source_path, config.mirror_path)
                    print(f"[green]Initialized mirror: {config.mirror_path}[/green]")
                else:
                    print(f"[yellow]Already swapped out: {config.source_path}[/yellow]")
                continue

            # Store modified content in mirror
            if config.source_path.exists():
                self._move_path(config.source_path, config.mirror_path)

            # Restore backup to source path if it exists
            if backup_path.exists():
                self._move_path(backup_path, config.source_path)
            else:
                print(f"[yellow]Warning: No backup found for {config.source_path}[/yellow]")

            # Remove sentinel file/directory
            if sentinel.is_dir():
                shutil.rmtree(sentinel)
            else:
                sentinel.unlink()

            print(f"[green]Swapped out: {config.source_path}[/green]")

    def delete(self, files: Optional[List[str]] = None, pattern: Optional[str] = None, exclude: Optional[List[str]] = None) -> None:
        """
        Remove paths from rplc management - only works when swapped out.

        Removes:
        - Mirror directory content (mirror_path)
        - Backup files (.rplc.original) if present
        - Configuration entry from config file

        Raises SystemExit if any target is currently swapped in.
        """
        configs = self._filter_configs(files=files, pattern=pattern, exclude=exclude)

        if not configs:
            print("[yellow]No matching files found[/yellow]")
            return

        logger.debug(f"Deleting: {configs}")
        print("[cyan]Checking swap status...[/cyan]")

        # ==============================================================================
        # Safety Check: Ensure Nothing Is Swapped In
        # ==============================================================================
        #
        # We only allow deletion when files are swapped out to avoid edge cases
        # where the user might lose data. If any sentinel file exists, that means
        # the file is currently swapped in and we abort the operation.

        swapped_in_files = []
        for config in configs:
            sentinel = self._get_sentinel_path(config)
            if sentinel.exists():
                swapped_in_files.append(config.source_path)

        if swapped_in_files:
            print("[red]✗ Error: Cannot delete - the following files are currently swapped in:[/red]")
            for path in swapped_in_files:
                try:
                    rel_path = path.relative_to(self.proj_dir)
                except ValueError:
                    rel_path = path
                print(f"  [red]• {rel_path}[/red]")
            print("[yellow]Run 'rplc swapout' first to restore original state[/yellow]")
            raise SystemExit(1)

        print("[green]✓ All files are swapped out[/green]")
        print()

        # ==============================================================================
        # Delete Mirror Artifacts
        # ==============================================================================
        #
        # For each configured path, we remove the mirror content and any backup files.
        # We print verbose output so the user knows exactly what's being deleted.

        print("[cyan]Deleting mirror artifacts:[/cyan]")
        deleted_count = 0

        for config in configs:
            # Remove mirror content
            if config.mirror_path.exists():
                if config.mirror_path.is_dir():
                    shutil.rmtree(config.mirror_path)
                    print(f"  [dim]Removed directory: {config.mirror_path}[/dim]")
                else:
                    config.mirror_path.unlink()
                    print(f"  [dim]Removed file: {config.mirror_path}[/dim]")
                deleted_count += 1
            else:
                print(f"  [dim]Already removed: {config.mirror_path}[/dim]")

            # Remove backup if it exists
            backup_path = self._get_backup_path(config)
            if backup_path.exists():
                if backup_path.is_dir():
                    shutil.rmtree(backup_path)
                    print(f"  [dim]Removed backup: {backup_path}[/dim]")
                else:
                    backup_path.unlink()
                    print(f"  [dim]Removed backup: {backup_path}[/dim]")

        print(f"[green]✓ Deleted {deleted_count} mirror artifact(s)[/green]")
        print()

        # ==============================================================================
        # Update Configuration File
        # ==============================================================================
        #
        # Remove the path entries from the configuration file so they're no longer
        # managed by rplc. This preserves the markdown structure and other entries.

        print(f"[cyan]Updating configuration file: {self.config_file}[/cyan]")
        removed_count = 0

        for config in configs:
            if ConfigParser.remove_config_entry(self.config_file, config.source_path, self.proj_dir):
                removed_count += 1

        if removed_count > 0:
            print(f"[green]✓ Removed {removed_count} configuration entr{'y' if removed_count == 1 else 'ies'}[/green]")
        else:
            print("[yellow]No configuration entries found to remove[/yellow]")

        print()
        print(f"[green]Successfully removed {len(configs)} file(s) from rplc management[/green]")

    def _filter_configs(self, files: Optional[List[str]] = None, pattern: Optional[str] = None, exclude: Optional[List[str]] = None) -> List[MirrorConfig]:
        """Filter configs based on specified files, patterns, and exclusions"""
        # If no filters specified, return all configs
        if not any([files, pattern, exclude]):
            return self.configs

        filtered_configs = []

        # Start with all configs if no positive filters (files/pattern) are specified
        if not files and not pattern:
            filtered_configs = self.configs.copy()
        else:
            # Apply file-specific filtering
            if files:
                for file_path in files:
                    # Resolve file path relative to project directory
                    if Path(file_path).is_absolute():
                        target_path = Path(file_path).resolve()
                    else:
                        target_path = (self.proj_dir / file_path).resolve()

                    # Find matching configs
                    matching_configs = [c for c in self.configs if c.source_path == target_path]
                    if not matching_configs:
                        print(f"[yellow]Warning: No configuration found for: {file_path}[/yellow]")
                    filtered_configs.extend(matching_configs)

            # Apply pattern-based filtering
            if pattern:
                for config in self.configs:
                    # Get relative path for pattern matching
                    try:
                        rel_path = config.source_path.relative_to(self.proj_dir)
                        if fnmatch.fnmatch(str(rel_path), pattern):
                            if config not in filtered_configs:
                                filtered_configs.append(config)
                    except ValueError:
                        # Skip if path is not relative to project directory
                        pass

        # Apply exclusion filtering
        if exclude:
            excluded_configs = []
            for exclude_pattern in exclude:
                for config in filtered_configs:
                    try:
                        rel_path = config.source_path.relative_to(self.proj_dir)
                        if fnmatch.fnmatch(str(rel_path), exclude_pattern):
                            excluded_configs.append(config)
                    except ValueError:
                        # Skip if path is not relative to project directory
                        pass

            # Remove excluded configs
            filtered_configs = [c for c in filtered_configs if c not in excluded_configs]

        return filtered_configs

    def _get_backup_path(self, config: MirrorConfig) -> Path:
        """Get backup path for original in mirror directory"""
        rel_path = config.source_path.relative_to(self.proj_dir)
        if config.is_directory:
            backup_path = self.mirror_dir / f"{rel_path}{self.ORIGINAL_SUFFIX}"
        else:
            backup_path = self.mirror_dir / rel_path.parent / f"{rel_path.name}{self.ORIGINAL_SUFFIX}"
        return backup_path.resolve()

    def _get_sentinel_path(self, config: MirrorConfig) -> Path:
        """Get sentinel file path for a config"""
        rel_path = config.source_path.relative_to(self.proj_dir)
        return (self.mirror_dir / f"{rel_path}{self.SENTINEL_SUFFIX}").resolve()

    def _create_sentinel(self, config: MirrorConfig) -> None:
        """Create a sentinel file for a swapped path"""
        sentinel = self._get_sentinel_path(config)
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.touch()

    @staticmethod
    def _move_path(src: Path, dst: Path) -> None:
        """Move a path to the destination"""
        logger.debug(f"Moving {src} -> {dst}")
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()

        try:
            # First try an atomic move
            src.rename(dst)
        except OSError:
            # If atomic move fails (e.g., across devices), fallback to copy and delete
            if src.is_dir():
                shutil.copytree(src, dst)
                shutil.rmtree(src)
            else:
                shutil.copy2(src, dst)
                src.unlink()

    @staticmethod
    def _copy_path(src: Path, dst: Path) -> None:
        """Copy a path to destination, preserving metadata"""
        logger.debug(f"Copying {src} -> {dst}")
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()

        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
