# SPDX-FileCopyrightText: 2025-present Yiannis Charalambous <yiannis128@hotmail.com>
#
# SPDX-License-Identifier: AGPL-3.0

from pathlib import Path
from typing import Callable
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
)

from ..models import AppConfig
from .widgets import ClickableDirectoryLabel


class SettingsTab(QWidget):
    """Tab for configuring application settings."""

    def __init__(self, config: AppConfig, on_settings_changed: Callable[[], None]):
        super().__init__()
        self.config = config
        self.on_settings_changed = on_settings_changed

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Form layout for settings
        form_layout = QFormLayout()

        # Base game directory
        game_dir_layout = QHBoxLayout()
        self.game_dir_input = QLineEdit(str(config.base_game_directory))
        game_dir_layout.addWidget(self.game_dir_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_game_directory)
        game_dir_layout.addWidget(browse_btn)

        form_layout.addRow("Base Game Directory:", game_dir_layout)

        # Relative active mods directory (editable)
        self.relative_dir_input = QLineEdit(config.relative_active_mods_dir)
        form_layout.addRow("Relative Active Mods Dir:", self.relative_dir_input)

        # Game directory (clickable, opens in file explorer)
        self.game_dir_label = ClickableDirectoryLabel(str(config.base_game_directory))
        form_layout.addRow("Game Directory:", self.game_dir_label)

        # Computed active mods directory (clickable, opens in file explorer)
        self.active_dir_label = ClickableDirectoryLabel(
            str(config.active_mods_directory)
        )
        form_layout.addRow("Active Mods Directory:", self.active_dir_label)

        # Computed inactive mods directory (clickable, opens in file explorer)
        self.inactive_dir_label = ClickableDirectoryLabel(
            str(config.inactive_mods_directory)
        )
        form_layout.addRow("Inactive Mods Directory:", self.inactive_dir_label)

        layout.addLayout(form_layout)

        # Save button
        save_layout = QHBoxLayout()
        save_layout.addStretch()

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(save_btn)

        layout.addLayout(save_layout)
        layout.addStretch()

        # Connect input changes to update preview
        self.game_dir_input.textChanged.connect(self.update_preview)
        self.relative_dir_input.textChanged.connect(self.update_preview)

    def browse_game_directory(self) -> None:
        """Open a directory browser for selecting the game directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Game Directory", str(self.config.base_game_directory)
        )

        if directory:
            self.game_dir_input.setText(directory)

    def update_preview(self) -> None:
        """Update the preview of all directory labels."""
        base_dir = Path(self.game_dir_input.text())
        relative_dir = self.relative_dir_input.text()
        active_dir = base_dir / relative_dir / "~mods"
        inactive_dir = base_dir / "mods"
        self.game_dir_label.setText(str(base_dir))
        self.active_dir_label.setText(str(active_dir))
        self.inactive_dir_label.setText(str(inactive_dir))

    def save_settings(self) -> None:
        """Save the settings."""
        # Update config
        self.config.base_game_directory = Path(self.game_dir_input.text())
        self.config.relative_active_mods_dir = self.relative_dir_input.text()

        # Validate configuration
        is_valid, error_message = self.config.is_valid()

        if is_valid:
            # Trigger callback to save and update UI
            self.on_settings_changed()
            QMessageBox.information(
                self, "Settings Saved", "Settings have been saved successfully!"
            )
        else:
            # Still save but warn the user
            self.on_settings_changed()
            QMessageBox.warning(
                self,
                "Configuration Invalid",
                f"Settings saved, but configuration is invalid:\n\n{error_message}\n\n"
                "Please correct the settings to use the mod manager.",
            )
