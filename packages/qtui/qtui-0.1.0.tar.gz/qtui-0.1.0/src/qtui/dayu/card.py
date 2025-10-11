from __future__ import annotations

from collections.abc import Callable

from qtpy import QtCore, QtGui, QtWidgets

from .avatar import MAvatar
from .divider import MDivider
from .label import MLabel
from .menu import MMenu
from .mixin import cursor_mixin, hover_shadow_mixin
from .theme import MTheme
from .tool_button import MToolButton
from .types import MCardTitleProps


@cursor_mixin
class MCard(QtWidgets.QWidget):
    def __init__(
        self,
        title: str = "",
        image: QtGui.QPixmap | None = None,
        size: int | None = None,
        extra: bool = False,
        extra_menus: list[tuple[str, Callable[[], None]]] | None = None,
        border: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)
        self._title_label = MLabel().h4()
        self._title_icon = MAvatar()
        self._title_icon_pixmap: QtGui.QPixmap | None = image
        self._title_divider = MDivider()
        self._extra_button = MToolButton().icon_only().svg("more.svg")
        self._extra_menus = extra_menus or []
        self._extra_button.clicked.connect(self._on_extra_menu_clicked)

        self._title_layout = QtWidgets.QHBoxLayout()
        self._title_layout.setContentsMargins(10, 10, 10, 10)
        self._title_layout.addWidget(self._title_icon)
        self._title_layout.addStretch()
        self._title_layout.addWidget(self._title_label)
        self._title_layout.addWidget(self._extra_button)

        self._content_layout = QtWidgets.QVBoxLayout()
        self._main_layout = QtWidgets.QVBoxLayout()
        self._main_layout.setSpacing(0)
        self._main_layout.setContentsMargins(1, 1, 1, 1)
        self._main_layout.addLayout(self._title_layout)
        self._main_layout.addWidget(self._title_divider)
        self._main_layout.addLayout(self._content_layout)
        self.setLayout(self._main_layout)

        size = size or MTheme().default_size
        self.set_title(title)
        self.set_icon(image)
        self.set_size(size)
        self.extra(extra)  # noqa: S610
        self.border(border)

    def get_more_button(self):
        return self._extra_button

    def set_title(self, title: str = "") -> None:
        if title:
            self._title_label.setText(title)
            self._title_label.setVisible(True)
            self._title_icon.setVisible(self._title_icon_pixmap is not None)
            self._title_divider.setVisible(True)
            self._main_layout.removeItem(self._title_layout)
            self._main_layout.insertLayout(0, self._title_layout)
        else:
            self._title_label.setVisible(False)
            self._title_icon.setVisible(False)
            self._title_divider.setVisible(False)
            self._main_layout.removeItem(self._title_layout)

    def set_icon(self, icon: QtGui.QPixmap | None = None) -> None:
        if icon:
            self._title_icon.set_dayu_image(icon)
            self._title_icon.setVisible(True)
        else:
            self._title_icon.setVisible(False)

    def set_content(self, widget: QtWidgets.QWidget | None = None) -> None:
        if self._content_layout.count() > 0:
            if item := self._content_layout.itemAt(0).widget():
                item.deleteLater()

        if widget:
            self._content_layout.addWidget(widget)
        else:
            self._content_layout.addStretch()

    def set_size(self, size: int | None = None) -> None:
        if size:
            title_props_map: dict[int, MCardTitleProps] = {
                MTheme().large: MCardTitleProps(MLabel.LabelLevel.H2, 20),
                MTheme().medium: MCardTitleProps(MLabel.LabelLevel.H3, 15),
                MTheme().small: MCardTitleProps(MLabel.LabelLevel.H4, 10),
            }
            title_props = title_props_map.get(
                size, MCardTitleProps(MLabel.LabelLevel.H4, 10)
            )
            self._title_label.set_dayu_level(title_props.level)
            padding = title_props.padding
            self._title_layout.setContentsMargins(padding, padding, padding, padding)
            self._title_icon.set_dayu_size(size)

    def extra(self, show: bool = True) -> MCard:
        if show:
            self._extra_button.setVisible(True)
        else:
            self._extra_button.setVisible(False)
        return self

    def border(self, border: bool = True):
        self.setProperty("border", border)
        self.style().polish(self)
        return self

    def _on_extra_menu_clicked(self):
        context_menu = MMenu(parent=self)
        for name, callback in self._extra_menus:
            context_menu.addAction(name, callback)
        context_menu.exec(self.mapToGlobal(self._extra_button.geometry().bottomLeft()))


@hover_shadow_mixin
@cursor_mixin
class MMetaCard(QtWidgets.QWidget):
    def __init__(
        self,
        title: str = "",
        description: str = "",
        avatar: QtGui.QPixmap | None = None,
        cover: QtGui.QPixmap | None = None,
        extra: bool = False,
        extra_menus: list[tuple[str, Callable[[], None]]] | None = None,
        border: bool = True,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)
        self._title_label = MLabel().h4()
        self._description_label = MLabel().secondary()
        self._description_label.setWordWrap(True)
        self._description_label.set_elide_mode(QtCore.Qt.TextElideMode.ElideRight)
        self._avatar = MAvatar()
        self._cover_label = QtWidgets.QLabel()

        self._title_layout = QtWidgets.QHBoxLayout()
        self._title_layout.addWidget(self._title_label)
        self._title_layout.addStretch()
        self._extra_button = MToolButton(parent=self).icon_only().svg("more.svg")
        self._extra_menus = extra_menus or []
        self._extra_button.clicked.connect(self._on_extra_menu_clicked)
        self._title_layout.addWidget(self._extra_button)
        self._extra_button.setVisible(extra)

        content_layout = QtWidgets.QFormLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.addRow(self._avatar, self._title_layout)
        content_layout.addRow(self._description_label)

        self._button_layout = QtWidgets.QHBoxLayout()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.addWidget(self._cover_label)
        main_layout.addLayout(content_layout)
        main_layout.addLayout(self._button_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)
        self._cover_label.setFixedSize(QtCore.QSize(200, 200))

        self.set_title(title)
        self.set_description(description)
        self.set_avatar(avatar)
        self.set_cover(cover)
        self.border(border)

    def get_more_button(self):
        return self._extra_button

    def set_title(self, title: str = "") -> None:
        if title:
            self._title_label.setText(title)
            self._title_label.setVisible(True)
        else:
            self._title_label.setVisible(False)

    def set_description(self, description: str = "") -> None:
        if description:
            self._description_label.setText(description)
            self._description_label.setVisible(True)
        else:
            self._description_label.setVisible(False)

    def set_avatar(self, avatar: QtGui.QPixmap | None = None) -> None:
        if avatar:
            self._avatar.set_dayu_image(avatar)
            self._avatar.setVisible(True)
        else:
            self._avatar.setVisible(False)

    def set_cover(self, cover: QtGui.QPixmap | None = None) -> None:
        if cover:
            fixed_height = self._cover_label.width()
            self._cover_label.setPixmap(
                cover.scaledToWidth(
                    fixed_height, QtCore.Qt.TransformationMode.SmoothTransformation
                )
            )
            self._cover_label.setVisible(True)
        else:
            self._cover_label.setVisible(False)

    def border(self, border: bool = True) -> MMetaCard:
        self.setProperty("border", border)
        self.style().polish(self)
        return self

    def _on_extra_menu_clicked(self):
        context_menu = MMenu(parent=self)
        for name, callback in self._extra_menus:
            context_menu.addAction(name, callback)
        context_menu.exec(self.mapToGlobal(self._extra_button.geometry().bottomLeft()))
