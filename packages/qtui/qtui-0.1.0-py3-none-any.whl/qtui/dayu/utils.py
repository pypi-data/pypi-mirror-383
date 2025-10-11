"""
Some helper functions for handling color and formatter.
"""

from __future__ import annotations

import datetime as dt
import math
import threading
from collections.abc import Iterable
from functools import singledispatch, wraps
from pathlib import Path
from typing import Any, TypeVar, cast

from qtpy import QtCore, QtGui, QtWidgets

from .qt import MIcon, get_scale_factor
from .types import MenuItemData

T = TypeVar("T")


def get_static_file(file_name: str) -> Path:
    """
    Args:
        file_name: The name of the file in the static folder.

    Returns:
        The full path of the file.
    """
    path = Path(__file__).parent / "static" / file_name

    if not path.is_file() or not path.exists():
        raise FileNotFoundError(f"File {path} not found")
    return path


def from_list_to_nested_dict(
    input_arg: Iterable[str], sep: str = "/"
) -> list[MenuItemData]:
    """
    A help function to convert the list of string to nested dict
    :param input_arg: a list/tuple/set of string
    :param sep: a separator to split input string
    :return: a list of nested dict
    """

    result: list[MenuItemData] = []
    for item in input_arg:
        components = item.strip(sep).split(sep)
        component_count = len(components)
        current = result
        for i, comp in enumerate(components):
            atom: MenuItemData | None = None
            for x in current:
                if x.get("value") == comp:
                    atom = x
                    break

            if atom is None:
                atom = MenuItemData(value=comp, label=comp, children=[])
                current.append(atom)
            current = atom.get("children", [])
            if i == component_count - 1:
                atom.pop("children")

    return result


def fade_color(color: str, alpha: str) -> str:
    """
    Fade color with given alpha.
    eg. fade_color('#ff0000', '10%) => 'rgba(255, 0, 0, 10%)'

    Args:
        color: string, hex digit format '#RRGGBB'
        alpha: string, percent 'number%'
    Returns:
        qss/css color format rgba(r, g, b, a)
    """
    q_color = QtGui.QColor(color)
    return f"rgba({q_color.red()}, {q_color.green()}, {q_color.blue()}, {alpha})"


def generate_color(primary_color: str | QtGui.QColor, index: int) -> str:
    """
    Reference to ant-design color system algorithm.

    Args:
        primary_color: base color. #RRGGBB
        index: color step. 1-10 from light to dark
    Returns:
        result color
    """

    hue_step = 2
    saturation_step = 16
    saturation_step2 = 5
    brightness_step1 = 5
    brightness_step2 = 15
    light_color_count = 5
    dark_color_count = 4

    def _get_hue(color: QtGui.QColor, i: int, is_light: bool) -> float:
        h_comp = color.hue()
        if 60 <= h_comp <= 240:
            hue = h_comp - hue_step * i if is_light else h_comp + hue_step * i
        else:
            hue = h_comp + hue_step * i if is_light else h_comp - hue_step * i
        if hue < 0:
            hue += 359
        elif hue >= 359:
            hue -= 359
        return hue / 359.0

    def _get_saturation(color: QtGui.QColor, i: int, is_light: bool) -> float:
        s_comp = color.saturationF() * 100
        if is_light:
            saturation = s_comp - saturation_step * i
        elif i == dark_color_count:
            saturation = s_comp + saturation_step
        else:
            saturation = s_comp + saturation_step2 * i
        saturation = min(100.0, saturation)
        if is_light and i == light_color_count and saturation > 10:
            saturation = 10
        saturation = max(6.0, saturation)
        return round(saturation * 10) / 1000.0

    def _get_value(color: QtGui.QColor, i: int, is_light: bool) -> float:
        v_comp = color.valueF()
        if is_light:
            return min((v_comp * 100 + brightness_step1 * i) / 100, 1.0)
        return max((v_comp * 100 - brightness_step2 * i) / 100, 0.0)

    light = index <= 6
    hsv_color = (
        QtGui.QColor(primary_color) if isinstance(primary_color, str) else primary_color
    )
    index = light_color_count + 1 - index if light else index - light_color_count - 1
    return QtGui.QColor.fromHsvF(
        _get_hue(hsv_color, index, light),
        _get_saturation(hsv_color, index, light),
        _get_value(hsv_color, index, light),
    ).name()


