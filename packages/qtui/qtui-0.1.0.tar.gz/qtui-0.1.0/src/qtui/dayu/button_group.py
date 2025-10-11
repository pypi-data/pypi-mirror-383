import functools
from collections.abc import Sequence
from typing import Generic, TypeVar, cast

from qtpy import QtCore, QtGui, QtWidgets

from .check_box import MCheckBox
from .menu import MMenu
from .push_button import MPushButton
from .qt import get_scale_factor
from .radio_button import MRadioButton
from .tool_button import MToolButton
from .types import MButtonGroupData
from .widget import MWidget

T = TypeVar("T", bound=QtWidgets.QAbstractButton)


class MButtonGroup(QtWidgets.QButtonGroup, Generic[T]):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)

    def button(self, id: int) -> T:
        return cast(T, super().button(id))

    def buttons(self) -> list[T]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return [cast(T, b) for b in super().buttons()]


class MButtonGroupBase(QtWidgets.QWidget, MWidget, Generic[T]):  # pyright: ignore[reportGeneralTypeIssues]
    def __init__(
        self,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)

        self._main_layout = QtWidgets.QBoxLayout(
            QtWidgets.QBoxLayout.Direction.LeftToRight
            if orientation == QtCore.Qt.Orientation.Horizontal
            else QtWidgets.QBoxLayout.Direction.TopToBottom
        )

        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._main_layout)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

        self._button_group = MButtonGroup[T]()

        self._orientation = (
            "horizontal"
            if orientation == QtCore.Qt.Orientation.Horizontal
            else "vertical"
        )

    def set_spacing(self, value: int) -> None:
        self._main_layout.setSpacing(value)

    def get_button_group(self) -> QtWidgets.QButtonGroup:
        return self._button_group

    def get_button(self, id: int) -> T:
        return self._button_group.button(id)

    def get_buttons(self) -> list[T]:
        return self._button_group.buttons()

    def create_button(self, data_dict: MButtonGroupData) -> T:
        raise NotImplementedError()

    def add_button(
        self, data_dict: MButtonGroupData | str | QtGui.QIcon, index: int | None = None
    ) -> T:
        if isinstance(data_dict, str):
            data_dict = MButtonGroupData(text=data_dict)

        elif isinstance(data_dict, QtGui.QIcon):
            data_dict = MButtonGroupData(icon=data_dict)

        button = self.create_button(data_dict)
        button.setProperty("combine", self._orientation)

        text = data_dict.get("text")
        icon = data_dict.get("icon")
        data = data_dict.get("data")
        checked = data_dict.get("checked")
        shortcut = data_dict.get("shortcut")
        tooltip = data_dict.get("tooltip")
        checkable = data_dict.get("checkable")
        clicked = data_dict.get("clicked")
        toggled = data_dict.get("toggled")

        if text:
            button.setProperty("text", text)

        if icon:
            button.setProperty("icon", icon)

        if data:
            button.setProperty("data", data)

        if checked:
            button.setProperty("checked", checked)

        if shortcut:
            button.setProperty("shortcut", shortcut)

        if tooltip:
            button.setProperty("toolTip", tooltip)

        if checkable:
            button.setProperty("checkable", checkable)

        if clicked:
            button.clicked.connect(clicked)

        if toggled:
            button.toggled.connect(toggled)

        if index is None:
            self._button_group.addButton(button)
        else:
            self._button_group.addButton(button, index)

        self._main_layout.insertWidget(self._main_layout.count(), button)

        return button

    def set_button_list(
        self, button_list: Sequence[MButtonGroupData | str | QtGui.QIcon]
    ) -> None:
        for button in self.get_buttons():
            self._button_group.removeButton(button)
            self._main_layout.removeWidget(button)
            button.setVisible(False)

        for index, data_dict in enumerate(button_list):
            button = self.add_button(data_dict, index)

            if index == 0:
                button.setProperty("position", "left")
            elif index == len(button_list) - 1:
                button.setProperty("position", "right")
            else:
                button.setProperty("position", "center")


