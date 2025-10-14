# SPDX-FileCopyrightText: 2025-present Yiannis Charalambous <yiannis128@hotmail.com>
#
# SPDX-License-Identifier: AGPL-3.0

from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget
from PySide6.QtCore import Qt

from ..models import AppConfig, ConfigManager
from ..services import ModManager
from .mods_tab import ModsTab
from .settings_tab import SettingsTab
from .download_tab import DownloadTab
from .about_tab import AboutTab


class MainWindow(QMainWindow):
    """Main application window with tabs."""

    def __init__(self, initial_download_url: str | None = None):
        super().__init__()

        # Load configuration
        self.config = ConfigManager.load()
        self.mod_manager = ModManager(self.config)

        # Set up the window
        self.setWindowTitle("Crossworlds Mod Manager")
        self.setMinimumSize(800, 600)

        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tabs
        self.mods_tab = ModsTab(self.mod_manager)
        self.download_tab = DownloadTab(self.config, self.on_download_complete)
        self.download_tab.main_window = self  # Set reference to MainWindow
        self.settings_tab = SettingsTab(self.config, self.on_settings_changed)
        self.about_tab = AboutTab()

        # Add tabs
        self.tabs.addTab(self.mods_tab, "Mods")
        self.tabs.addTab(self.download_tab, "Download")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.about_tab, "About")

        # Validate config and update UI
        self.validate_config()

        # Initial refresh if config is valid
        if self.config.is_valid()[0]:
            self.mods_tab.refresh()

        # If launched with a download URL, switch to Download tab and populate URL
        if initial_download_url:
            self.tabs.setCurrentWidget(self.download_tab)
            self.download_tab.set_url(initial_download_url)

    def validate_config(self) -> None:
        """Validate configuration and update UI state."""
        is_valid, error_message = self.config.is_valid()
        self.mods_tab.set_config_validity(is_valid, error_message)

    def on_settings_changed(self) -> None:
        """Handle settings changes."""
        # Save configuration
        ConfigManager.save(self.config)

        # Update mod manager with new config
        self.mod_manager.config = self.config

        # Validate config and update UI
        self.validate_config()

        # Refresh mods list if config is valid
        if self.config.is_valid()[0]:
            self.mods_tab.refresh()

    def on_download_complete(self) -> None:
        """Handle download completion by refreshing mods list."""
        if self.config.is_valid()[0]:
            self.mods_tab.refresh()

    def set_tabs_enabled(self, enabled: bool) -> None:
        """Enable or disable tab switching."""
        if enabled:
            # Re-enable all tabs and tab bar
            for i in range(self.tabs.count()):
                self.tabs.setTabEnabled(i, True)
            self.tabs.tabBar().setEnabled(True)
        else:
            # Disable tab switching (but keep current tab content enabled)
            # Disable all other tabs
            current_index = self.tabs.currentIndex()
            for i in range(self.tabs.count()):
                if i != current_index:
                    self.tabs.setTabEnabled(i, False)

            # Disable tab bar to prevent clicking on tabs
            self.tabs.tabBar().setEnabled(False)
