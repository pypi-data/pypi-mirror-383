# SPDX-FileCopyrightText: 2025-present Yiannis Charalambous <yiannis128@hotmail.com>
#
# SPDX-License-Identifier: AGPL-3.0

import shutil
from pathlib import Path
from typing import List
from ..models import AppConfig, Mod


class ModManager:
    """Business logic for managing UE5 mods."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.mods: list[Mod] = []

    def _cleanup_active_directory(self) -> None:
        """
        Clean up the active mods directory by moving any mod folders that don't
        follow the xxx. prefix pattern to the inactive directory.
        """
        active_dir = self.config.active_mods_directory
        inactive_dir = self.config.inactive_mods_directory

        # Only proceed if active directory exists
        if not active_dir.exists():
            return

        # Ensure inactive directory exists
        inactive_dir.mkdir(parents=True, exist_ok=True)

        # Scan for mod directories without proper prefix
        for item in active_dir.iterdir():
            # Only process directories
            if not item.is_dir():
                continue

            dirname = item.name
            # Check if dirname matches the ###. pattern
            parts = dirname.split(".", 1)

            has_valid_prefix = (
                len(parts) == 2 and len(parts[0]) == 3 and parts[0].isdigit()
            )

            # If it doesn't have a valid prefix, move it to inactive directory
            if not has_valid_prefix:
                dest = inactive_dir / dirname
                # Only move if destination doesn't exist to avoid conflicts
                if not dest.exists():
                    shutil.move(str(item), str(dest))

    def refresh(self) -> list[Mod]:
        """
        Scan both active and inactive mod directories and build the mod list.

        Returns:
            List of mods with their current state
        """
        active_dir = self.config.active_mods_directory
        inactive_dir = self.config.inactive_mods_directory

        # Clean up active directory first
        self._cleanup_active_directory()

        # Dictionary to store mods by name
        mods_dict: dict[str, Mod] = {}

        # Scan inactive mods directory
        if inactive_dir.exists():
            for item in inactive_dir.iterdir():
                # Only process directories
                if not item.is_dir():
                    continue

                name = item.name
                if name not in mods_dict:
                    mods_dict[name] = Mod(
                        name=name, file_path=item, enabled=False, priority=None
                    )

        # Scan active mods directory
        if active_dir.exists():
            for item in active_dir.iterdir():
                # Only process directories
                if not item.is_dir():
                    continue

                dirname = item.name
                name, priority = Mod.parse_dirname(dirname)

                # If this mod exists in inactive, update it; otherwise create new
                if name in mods_dict:
                    mods_dict[name].enabled = True
                    mods_dict[name].priority = priority
                else:
                    # Mod only exists in active directory
                    mods_dict[name] = Mod(
                        name=name, file_path=item, enabled=True, priority=priority
                    )

        # Sort mods: enabled first (by priority), then disabled (alphabetically)
        self.mods = sorted(
            mods_dict.values(),
            key=lambda m: (
                not m.enabled,
                m.priority if m.priority is not None else 999999,
                m.name,
            ),
        )

        # Reassign priorities to enabled mods based on their order
        self._reassign_priorities()

        return self.mods

    def _reassign_priorities(self) -> None:
        """Reassign priorities to enabled mods based on their current order."""
        priority = 0
        for mod in self.mods:
            if mod.enabled:
                mod.priority = priority
                priority += 1
            else:
                mod.priority = None

    def toggle_mod(self, index: int) -> None:
        """Toggle a mod's enabled state."""
        if 0 <= index < len(self.mods):
            mod = self.mods[index]
            mod.enabled = not mod.enabled

            # If enabling, move to end of enabled list and assign priority
            if mod.enabled:
                # Remove from current position
                self.mods.pop(index)
                # Find last enabled mod position
                last_enabled_idx = 0
                for i, m in enumerate(self.mods):
                    if m.enabled:
                        last_enabled_idx = i + 1
                # Insert after last enabled mod
                self.mods.insert(last_enabled_idx, mod)
            else:
                # If disabling, move to disabled section
                self.mods.pop(index)
                # Find first disabled mod position
                first_disabled_idx = len(self.mods)
                for i, m in enumerate(self.mods):
                    if not m.enabled:
                        first_disabled_idx = i
                        break
                self.mods.insert(first_disabled_idx, mod)

            self._reassign_priorities()

    def move_up(self, index: int) -> int:
        """
        Move a mod up in the list (decrease priority).

        Returns:
            New index of the mod
        """
        if index > 0 and index < len(self.mods):
            mod = self.mods[index]
            other_mod = self.mods[index - 1]

            # Can only swap within the same enabled/disabled group
            if mod.enabled == other_mod.enabled:
                self.mods[index], self.mods[index - 1] = (
                    self.mods[index - 1],
                    self.mods[index],
                )
                self._reassign_priorities()
                return index - 1

        return index

    def move_down(self, index: int) -> int:
        """
        Move a mod down in the list (increase priority).

        Returns:
            New index of the mod
        """
        if index >= 0 and index < len(self.mods) - 1:
            mod = self.mods[index]
            other_mod = self.mods[index + 1]

            # Can only swap within the same enabled/disabled group
            if mod.enabled == other_mod.enabled:
                self.mods[index], self.mods[index + 1] = (
                    self.mods[index + 1],
                    self.mods[index],
                )
                self._reassign_priorities()
                return index + 1

        return index

    def apply(self) -> None:
        """
        Apply mod changes by intelligently copying enabled mod folders to the active
        directory with priority prefixes and removing disabled mods from active directory.
        Only copies mods that aren't already in the correct location, and only deletes
        mods that should no longer be active.
        """
        active_dir = self.config.active_mods_directory
        inactive_dir = self.config.inactive_mods_directory

        # Ensure active directory exists
        active_dir.mkdir(parents=True, exist_ok=True)

        # Build set of expected active mod directory names
        expected_active_mods = set()
        for mod in self.mods:
            if mod.enabled:
                expected_active_mods.add(mod.active_dirname)

        # Remove mods that shouldn't be in active directory
        if active_dir.exists():
            for item in active_dir.iterdir():
                if item.is_dir() and item.name not in expected_active_mods:
                    shutil.rmtree(item)

        # Copy enabled mods that aren't already in active directory
        for mod in self.mods:
            if mod.enabled:
                source = inactive_dir / mod.name
                dest = active_dir / mod.active_dirname

                # Only copy if source exists and destination doesn't
                if source.exists() and source.is_dir() and not dest.exists():
                    shutil.copytree(source, dest)

    def get_mod_at(self, index: int) -> Mod | None:
        """Get mod at specific index."""
        if 0 <= index < len(self.mods):
            return self.mods[index]
        return None

    def set_mod_enabled(self, index: int, enabled: bool) -> None:
        """Set a mod's enabled state."""
        if 0 <= index < len(self.mods):
            mod = self.mods[index]
            if mod.enabled != enabled:
                self.toggle_mod(index)
