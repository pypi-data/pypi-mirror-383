from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, NamedTuple, NotRequired, TypedDict

from qtpy import QtCore, QtGui, QtWidgets


class MBreadcrumbData(TypedDict):
    text: NotRequired[str]
    svg: NotRequired[str]
    tooltip: NotRequired[str]
    clicked: NotRequired[Callable[[], None]]


class MButtonGroupData(TypedDict):
    # default properties
    dayu_size: NotRequired[int]
    dayu_type: NotRequired[str]
    text: NotRequired[str]
    icon: NotRequired[QtGui.QIcon]
    data: NotRequired[Any]
    checked: NotRequired[bool]
    shortcut: NotRequired[str]
    tooltip: NotRequired[str]
    checkable: NotRequired[bool]
    clicked: NotRequired[Callable[..., Any]]
    toggled: NotRequired[Callable[..., Any]]

    # mtoolbutton properties
    svg: NotRequired[str]


class MCollapseData(TypedDict):
    title: NotRequired[str]
    content: NotRequired[QtWidgets.QWidget | None]
    expand: NotRequired[bool]
    closable: NotRequired[bool]
    parent: NotRequired[QtWidgets.QWidget | None]


class MCardData(TypedDict):
    title: NotRequired[str]
    image: NotRequired[QtGui.QPixmap | None]
    size: NotRequired[int]
    extra: NotRequired[bool]
    extra_menus: NotRequired[list[tuple[str, Callable[[], None]]] | None]
    border: NotRequired[bool]
    parent: NotRequired[QtWidgets.QWidget | None]


class MMetaCardData(TypedDict):
    title: NotRequired[str]
    description: NotRequired[str]
    avatar: NotRequired[QtGui.QPixmap | None]
    cover: NotRequired[QtGui.QPixmap | None]
    extra: NotRequired[bool]
    extra_menus: NotRequired[list[tuple[str, Callable[[], None]]] | None]
    border: NotRequired[bool]
    parent: NotRequired[QtWidgets.QWidget | None]


class MCardTitleProps(NamedTuple):
    level: int
    padding: int


class MixinData(TypedDict):
    data_name: str
    widget: QtWidgets.QWidget
    widget_property: str
    index: int | None
    callback: Callable[[], Any] | None


class MixinProps(TypedDict):
    value: Callable[[], Any] | Any
    required: bool
    bind: list[MixinData]


class MixinComputed(TypedDict):
    value: Any
    getter: Callable[[], Any] | None
    setter: Callable[[Any], None] | None
    required: bool
    bind: list[MixinData]


ModelData = dict[str, Any]


class HeaderData(TypedDict):
    label: str
    key: str
    width: NotRequired[float]
    default_filter: NotRequired[bool]
    editable: NotRequired[bool]
    selectable: NotRequired[bool]
    searchable: NotRequired[bool]
    checkable: NotRequired[bool]
    exclusive: NotRequired[bool]
    order: NotRequired[str]  # asc, desc
    color: NotRequired[
        Callable[[Any, ModelData], QtGui.QColor | str] | str
    ]  # Any is the data_obj
    bg_color: NotRequired[Callable[[Any, ModelData], QtGui.QColor | str] | str]
    display: NotRequired[Callable[[Any, ModelData], str]]
    align: NotRequired[str]  # left, center, right
    font: NotRequired[
        Callable[[Any, ModelData], dict[str, Any]]
    ]  # {underline: bool, bold: bool}
    icon: NotRequired[Callable[[Any, ModelData], Any] | str]
    tooltip: NotRequired[Callable[[Any, ModelData], str]]
    size: NotRequired[Callable[[Any, ModelData], QtCore.QSize]]
    hide: NotRequired[bool]
    reg: NotRequired[re.Pattern[str] | None]


class MenuItemData(TypedDict):
    value: str | int | float | MenuItemData
    label: str
    children: NotRequired[list[MenuItemData]]


@dataclass
class ItemViewMenuEvent:
    view: QtWidgets.QAbstractItemView
    selection: list[QtCore.QItemSelection]
    extra: Any