def real_model(
    item: QtCore.QAbstractItemModel
    | QtCore.QSortFilterProxyModel
    | QtCore.QModelIndex
    | None,
) -> QtCore.QAbstractItemModel | None:
    if isinstance(item, QtCore.QSortFilterProxyModel):
        return item.sourceModel()
    elif isinstance(item, QtCore.QModelIndex):
        return item.model()
    return item


def real_index(index: QtCore.QModelIndex) -> QtCore.QModelIndex:
    """
    Get the source index whenever user give a source index or proxy index.
    """
    model = index.model()
    if isinstance(model, QtCore.QSortFilterProxyModel):
        return model.mapToSource(index)
    return index


def get_obj_value(
    data_obj: dict[str, Any] | object, attr: str, default: Any = None
) -> Any:
    """Get dict's key or object's attribute with given attr"""
    if isinstance(data_obj, dict):
        return cast(dict[str, Any], data_obj).get(attr, default)
    return getattr(data_obj, attr, default)


def set_obj_value(data_obj: dict[str, Any] | object, attr: str, value: Any) -> None:
    """Set dict's key or object's attribute with given attr and value"""
    if isinstance(data_obj, dict):
        return cast(dict[str, Any], data_obj).update({attr: value})
    return setattr(data_obj, attr, value)


def has_obj_value(data_obj: dict[str, Any] | object, attr: str) -> bool:
    """Return weather dict has the given key or object has the given attribute."""
    if isinstance(data_obj, dict):
        return attr in data_obj
    return hasattr(data_obj, attr)


def apply_formatter(formatter: Any, *args: Any, **kwargs: Any) -> Any:
    """
    Used for QAbstractModel data method.
    Config a formatter for one field, apply the formatter with the index data.

    Args:
        formatter: formatter. It can be None/dict/callable or just any type of value
        args:
        kwargs:
    Returns:
        apply the formatter with args and kwargs
    """
    if formatter is None:
        return args[0]
    elif isinstance(formatter, dict):
        return cast(dict[str, Any], formatter).get(args[0], None)
    elif callable(formatter):
        return formatter(*args, **kwargs)
    return formatter


@singledispatch
def display_formatter(input_other_type: Any) -> str:
    """
    Used for QAbstractItemModel data method for Qt.DisplayRole
    Format any input value to a string.
    :param input_other_type: any type value
    :return: str
    """
    return str(input_other_type)  # this function never reached


@display_formatter.register(dict)
def _(input_dict: dict[str, Any]) -> str:
    if "name" in input_dict:
        return display_formatter(input_dict.get("name"))
    elif "code" in input_dict:
        return display_formatter(input_dict.get("code"))
    return str(input_dict)


@display_formatter.register(list)
def _(input_list: list[Any]) -> str:
    result: list[str] = []
    for i in input_list:
        result.append(str(display_formatter(i)))
    return ",".join(result)


@display_formatter.register(bytes)
def _(input_str: bytes) -> str:
    # ['utf-8', 'windows-1250', 'windows-1252', 'ISO-8859-1']
    return input_str.decode("windows-1252")
    # return obj.decode()


@display_formatter.register(str)
def _(input_unicode: str) -> str:
    return input_unicode


@display_formatter.register(type(None))
def _(input_none: None) -> str:
    return "--"


@display_formatter.register(int)
def _(input_int: int) -> str:
    return str(input_int)


@display_formatter.register(float)
def _(input_float: float) -> str:
    return f"{round(input_float, 2):.2f}"


