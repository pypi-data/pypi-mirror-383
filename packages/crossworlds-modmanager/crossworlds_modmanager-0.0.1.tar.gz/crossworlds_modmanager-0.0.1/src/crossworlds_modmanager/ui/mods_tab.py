# SPDX-FileCopyrightText: 2025-present Yiannis Charalambous <yiannis128@hotmail.com>
#
# SPDX-License-Identifier: AGPL-3.0

import webbrowser
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QListWidgetItem,
    QMessageBox,
    QLabel,
)
from PySide6.QtCore import Qt

from ..services import ModManager
from .widgets import ClickableLinkLabel


class ModsTab(QWidget):
    """Tab for displaying and managing mods."""

    def __init__(self, mod_manager: ModManager):
        super().__init__()
        self.mod_manager = mod_manager
        self.config_valid = True

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Error message label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; font-weight: bold; padding: 10px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        # Download mods link
        download_link = ClickableLinkLabel(
            "Download Mods", "https://gamebanana.com/games/21640"
        )
        download_link.setStyleSheet(
            "color: blue; text-decoration: underline; padding: 5px;"
        )
        layout.addWidget(download_link)

        # Mods list widget
        self.mods_list = QListWidget()
        layout.addWidget(self.mods_list)

        # Button bar
        button_layout = QHBoxLayout()

        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self.on_move_up)
        button_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self.on_move_down)
        button_layout.addWidget(self.move_down_btn)

        button_layout.addStretch()

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.on_play)
        button_layout.addWidget(self.play_btn)

        self.apply_play_btn = QPushButton("Apply && Play")
        self.apply_play_btn.clicked.connect(self.on_apply_and_play)
        button_layout.addWidget(self.apply_play_btn)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.on_apply)
        button_layout.addWidget(self.apply_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        button_layout.addWidget(self.refresh_btn)

        self.update_btn = QPushButton("Update")
        self.update_btn.setEnabled(False)  # TODO: Implement update functionality
        button_layout.addWidget(self.update_btn)

        layout.addLayout(button_layout)

    def set_config_validity(self, is_valid: bool, error_message: str = "") -> None:
        """
        Set the configuration validity state and update UI accordingly.

        Args:
            is_valid: Whether the config is valid
            error_message: Error message to display if invalid
        """
        self.config_valid = is_valid

        if is_valid:
            # Hide error message
            self.error_label.hide()
            # Enable all buttons
            self.move_up_btn.setEnabled(True)
            self.move_down_btn.setEnabled(True)
            self.play_btn.setEnabled(True)
            self.apply_play_btn.setEnabled(True)
            self.apply_btn.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            # Update button stays disabled (TODO)
        else:
            # Show error message
            self.error_label.setText(
                f"⚠ Configuration Error: {error_message}\n"
                "Please configure the correct settings in the Settings tab."
            )
            self.error_label.show()
            # Disable all buttons
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            self.play_btn.setEnabled(False)
            self.apply_play_btn.setEnabled(False)
            self.apply_btn.setEnabled(False)
            self.refresh_btn.setEnabled(False)

    def refresh(self) -> None:
        """Refresh the mods list from disk."""
        if not self.config_valid:
            return

        # Block signals to prevent triggering itemChanged
        self.mods_list.blockSignals(True)

        # Clear and repopulate
        self.mods_list.clear()

        # Get mods from mod manager
        mods = self.mod_manager.refresh()

        # Add mods to list
        for mod in mods:
            item = QListWidgetItem(mod.display_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if mod.enabled else Qt.Unchecked)
            self.mods_list.addItem(item)

        # Re-enable signals
        self.mods_list.blockSignals(False)

    def on_move_up(self) -> None:
        """Move selected mod up in the list."""
        current_row = self.mods_list.currentRow()
        if current_row > 0:
            # Swap items in UI
            item = self.mods_list.takeItem(current_row)
            self.mods_list.insertItem(current_row - 1, item)
            self.mods_list.setCurrentRow(current_row - 1)

            # Swap in mod manager's internal list
            (
                self.mod_manager.mods[current_row],
                self.mod_manager.mods[current_row - 1],
            ) = (
                self.mod_manager.mods[current_row - 1],
                self.mod_manager.mods[current_row],
            )
            self.mod_manager._reassign_priorities()

    def on_move_down(self) -> None:
        """Move selected mod down in the list."""
        current_row = self.mods_list.currentRow()
        if current_row >= 0 and current_row < self.mods_list.count() - 1:
            # Swap items in UI
            item = self.mods_list.takeItem(current_row)
            self.mods_list.insertItem(current_row + 1, item)
            self.mods_list.setCurrentRow(current_row + 1)

            # Swap in mod manager's internal list
            (
                self.mod_manager.mods[current_row],
                self.mod_manager.mods[current_row + 1],
            ) = (
                self.mod_manager.mods[current_row + 1],
                self.mod_manager.mods[current_row],
            )
            self.mod_manager._reassign_priorities()

    def on_apply(self) -> None:
        """Apply mod changes based on current checkbox states."""
        try:
            # Update mod states based on current checkbox states (without reordering)
            for index in range(self.mods_list.count()):
                item = self.mods_list.item(index)
                is_checked = item.checkState() == Qt.Checked
                mod = self.mod_manager.mods[index]
                mod.enabled = is_checked

            # Reassign priorities for enabled mods
            self.mod_manager._reassign_priorities()

            # Apply the changes to disk
            self.mod_manager.apply()

            # Refresh to show the actual state from disk
            self.refresh()

            QMessageBox.information(self, "Success", "Mods applied successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply mods: {e}")

    def on_play(self) -> None:
        """Launch the game via Steam."""
        try:
            webbrowser.open("steam://launch/2486820")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch game: {e}")

    def on_apply_and_play(self) -> None:
        """Apply mods and launch the game."""
        try:
            # Update mod states based on current checkbox states (without reordering)
            for index in range(self.mods_list.count()):
                item = self.mods_list.item(index)
                is_checked = item.checkState() == Qt.Checked
                mod = self.mod_manager.mods[index]
                mod.enabled = is_checked

            # Reassign priorities for enabled mods
            self.mod_manager._reassign_priorities()

            # Apply the changes to disk
            self.mod_manager.apply()

            # Refresh to show the actual state from disk
            self.refresh()

            # Launch the game via Steam
            webbrowser.open("steam://launch/2486820")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to apply mods or launch game: {e}"
            )
