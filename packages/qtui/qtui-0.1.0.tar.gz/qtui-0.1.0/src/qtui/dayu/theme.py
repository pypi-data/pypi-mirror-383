"""MTheme"""

from __future__ import annotations

import string
from enum import StrEnum
from pathlib import Path
from typing import Any

from qtpy import QtGui, QtWidgets

from .qt import get_scale_factor
from .utils import fade_color, generate_color, get_static_file, singleton

DEFAULT_STATIC_DIR = Path(__file__).parent / "static"


class QssTemplate(string.Template):
    delimiter = "@"
    idpattern = r"[_a-z][_a-z0-9]*"


@singleton
class MTheme:
    class ThemeType(StrEnum):
        Light = "light"
        Dark = "dark"
        System = "system"

    class GlobalColor(StrEnum):
        Blue = "#1890ff"
        Purple = "#722ed1"
        Cyan = "#13c2c2"
        Green = "#52c41a"
        Magenta = "#eb2f96"
        Pink = "#ef5b97"
        Red = "#f5222d"
        Orange = "#fa8c16"
        Yellow = "#fadb14"
        Volcano = "#fa541c"
        Geekblue = "#2f54eb"
        Lime = "#a0d911"
        Gold = "#faad14"
        Female = "#ef5b97"
        Male = "#4ebbff"

    def __init__(
        self, theme: ThemeType = ThemeType.Dark, primary_color: str = "orange"
    ):
        # if not self._initialized:
        super().__init__()
        default_qss_file = get_static_file("main.qss")
        self.default_qss = QssTemplate(default_qss_file.read_text())
        self._init_sizes()
        self._init_font()
        self._init_semantic_color()
        self.set_primary_color(primary_color or MTheme.GlobalColor.Blue)
        self.set_theme(theme)
        self.unit = "px"
        self.font_unit = "pt"

    def _init_font(self):
        """
        Init font size and family
        """

        self.font_family = f"{QtGui.QFont().families()}"
        self.font_size_base = 11
        self.font_size_large = self.font_size_base + 2
        self.font_size_small = self.font_size_base - 2
        self.h1_size = int(self.font_size_base * 2.71)
        self.h2_size = int(self.font_size_base * 2.12)
        self.h3_size = int(self.font_size_base * 1.71)
        self.h4_size = int(self.font_size_base * 1.41)

    def _init_semantic_color(self):
        """
        Init semantic color
        """
        self.info_color = MTheme.GlobalColor.Blue
        self.success_color = MTheme.GlobalColor.Green
        self.processing_color = MTheme.GlobalColor.Blue
        self.error_color = MTheme.GlobalColor.Red
        self.warning_color = MTheme.GlobalColor.Gold

        self.info_1 = fade_color(self.info_color, "15%")
        self.info_2 = generate_color(self.info_color, 2)
        self.info_3 = fade_color(self.info_color, "35%")
        self.info_4 = generate_color(self.info_color, 4)
        self.info_5 = generate_color(self.info_color, 5)
        self.info_6 = generate_color(self.info_color, 6)
        self.info_7 = generate_color(self.info_color, 7)
        self.info_8 = generate_color(self.info_color, 8)
        self.info_9 = generate_color(self.info_color, 9)
        self.info_10 = generate_color(self.info_color, 10)

        self.success_1 = fade_color(self.success_color, "15%")
        self.success_2 = generate_color(self.success_color, 2)
        self.success_3 = fade_color(self.success_color, "35%")
        self.success_4 = generate_color(self.success_color, 4)
        self.success_5 = generate_color(self.success_color, 5)
        self.success_6 = generate_color(self.success_color, 6)
        self.success_7 = generate_color(self.success_color, 7)
        self.success_8 = generate_color(self.success_color, 8)
        self.success_9 = generate_color(self.success_color, 9)
        self.success_10 = generate_color(self.success_color, 10)

        self.warning_1 = fade_color(self.warning_color, "15%")
        self.warning_2 = generate_color(self.warning_color, 2)
        self.warning_3 = fade_color(self.warning_color, "35%")
        self.warning_4 = generate_color(self.warning_color, 4)
        self.warning_5 = generate_color(self.warning_color, 5)
        self.warning_6 = generate_color(self.warning_color, 6)
        self.warning_7 = generate_color(self.warning_color, 7)
        self.warning_8 = generate_color(self.warning_color, 8)
        self.warning_9 = generate_color(self.warning_color, 9)
        self.warning_10 = generate_color(self.warning_color, 10)

        self.error_1 = fade_color(self.error_color, "15%")
        self.error_2 = generate_color(self.error_color, 2)
        self.error_3 = fade_color(self.error_color, "35%")
        self.error_4 = generate_color(self.error_color, 4)
        self.error_5 = generate_color(self.error_color, 5)
        self.error_6 = generate_color(self.error_color, 6)
        self.error_7 = generate_color(self.error_color, 7)
        self.error_8 = generate_color(self.error_color, 8)
        self.error_9 = generate_color(self.error_color, 9)
        self.error_10 = generate_color(self.error_color, 10)

        self.text_error_color = self.error_7
        self.text_color_inverse = "#fff"
        self.text_warning_color = self.warning_7

    def _init_sizes(self):
        """
        Init sizes
        """
        scale_factor_x, _ = get_scale_factor()
        self.border_radius_large = int(6 * scale_factor_x)
        self.border_radius_base = int(4 * scale_factor_x)
        self.border_radius_small = int(2 * scale_factor_x)
        self.huge = int(48 * scale_factor_x)
        self.large = int(40 * scale_factor_x)
        self.medium = int(32 * scale_factor_x)
        self.small = int(24 * scale_factor_x)
        self.tiny = int(18 * scale_factor_x)
        self.huge_icon = int((48 - 20) * scale_factor_x)
        self.large_icon = int((40 - 16) * scale_factor_x)
        self.medium_icon = int((32 - 12) * scale_factor_x)
        self.small_icon = int((24 - 10) * scale_factor_x)
        self.tiny_icon = int((18 - 8) * scale_factor_x)
        self.default_size = int(32 * scale_factor_x)
        self.badge_width_radius = int(8 * scale_factor_x)
        self.badge_width = int(16 * scale_factor_x)
        self.badge_dot = int(8 * scale_factor_x)
        self.badge_dot_radius = int(4 * scale_factor_x)
        self.drop_down_huge = int(20 * scale_factor_x)
        self.drop_down_large = int(16 * scale_factor_x)
        self.drop_down_medium = int(14 * scale_factor_x)
        self.drop_down_small = int(10 * scale_factor_x)
        self.drop_down_tiny = int(8 * scale_factor_x)
        self.spin_box_huge = int(28 * scale_factor_x)
        self.spin_box_large = int(26 * scale_factor_x)
        self.spin_box_medium = int(24 * scale_factor_x)
        self.spin_box_small = int(20 * scale_factor_x)
        self.spin_box_tiny = int(18 * scale_factor_x)
        self.spin_box_icon_huge = int(14 * scale_factor_x)
        self.spin_box_icon_large = int(12 * scale_factor_x)
        self.spin_box_icon_medium = int(10 * scale_factor_x)
        self.spin_box_icon_small = int(8 * scale_factor_x)
        self.spin_box_icon_tiny = int(6 * scale_factor_x)
        self.drag_border = int(2 * scale_factor_x)
        self.drag_border_radius = int(10 * scale_factor_x)
        self.drag_padding_x = int(20 * scale_factor_x)
        self.drag_padding_y = int(40 * scale_factor_x)
        self.drag_size = int(60 * scale_factor_x)
        self.switch_width_huge = int(58 * scale_factor_x)
        self.switch_height_huge = int(30 * scale_factor_x)
        self.switch_radius_huge = int(15 * scale_factor_x)
        self.switch_width_large = int(48 * scale_factor_x)
        self.switch_height_large = int(24 * scale_factor_x)
        self.switch_radius_large = int(12 * scale_factor_x)
        self.switch_width_medium = int(38 * scale_factor_x)
        self.switch_height_medium = int(19 * scale_factor_x)
        self.switch_radius_medium = int(9 * scale_factor_x)
        self.switch_width_small = int(28 * scale_factor_x)
        self.switch_height_small = int(14 * scale_factor_x)
        self.switch_radius_small = int(7 * scale_factor_x)
        self.switch_width_tiny = int(18 * scale_factor_x)
        self.switch_height_tiny = int(10 * scale_factor_x)
        self.switch_radius_tiny = int(5 * scale_factor_x)
        self.check_box_size = int(13 * scale_factor_x)
        self.check_box_spacing = int(4 * scale_factor_x)
        self.radio_size = int(14 * scale_factor_x)
        self.radio_radius = int(14 * scale_factor_x / 2.0)
        self.radio_spacing = int(4 * scale_factor_x)
        self.slider_height = int(4 * scale_factor_x)
        self.slider_radius = int(3 * scale_factor_x)
        self.slider_handle_size = int(8 * scale_factor_x)
        self.slider_handle_radius = int(8 * scale_factor_x / 1.5)
        self.progress_circle_default_radius = int(120 * scale_factor_x)
        self.progress_bar_size = int(12 * scale_factor_x)
        self.progress_bar_radius = int(12 * scale_factor_x / 2.0)
        self.toast_size = int(120 * scale_factor_x)
        self.toast_icon_size = int(60 * scale_factor_x)
        self.big_view_default_size = int(120 * scale_factor_x)
        self.big_view_max_size = int(400 * scale_factor_x)
        self.big_view_min_size = int(24 * scale_factor_x)
        self.indicator_padding = int(4 * scale_factor_x)
        self.indicator_size = int(8 * scale_factor_x)
        self.scroll_bar_size = int(12 * scale_factor_x)
        self.scroll_bar_min_length = int(20 * scale_factor_x)
        self.scroll_bar_margin = int(12 * scale_factor_x * 2) + 1
        self.scroll_bar_radius = int(12 * scale_factor_x / 2.0)

    def set_primary_color(self, color: str):
        self.primary_color = color
        self.primary_1 = generate_color(color, 1)
        self.primary_2 = generate_color(color, 2)
        self.primary_3 = generate_color(color, 3)
        self.primary_4 = generate_color(color, 4)
        self.primary_5 = generate_color(color, 5)
        self.primary_6 = generate_color(color, 6)
        self.primary_7 = generate_color(color, 7)
        self.primary_8 = generate_color(color, 8)
        self.primary_9 = generate_color(color, 9)
        self.primary_10 = generate_color(color, 10)
        self.item_hover_bg = self.primary_1
        self.hyperlink_style = f"""
        <style>
         a {{
            text-decoration: none;
            color: {self.primary_color};
        }}
        </style>"""

    def set_theme(self, theme: ThemeType):
        if theme == MTheme.ThemeType.Light:
            self._light()
        else:
            self._dark()
        self._set_icons(theme)

    def _set_icons(self, theme: ThemeType):
        """
        Set icons
        """
        pre_str = DEFAULT_STATIC_DIR.as_posix()
        suf_str = "" if theme == MTheme.ThemeType.Light else "_dark"
        url_prefix = f"{pre_str}/{{}}{suf_str}.png"
        url_prefix_2 = f"{pre_str}/{{}}.svg"
        self.icon_down = url_prefix.format("down_line")
        self.icon_up = url_prefix.format("up_line")
        self.icon_left = url_prefix.format("left_line")
        self.icon_right = url_prefix.format("right_line")
        self.icon_close = url_prefix.format("close_line")
        self.icon_calender = url_prefix.format("calendar_fill")
        self.icon_splitter = url_prefix.format("splitter")
        self.icon_float = url_prefix.format("float")
        self.icon_size_grip = url_prefix.format("size_grip")

        self.icon_check = url_prefix_2.format("check")
        self.icon_minus = url_prefix_2.format("minus")
        self.icon_circle = url_prefix_2.format("circle")
        self.icon_sphere = url_prefix_2.format("sphere")

    def _dark(self):
        self.title_color = "#ffffff"
        self.primary_text_color = "#d9d9d9"
        self.secondary_text_color = "#a6a6a6"
        self.disable_color = "#737373"
        self.border_color = "#1e1e1e"
        self.divider_color = "#262626"
        self.header_color = "#0a0a0a"
        self.icon_color = "#a6a6a6"

        self.background_color = "#323232"
        self.background_selected_color = "#292929"
        self.background_in_color = "#3a3a3a"
        self.background_out_color = "#494949"
        self.mask_color = fade_color(self.background_color, "90%")
        self.toast_color = "#555555"

    def _light(self):
        self.title_color = "#262626"
        self.primary_text_color = "#595959"
        self.secondary_text_color = "#8c8c8c"
        self.disable_color = "#e5e5e5"
        self.border_color = "#d9d9d9"
        self.divider_color = "#e8e8e8"
        self.header_color = "#fafafa"
        self.icon_color = "#8c8c8c"

        self.background_color = "#f8f8f9"
        self.background_selected_color = "#bfbfbf"
        self.background_in_color = "#ffffff"
        self.background_out_color = "#eeeeee"
        self.mask_color = fade_color(self.background_color, "90%")
        self.toast_color = "#333333"

    def get_color(self, prefix: str) -> str:
        return str(getattr(self, f"{prefix}_color"))

    def _theme_vals(self) -> dict[str, Any]:
        return {k: v for k, v in vars(self).items() if not k.startswith("_")}

    def apply(self, widget: QtWidgets.QWidget):
        widget.setStyleSheet(self.default_qss.substitute(self._theme_vals()))

    def change_theme(self, widget: QtWidgets.QWidget, theme: ThemeType, color: str):
        self.set_theme(theme)
        self.set_primary_color(color)
        self.apply(widget.window())
        for sub_widget in widget.window().findChildren(QtWidgets.QComboBox):
            self.apply(sub_widget)
        for sub_widget in widget.window().findChildren(QtWidgets.QSplitter):
            self.apply(sub_widget)

    def deco(self, cls: type[QtWidgets.QWidget]):
        original_init__ = cls.__init__

        def my__init__(instance: QtWidgets.QWidget, *args: Any, **kwargs: Any):
            original_init__(instance, *args, **kwargs)
            instance.setStyleSheet(self.default_qss.substitute(self._theme_vals()))

        def polish(instance: QtWidgets.QWidget):
            instance.style().polish(instance)

        cls.__init__ = my__init__
        cls.polish = polish  # pyright: ignore[reportAttributeAccessIssue]
        return cls