@display_formatter.register(object)
def _(input_object: object) -> str:
    if hasattr(input_object, "name"):
        return display_formatter(input_object.name)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
    if hasattr(input_object, "code"):
        return display_formatter(input_object.code)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
    return str(input_object)


@display_formatter.register(dt.datetime)
def _(input_datetime: dt.datetime) -> str:
    return input_datetime.strftime("%Y-%m-%d %H:%M:%S")


def font_formatter(setting_dict: dict[str, Any]) -> QtGui.QFont:
    """
    Used for QAbstractItemModel data method for Qt.FontRole

    Args:
        setting_dict: a dict with underline and bold
    Returns:
        a QFont instance with given style
    """
    _font = QtGui.QFont()
    _font.setUnderline(setting_dict.get("underline") or False)
    _font.setBold(setting_dict.get("bold") or False)
    return _font


@singledispatch
def icon_formatter(input_other_type: Any) -> QtGui.QIcon:
    """
    Used for QAbstractItemModel data method for Qt.DecorationRole
    A helper function to easy get QIcon.
    The input can be dict/object, string, None, tuple(file_path, fill_color)

    Args:
        input_other_type:
    Returns:
        a QIcon instance
    """
    return input_other_type  # this function never reached


@icon_formatter.register(dict)
def _(input_dict: dict[str, Any]) -> QtGui.QIcon:
    attr_list = ["icon"]
    path = next((get_obj_value(input_dict, attr) for attr in attr_list), None)
    return icon_formatter(path)


@icon_formatter.register(QtGui.QIcon)
def _(input_dict: QtGui.QIcon) -> QtGui.QIcon:
    return input_dict


@icon_formatter.register(object)
def _(input_object: object) -> QtGui.QIcon:
    attr_list = ["icon"]
    path = next((get_obj_value(input_object, attr) for attr in attr_list), None)
    return icon_formatter(path)


@icon_formatter.register(str)
def _(input_string: str) -> QtGui.QIcon:
    return MIcon(input_string)


@icon_formatter.register(tuple)
def _(input_tuple: tuple[str, str]) -> QtGui.QIcon:
    return MIcon(*input_tuple)


@icon_formatter.register(type(None))
def _(input_none: None) -> QtGui.QIcon:
    return icon_formatter("confirm_fill.svg")


def overflow_format(num: int, overflow: int) -> str:
    """
    Give a integer, return a string.
    When this integer is large than given overflow, return "overflow+"
    """
    return str(num) if num <= overflow else f"{overflow}+"


def get_percent(value: int, minimum: int, maximum: int) -> float:
    """
    Get a given value's percent in the range.

    Args:
        value: value
        minimum: the range's minimum value
        maximum: the range's maximum value
    Returns:
        percent float
    """
    if minimum == maximum:
        # reference from qprogressbar.cpp
        # If max and min are equal and we get this far, it means that the
        # progress bar has one step and that we are on that step. Return
        # 100% here in order to avoid division by zero further down.
        return 100
    return max(0, min(100, (value - minimum) * 100 / (maximum - minimum)))


def get_total_page(total: int, per: int) -> int:
    """
    Get the page count.
    :param total: total count
    :param per: count per page
    :return: page count int
    """
    return math.ceil(1.0 * total / per)


def get_page_display_string(current: int, per: int, total: int) -> str:
    """
    Get the format string x - x of xx
    :param current: current page
    :param per: count per page
    :param total: total count
    :return: str
    """
    return f"{((current - 1) * per + 1) if current else 0} - {min(total, current * per)} of {total}"  # noqa: E501


def read_settings(organization: str, app_name: str) -> dict[str, Any]:
    settings = QtCore.QSettings(
        QtCore.QSettings.Format.IniFormat,
        QtCore.QSettings.Scope.UserScope,
        organization,
        app_name,
    )
    result_dict = {key: settings.value(key) for key in settings.childKeys()}
    for grp_name in settings.childGroups():
        settings.beginGroup(grp_name)
        result_dict.update(
            {grp_name + "/" + key: settings.value(key) for key in settings.childKeys()}
        )
        settings.endGroup()
    return result_dict