class MPushButtonGroup(MButtonGroupBase[MPushButton]):
    def __init__(
        self,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(orientation=orientation, parent=parent)

        self.set_spacing(1)
        self.set_dayu_type(MPushButton.ButtonType.Primary)
        self._button_group.setExclusive(False)

    def create_button(self, data_dict: MButtonGroupData) -> MPushButton:
        button = MPushButton()
        button.set_dayu_size(data_dict.get("dayu_size", self._dayu_size))
        button.set_dayu_type(data_dict.get("dayu_type", self._dayu_type))

        return button


class MCheckBoxGroup(MButtonGroupBase[MCheckBox]):
    checked_changed = QtCore.Signal(list)

    def __init__(
        self,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(orientation=orientation, parent=parent)
        scale_x, _ = get_scale_factor()
        self.set_spacing(int(15 * scale_x))
        self._button_group.setExclusive(False)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self._dayu_checked = []
        self._context_menu_show = True
        self._context_menu_select_all = "Select All"
        self._context_menu_select_none = "Select None"
        self._context_menu_select_invert = "Select Invert"

        self.customContextMenuRequested.connect(self._on_context_menu_requested)
        self._button_group.buttonClicked.connect(self._on_map_signal)

    def create_button(self, data_dict: MButtonGroupData) -> MCheckBox:
        return MCheckBox()

    def set_context_menu_properties(
        self,
        show: bool = True,
        select_all: str = "Select All",
        select_none: str = "Select None",
        select_invert: str = "Select Invert",
    ) -> None:
        self._context_menu_show = show
        self._context_menu_select_all = select_all
        self._context_menu_select_none = select_none
        self._context_menu_select_invert = select_invert
        if show:
            self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        else:
            self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)

    @QtCore.Slot(QtCore.QPoint)
    def _on_context_menu_requested(self, point: QtCore.QPoint) -> None:
        context_menu = MMenu(parent=self)
        action_select_all = context_menu.addAction(self._context_menu_select_all)
        action_select_none = context_menu.addAction(self._context_menu_select_none)
        action_select_invert = context_menu.addAction(self._context_menu_select_invert)
        action_select_all.triggered.connect(
            functools.partial(self._on_set_select, True)
        )
        action_select_none.triggered.connect(
            functools.partial(self._on_set_select, False)
        )
        action_select_invert.triggered.connect(
            functools.partial(self._on_set_select, None)
        )
        context_menu.exec(QtGui.QCursor.pos() + QtCore.QPoint(10, 10))

    @QtCore.Slot(bool)
    def _on_set_select(self, state: bool | None) -> None:
        for check_box in self.get_buttons():
            if state is None:
                old_state = check_box.isChecked()
                check_box.setChecked(not old_state)
            else:
                check_box.setChecked(state)
        self._on_map_signal()

    @QtCore.Slot(int)
    def _on_map_signal(self, state: int | None = None) -> None:
        self.checked_changed.emit(
            [
                check_box.text()
                for check_box in self.get_buttons()
                if check_box.isChecked()
            ]
        )

    def set_dayu_checked(self, value: list[str] | str) -> None:
        if not isinstance(value, list):
            value = [value]

        if value == self.get_dayu_checked():
            return

        self._dayu_checked = value
        for check_box in self.get_buttons():
            flag = (
                QtCore.Qt.CheckState.Checked
                if check_box.text() in value
                else QtCore.Qt.CheckState.Unchecked
            )

            if flag != check_box.checkState():
                check_box.setCheckState(flag)

        self.checked_changed.emit(value)

    def get_dayu_checked(self) -> list[str]:
        return [
            check_box.text()
            for check_box in self.get_buttons()
            if check_box.isChecked()
        ]

    dayu_checked = QtCore.Property(
        "QVariantList",  # pyright: ignore[reportArgumentType]
        get_dayu_checked,
        set_dayu_checked,
        notify=checked_changed,
    )


class MRadioButtonGroup(MButtonGroupBase[MRadioButton]):
    """
    Property:
        dayu_checked
    """

    checked_changed = QtCore.Signal(int)

    def __init__(
        self,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(orientation=orientation, parent=parent)
        scale_x, _ = get_scale_factor()
        self.set_spacing(int(15 * scale_x))
        self._button_group.setExclusive(True)
        self._button_group.buttonClicked.connect(
            lambda: self.checked_changed.emit(self._button_group.checkedId())
        )

    def create_button(self, data_dict: MButtonGroupData) -> MRadioButton:
        return MRadioButton()

    def set_dayu_checked(self, value: int) -> None:
        if value == self.get_dayu_checked():
            return

        button = self._button_group.button(value)
        if button:
            button.setChecked(True)
            self.checked_changed.emit(value)
        else:
            print("error")

    def get_dayu_checked(self) -> int:
        return self._button_group.checkedId()

    dayu_checked = QtCore.Property(
        int,
        get_dayu_checked,
        set_dayu_checked,
        notify=checked_changed,
    )


class MToolButtonGroup(MButtonGroupBase[MToolButton]):
    checked_changed = QtCore.Signal(int)

    def __init__(
        self,
        size: int | None = None,
        type: str | None = None,
        exclusive: bool = False,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(orientation=orientation, parent=parent)
        self.set_spacing(1)
        self._button_group.setExclusive(exclusive)
        self._size = size
        self._type = type
        self._button_group.buttonClicked.connect(
            lambda: self.checked_changed.emit(self._button_group.checkedId())
        )

    def create_button(self, data_dict: MButtonGroupData) -> MToolButton:
        button = MToolButton()
        svg = data_dict.get("svg")
        text = data_dict.get("text")
        icon = data_dict.get("icon")
        if svg:
            button.svg(svg)
        if text:
            if svg or icon:
                button.text_beside_icon()
            else:
                button.text_only()
        else:
            button.icon_only()
        return button

    def set_dayu_checked(self, value: int) -> None:
        if value == self.get_dayu_checked():
            return
        button = self._button_group.button(value)
        if button:
            button.setChecked(True)
            self.checked_changed.emit(value)
        else:
            raise ValueError("button not found")

    def get_dayu_checked(self) -> int:
        return self._button_group.checkedId()

    dayu_checked = QtCore.Property(
        int,
        get_dayu_checked,
        set_dayu_checked,
        notify=checked_changed,
    )
