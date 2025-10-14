# SPDX-FileCopyrightText: 2025-present Yiannis Charalambous <yiannis128@hotmail.com>
#
# SPDX-License-Identifier: AGPL-3.0

from typing import Callable
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QProgressBar,
    QMessageBox,
    QLabel,
)
from PySide6.QtCore import Qt

from ..services import ModDownloader, ModDownloadError
from ..models import AppConfig


class DownloadTab(QWidget):
    """Tab for downloading mods from GameBanana."""

    def __init__(
        self, config: AppConfig, on_download_complete: Callable[[], None], parent=None
    ):
        super().__init__(parent)
        self.config = config
        self.on_download_complete = on_download_complete
        self.downloader = None
        self.is_downloading = False
        self.main_window = None  # Will be set by MainWindow

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Instructions label
        instructions = QLabel(
            "Paste a GameBanana download URL below:\n"
            "• Direct link: gamebanana.com/dl/1535503\n"
            "• Crosspatch link: crosspatch:https://gamebanana.com/mmdl/1535503,Mod,622573,rar"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(
            "padding: 10px; background-color: #f0f0f0; border-radius: 5px;"
        )
        layout.addWidget(instructions)

        # URL text box
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("Paste GameBanana URL here...")
        self.url_input.setMaximumHeight(100)
        layout.addWidget(self.url_input)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        layout.addWidget(self.progress_bar)

        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.on_download_clicked)
        layout.addWidget(self.download_btn)

        layout.addStretch()

    def set_url(self, url: str) -> None:
        """
        Programmatically set the URL in the input field.
        Used when the application is launched with a crosspatch URL.
        """
        self.url_input.setPlainText(url)

    def on_download_clicked(self) -> None:
        """Handle download/cancel button click."""
        if self.is_downloading:
            # Cancel the download
            self.cancel_download()
        else:
            # Start the download
            self.start_download()

    def start_download(self) -> None:
        """Start downloading the mod."""
        url = self.url_input.toPlainText().strip()

        if not url:
            QMessageBox.warning(self, "No URL", "Please paste a GameBanana URL.")
            return

        # Validate URL format
        try:
            ModDownloader.parse_gamebanana_url(url)
        except ModDownloadError as e:
            QMessageBox.critical(
                self,
                "Invalid URL",
                f"Invalid URL format:\n\n{e}\n\n"
                "Please use one of these formats:\n"
                "• gamebanana.com/dl/1535503\n"
                "• crosspatch:https://gamebanana.com/mmdl/1535503,Mod,622573,rar",
            )
            return

        # Create and configure downloader
        self.downloader = ModDownloader(url, self.config.inactive_mods_directory)
        self.downloader.progress_updated.connect(self.on_progress_updated)
        self.downloader.download_complete.connect(self.on_download_complete_handler)
        self.downloader.download_failed.connect(self.on_download_failed)

        # Update UI state
        self.is_downloading = True
        self.download_btn.setText("Cancel")
        self.url_input.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Starting download...")

        # Disable tab switching
        if self.main_window:
            self.main_window.set_tabs_enabled(False)

        # Start download
        self.downloader.start()

    def cancel_download(self) -> None:
        """Cancel the ongoing download."""
        if self.downloader:
            self.downloader.cancel()
            self.downloader.wait()  # Wait for thread to finish

        self.reset_ui()

    def on_progress_updated(self, downloaded: int, total: int) -> None:
        """Update progress bar based on download progress."""
        if total > 0:
            percentage = int((downloaded / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(
                f"{downloaded // 1024} KB / {total // 1024} KB ({percentage}%)"
            )
        else:
            self.progress_bar.setFormat(f"{downloaded // 1024} KB downloaded...")

    def on_download_complete_handler(self, mod_name: str) -> None:
        """Handle successful download completion."""
        self.reset_ui()
        QMessageBox.information(
            self,
            "Download Complete",
            f"Mod '{mod_name}' has been downloaded and extracted successfully!",
        )
        # Trigger callback to refresh mods list
        self.on_download_complete()

    def on_download_failed(self, error_message: str) -> None:
        """Handle download failure."""
        self.reset_ui()
        QMessageBox.critical(
            self, "Download Failed", f"Failed to download mod:\n\n{error_message}"
        )

    def reset_ui(self) -> None:
        """Reset UI to initial state."""
        self.is_downloading = False
        self.download_btn.setText("Download")
        self.url_input.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready")

        # Re-enable tab switching
        if self.main_window:
            self.main_window.set_tabs_enabled(True)

        # Clean up downloader
        if self.downloader:
            self.downloader.deleteLater()
            self.downloader = None
