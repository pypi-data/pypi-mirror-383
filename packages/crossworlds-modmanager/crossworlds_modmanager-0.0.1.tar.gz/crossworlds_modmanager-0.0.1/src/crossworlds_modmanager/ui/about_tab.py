# SPDX-FileCopyrightText: 2025-present Yiannis Charalambous <yiannis128@hotmail.com>
#
# SPDX-License-Identifier: AGPL-3.0

from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout,
)

from .widgets import ClickableLinkLabel
from crossworlds_modmanager.__about__ import __version__


class AboutTab(QWidget):
    """Tab for configuring application settings."""

    def __init__(self):
        super().__init__()

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        layout.addWidget(
            ClickableLinkLabel(
                "GitHub", "https://github.com/Yiannis128/crossworlds-modmanager"
            )
        )

        layout.addWidget(
            ClickableLinkLabel(
                "Made By Yiannis Charalambous", "https://github.com/Yiannis128"
            )
        )

        layout.addWidget(QLabel("Made with Claude CLI"))

        layout.addWidget(QLabel(f"Version: {__version__}"))