def get_fit_geometry() -> QtCore.QRect:
    geo = next(
        (screen.availableGeometry() for screen in QtWidgets.QApplication.screens()),
        None,
    )
    if geo is None:
        return QtCore.QRect(0, 0, 0, 0)
    return QtCore.QRect(
        geo.width() // 4, geo.height() // 4, geo.width() // 2, geo.height() // 2
    )


def convert_to_round_pixmap(orig_pix: QtGui.QPixmap) -> QtGui.QPixmap:
    w = min(orig_pix.width(), orig_pix.height())
    pix_map = QtGui.QPixmap(w, w)
    pix_map.fill(QtCore.Qt.GlobalColor.transparent)

    painter = QtGui.QPainter(pix_map)
    painter.setRenderHints(
        QtGui.QPainter.RenderHint.Antialiasing
        | QtGui.QPainter.RenderHint.SmoothPixmapTransform
    )

    path = QtGui.QPainterPath()
    path.addEllipse(0, 0, w, w)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, w, w, orig_pix)
    return pix_map


def generate_text_pixmap(
    width: int,
    height: int,
    text: str,
    alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignCenter,
    bg_color: str = "",
) -> QtGui.QPixmap:
    from .theme import MTheme

    bg_color = bg_color or MTheme().background_in_color
    # draw a pixmap with text
    pix_map = QtGui.QPixmap(width, height)
    pix_map.fill(QtGui.QColor(bg_color))
    painter = QtGui.QPainter(pix_map)
    painter.setRenderHints(QtGui.QPainter.RenderHint.TextAntialiasing)
    font = painter.font()
    font.setFamily(MTheme().font_family)
    painter.setFont(font)
    painter.setPen(QtGui.QPen(QtGui.QColor(MTheme().secondary_text_color)))

    font_metrics = painter.fontMetrics()
    text_width = font_metrics.horizontalAdvance(text)
    text_height = font_metrics.height()
    x = width // 2 - text_width // 2
    y = height // 2 - text_height // 2
    if alignment & QtCore.Qt.AlignmentFlag.AlignLeft:
        x = 0
    elif alignment & QtCore.Qt.AlignmentFlag.AlignRight:
        x = width - text_width
    elif alignment & QtCore.Qt.AlignmentFlag.AlignTop:
        y = 0
    elif alignment & QtCore.Qt.AlignmentFlag.AlignBottom:
        y = height - text_height

    painter.drawText(x, y, text)
    painter.end()
    return pix_map


def get_color_icon(color: str | QtGui.QColor, size: int = 24) -> QtGui.QIcon:
    scale_x, _ = get_scale_factor()
    pix = QtGui.QPixmap(int(size * scale_x), int(size * scale_x))
    q_color = color
    if isinstance(color, str):
        if color.startswith("#"):
            q_color = QtGui.QColor(str)
        elif color.count(",") == 2:
            q_color = QtGui.QColor(*tuple(map(int, color.split(","))))
    pix.fill(q_color)
    return QtGui.QIcon(pix)


def str_to_qbytearray(string: str):
    return QtCore.QByteArray(string.encode())


def qbytearray_to_str(qbytearray: QtCore.QByteArray):
    return str(qbytearray.data().decode())  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]


def singleton(cls: type[T]) -> type[T]:
    """스레드 안전한 싱글톤 데코레이터"""
    instances: dict[type[T], T] = {}
    lock = threading.Lock()

    @wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> T:
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    # 클래스 메서드로 명시적 접근 제공
    cls.get_instance = classmethod(lambda c, *a, **k: get_instance(*a, **k))  # pyright: ignore[reportAttributeAccessIssue]
    cls.clear_instance = classmethod(lambda c: instances.pop(cls, None))  # pyright: ignore[reportAttributeAccessIssue]

    return get_instance  # pyright: ignore[reportReturnType]
