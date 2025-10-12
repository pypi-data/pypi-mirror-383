from __future__ import annotations

from typing import TYPE_CHECKING

from frontengine.utils.logging.loggin_instance import front_engine_logger

if TYPE_CHECKING:
    from frontengine.ui.main_ui import FrontEngineMainUI

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu


class ExtendSystemTray(QSystemTrayIcon):

    def __init__(self, main_window: FrontEngineMainUI):
        front_engine_logger.info(f"Init ExtendSystemTray main_window: {main_window}")
        super().__init__(parent=main_window)
        self.menu = QMenu()
        self.main_window = main_window
        self.hide_main_window_action = QAction("Hide")
        self.hide_main_window_action.triggered.connect(self.main_window.hide)
        self.menu.addAction(self.hide_main_window_action)
        self.maximized_main_window_action = QAction("Maximized")
        self.maximized_main_window_action.triggered.connect(self.main_window.showMaximized)
        self.menu.addAction(self.maximized_main_window_action)
        self.normal_main_window_action = QAction("Normal")
        self.normal_main_window_action.triggered.connect(self.main_window.showNormal)
        self.menu.addAction(self.normal_main_window_action)
        self.close_main_window_action = QAction("Close")
        self.close_main_window_action.triggered.connect(self.close_all)
        self.menu.addAction(self.close_main_window_action)
        self.setContextMenu(self.menu)
        self.activated.connect(self.clicked)

    def close_all(self):
        front_engine_logger.info("ExtendSystemTray close_all")
        self.setVisible(False)
        self.main_window.close()

    def clicked(self, reason):
        front_engine_logger.info(f"ExtendSystemTray clicked reason:{reason}")
        if reason == self.ActivationReason.DoubleClick:
            self.main_window.showMaximized()
