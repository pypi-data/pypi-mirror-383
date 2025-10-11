"""MLineEdit
Get the user input is a text field
"""

import functools

from qtpy import QtCore, QtWidgets

from .browser import (
    MClickBrowserFileToolButton,
    MClickBrowserFolderToolButton,
    MClickSaveFileToolButton,
)
from .mixin import focus_shadow_mixin
from .push_button import MPushButton
from .theme import MTheme
from .tool_button import MToolButton
from .widget import MWidget


@focus_shadow_mixin
class MLineEdit(QtWidgets.QLineEdit, MWidget):  # pyright: ignore[reportIncompatibleMethodOverride]
    """MLineEdit"""

    delay_text_changed = QtCore.Signal(str)

    def __init__(self, text: str = "", parent: QtWidgets.QWidget | None = None):
        super().__init__(text, parent)
        self._main_layout = QtWidgets.QHBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.addStretch()

        self._prefix_widget: MWidget | None = None
        self._suffix_widget: MWidget | None = None

        self.setLayout(self._main_layout)
        self.setProperty("history", self.property("text"))
        self.setTextMargins(2, 0, 2, 0)

        self._delay_timer = QtCore.QTimer()
        self._delay_timer.setInterval(500)
        self._delay_timer.setSingleShot(True)
        self._delay_timer.timeout.connect(self._on_delay_text_changed)
        self.textChanged.connect(self._on_begin_to_start_delay)

    def get_dayu_size(self) -> int:
        """
        Get the push button height
        :return: integer
        """
        return self._dayu_size

    def set_dayu_size(self, value: int):
        """
        Set the avatar size.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        if self._prefix_widget and hasattr(self._prefix_widget, "set_dayu_size"):
            self._prefix_widget.set_dayu_size(self._dayu_size)
        if self._suffix_widget and hasattr(self._suffix_widget, "set_dayu_size"):
            self._suffix_widget.set_dayu_size(self._dayu_size)
        self.on_style_changed()

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def set_delay_duration(self, millisecond: int):
        """Set delay timer's timeout duration."""
        self._delay_timer.setInterval(millisecond)

    @QtCore.Slot()
    def _on_delay_text_changed(self):
        self.delay_text_changed.emit(self.text())

    @QtCore.Slot(str)
    def _on_begin_to_start_delay(self, _: str):
        if self._delay_timer.isActive():
            self._delay_timer.stop()
        self._delay_timer.start()

    def get_prefix_widget(self):
        """Get the prefix widget for user to edit"""
        return self._prefix_widget

    def set_prefix_widget(self, widget: MWidget):
        """Set the line edit left start widget"""
        if self._prefix_widget:
            index = self._main_layout.indexOf(self._prefix_widget)
            self._main_layout.takeAt(index)
            self._prefix_widget.setVisible(False)
        widget.setProperty("combine", "horizontal")
        widget.setProperty("position", "left")
        if hasattr(widget, "set_dayu_size"):
            widget.set_dayu_size(self._dayu_size)

        margin = self.textMargins()
        margin.setLeft(margin.left() + widget.width())
        self.setTextMargins(margin)

        self._main_layout.insertWidget(0, widget)
        self._prefix_widget = widget
        return widget

    def get_suffix_widget(self):
        """Get the suffix widget for user to edit"""
        return self._suffix_widget

    def set_suffix_widget(self, widget: MWidget):
        """Set the line edit right end widget"""
        if self._suffix_widget:
            index = self._main_layout.indexOf(self._suffix_widget)
            self._main_layout.takeAt(index)
            self._suffix_widget.setVisible(False)
        widget.setProperty("combine", "horizontal")
        widget.setProperty("position", "right")
        if hasattr(widget, "set_dayu_size"):
            widget.set_dayu_size(self._dayu_size)

        margin = self.textMargins()
        margin.setRight(margin.right() + widget.width())
        self.setTextMargins(margin)
        self._main_layout.addWidget(widget)
        self._suffix_widget = widget
        return widget

    def setText(self, text: str):  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        """Override setText save text to history"""
        self.setProperty("history", "{}\n{}".format(self.property("history"), text))
        return super().setText(text)

    def clear(self):
        """Override clear to clear history"""
        self.setProperty("history", "")
        return super().clear()

    def search_with_close(self):
        """Add a search icon button for MLineEdit."""
        suffix_button = MToolButton().icon_only().svg("close_line.svg")
        suffix_button.clicked.connect(self.clear)
        self.set_suffix_widget(suffix_button)
        self.setPlaceholderText("Enter key word to search...")
        return self

    def search_with_button(self, text: str = "Search"):
        """Add a MPushButton to suffix for MLineEdit"""
        _suffix_button = MPushButton(text=text).primary()
        _suffix_button.clicked.connect(self.returnPressed)
        _suffix_button.setFixedWidth(100)
        self.set_suffix_widget(_suffix_button)
        self.setPlaceholderText("Enter key word to search...")
        return self

    def error(self):
        """A a toolset to MLineEdit to store error info with red style"""

        @QtCore.Slot()
        def _on_show_detail(self: MLineEdit):
            dialog = QtWidgets.QTextEdit(self)
            dialog.setReadOnly(True)
            geo = QtWidgets.QApplication.primaryScreen().geometry()
            dialog.setGeometry(
                geo.width() // 2, geo.height() // 2, geo.width() // 4, geo.height() // 4
            )
            dialog.setWindowTitle("Error Detail Information")
            dialog.setText(self.property("history"))
            dialog.setWindowFlags(QtCore.Qt.WindowType.Dialog)
            dialog.show()

        self.setProperty("dayu_type", "error")
        self.setReadOnly(True)
        _suffix_button = MToolButton().icon_only().svg("detail_line.svg")
        _suffix_button.clicked.connect(functools.partial(_on_show_detail, self))
        self.set_suffix_widget(_suffix_button)
        self.setPlaceholderText("Error information will be here...")
        return self

    def file(self, filters: list[str] | None = None):
        """Add a MClickBrowserFileToolButton for MLineEdit to select file"""
        _suffix_button = MClickBrowserFileToolButton()
        _suffix_button.sig_file_changed.connect(self.setText)
        _suffix_button.set_dayu_filters(filters or [])
        self.textChanged.connect(_suffix_button.set_dayu_path)
        self.set_suffix_widget(_suffix_button)
        self.setPlaceholderText("Click button to browser files")
        return self

    def save_file(self, filters: list[str] | None = None):
        """Add a MClickSaveFileToolButton for MLineEdit to set save file"""
        _suffix_button = MClickSaveFileToolButton()
        _suffix_button.sig_file_changed.connect(self.setText)
        _suffix_button.set_dayu_filters(filters or [])
        self.textChanged.connect(_suffix_button.set_dayu_path)
        self.set_suffix_widget(_suffix_button)
        self.setPlaceholderText("Click button to set save file")
        return self

    def folder(self):
        """Add a MClickBrowserFolderToolButton for MLineEdit to select folder"""
        _suffix_button = MClickBrowserFolderToolButton()
        _suffix_button.sig_folder_changed.connect(self.setText)
        self.textChanged.connect(_suffix_button.set_dayu_path)
        self.set_suffix_widget(_suffix_button)
        self.setPlaceholderText("Click button to browser folder")
        return self

    def huge(self):
        """Set MLineEdit to huge size"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MLineEdit to large size"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MLineEdit to  medium"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MLineEdit to small size"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MLineEdit to tiny size"""
        self.set_dayu_size(MTheme().tiny)
        return self

    def password(self):
        """Set MLineEdit to password echo mode"""
        self.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        return self
