from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from qtpy import QtCore, QtWidgets

from . import utils
from .completer import MCompleter
from .menu import MMenu
from .mixin import cursor_mixin, focus_shadow_mixin, property_mixin
from .theme import MTheme
from .widget import MWidget


@property_mixin
@cursor_mixin
@focus_shadow_mixin
class MComboBox(QtWidgets.QComboBox, MWidget):
    value_changed = QtCore.Signal(object)

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self.filter_model = QtCore.QSortFilterProxyModel(self)
        self.filter_model.setFilterCaseSensitivity(
            QtCore.Qt.CaseSensitivity.CaseInsensitive
        )
        self.filter_model.setSourceModel(self.model())

        self._completer = MCompleter(self)
        self._completer.setCompletionMode(
            QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion
        )
        self._completer.setModel(self.filter_model)

        self._root_menu: MMenu | None = None
        self._display_formatter = utils.display_formatter

        self.setEditable(True)
        self.line_edit = cast(QtWidgets.QLineEdit, self.lineEdit())
        self.line_edit.setReadOnly(True)
        self.line_edit.setTextMargins(4, 0, 4, 0)
        self.line_edit.setStyleSheet("background-color:transparent")
        self.line_edit.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.line_edit.installEventFilter(self)
        self._has_custom_view: bool = False
        self.set_value("")
        self.set_placeholder("Please Select")
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self._dayu_size: int = MTheme().default_size
        MTheme().apply(self)

    def search(self):
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setEditable(True)

        self.setCompleter(self._completer)

        self.line_edit.setReadOnly(False)
        self.line_edit.returnPressed.disconnect()
        self.line_edit.textEdited.connect(self.filter_model.setFilterFixedString)
        self._completer.activated.connect(self._completer_activated)

    def _completer_activated(self, text: str) -> None:
        if text:
            self.setCurrentIndex(self.findText(text))

    def _set_searchable(self, value: bool):
        """search property to True then trigger search"""
        if value:
            self.search()

    def setModel(self, model: QtCore.QAbstractItemModel):  # noqa: N802
        super().setModel(model)
        self.filter_model.setSourceModel(model)
        self._completer.setModel(self.filter_model)

    def setModelColumn(self, column: int):  # noqa: N802
        self._completer.setCompletionColumn(column)
        self.filter_model.setFilterKeyColumn(column)
        super().setModelColumn(column)

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
        self.line_edit.setProperty("dayu_size", value)
        self.style().polish(self)

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def set_formatter(self, func: Callable[[Any], str]):
        self._display_formatter = func

    def set_placeholder(self, text: str):
        """Display the text when no item selected."""
        self.line_edit.setPlaceholderText(text)

    def set_value(self, value: Any):
        self.setProperty("value", value)

    def _set_value(self, value: Any):
        self.line_edit.setProperty("text", self._display_formatter(value))
        if self._root_menu:
            self._root_menu.set_value(value)

    def set_menu(self, menu: MMenu):
        self._root_menu = menu
        self._root_menu.value_changed.connect(self.value_changed)
        self._root_menu.value_changed.connect(self.set_value)

    def setView(self, *args: Any, **kwargs: Any):  # noqa: N802
        """Override setView to flag _has_custom_view variable."""
        self._has_custom_view = True
        super().setView(*args, **kwargs)

    def showPopup(self) -> None:  # noqa: N802
        """Override default showPopup. When set custom menu, show the menu instead."""
        if self._has_custom_view or self._root_menu is None:
            super().showPopup()
        else:
            super().hidePopup()
            self._root_menu.popup(self.mapToGlobal(QtCore.QPoint(0, self.height())))

    def eventFilter(self, widget: QtWidgets.QWidget, event: QtCore.QEvent) -> bool:  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        if (
            widget is self.line_edit
            and self.line_edit.isReadOnly()
            and self.isEnabled()
            and event.type() == QtCore.QEvent.Type.MouseButtonPress
        ):
            self.showPopup()
        return super().eventFilter(widget, event)

    def huge(self):
        """Set MComboBox to huge size"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MComboBox to large size"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MComboBox to  medium"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MComboBox to small size"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MComboBox to tiny size"""
        self.set_dayu_size(MTheme().tiny)
        return self
