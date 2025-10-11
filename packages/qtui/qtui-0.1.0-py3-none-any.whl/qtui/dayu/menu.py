from __future__ import annotations

import contextlib
import re
from collections.abc import Callable, Iterator, Sequence
from functools import partial
from typing import Any, cast

from qtpy import QtCore, QtGui, QtWidgets

from . import utils
from .line_edit import MLineEdit
from .mixin import property_mixin
from .popup import MPopup
from .types import MenuItemData


@property_mixin
class ScrollableMenuBase(QtWidgets.QMenu):
    delta_y: int = 0
    dirty: bool = True
    ignore_auto_scroll: bool = False

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._maximum_height = self.maximumHeight()
        self._action_rects: list[QtCore.QRect] = []

        self.scroll_timer = QtCore.QTimer(self, interval=50, singleShot=True)
        self.scroll_timer.timeout.connect(self.check_scroll)
        self.scroll_timer.setProperty("defaultInterval", 50)
        self.delay_timer = QtCore.QTimer(self, interval=100, singleShot=True)

        self.set_max_item_count(0)

    def _set_max_scroll_count(self, value: float):
        self.set_max_item_count(int(value * 2.2))

    @property
    def action_rects(self):
        if self.dirty or not self._action_rects:
            del self._action_rects[:]
            offset = self.offset()
            for action in self.actions():
                geo = super().actionGeometry(action)
                if offset:
                    geo.moveTop(geo.y() - offset)
                self._action_rects.append(geo)
            self.dirty = False
        return self._action_rects

    def iter_action_rects(self) -> Iterator[tuple[QtGui.QAction, QtCore.QRect]]:
        yield from zip(self.actions(), self.action_rects, strict=False)

    def set_max_item_count(self, count: int):
        style = self.style()
        opt = QtWidgets.QStyleOptionMenuItem()
        opt.initFrom(self)

        a = QtGui.QAction("fake action", self)
        self.initStyleOption(opt, a)
        size = QtCore.QSize()
        fm = self.fontMetrics()
        size.setWidth(
            fm.boundingRect(
                QtCore.QRect(), QtCore.Qt.TextFlag.TextSingleLine, a.text()
            ).width()
        )
        size.setHeight(fm.height())
        self.default_item_height = style.sizeFromContents(
            QtWidgets.QStyle.ContentsType.CT_MenuItem, opt, size, self
        ).height()

        if not count:
            self.setMaximumHeight(self._maximum_height)
        else:
            fw = style.pixelMetric(style.PixelMetric.PM_MenuHMargin, None, self)
            vmargin = style.pixelMetric(style.PixelMetric.PM_MenuHMargin, opt, self)
            scroll_height = self.scroll_height(style)
            self.setMaximumHeight(
                self.default_item_height * count + (fw + vmargin + scroll_height) * 2
            )
        self.dirty = True

    def scroll_height(self, style: QtWidgets.QStyle) -> int:
        return (
            style.pixelMetric(style.PixelMetric.PM_MenuScrollerHeight, None, self) * 2
        )

    def is_scrollable(self) -> bool:
        return (
            self.property("scrollable") and self.height() < super().sizeHint().height()
        )

    def check_scroll(self):
        pos = self.mapFromGlobal(QtGui.QCursor.pos())
        delta = max(2, int(self.default_item_height * 0.25))
        if self.scroll_up_rect.contains(pos):
            delta *= -1
        elif not self.scroll_down_rect.contains(pos):
            return
        if self.scroll_by(delta):
            self.scroll_timer.start(self.scroll_timer.property("defaultInterval"))

    def offset(self) -> int:
        if self.is_scrollable():
            return self.delta_y - self.scroll_height(self.style())
        return 0

    def translated_action_geometry(self, action: QtGui.QAction) -> QtCore.QRect:
        return self.action_rects[self.actions().index(action)]

    def ensure_visible(self, action: QtGui.QAction):
        style = self.style()
        fw = style.pixelMetric(style.PixelMetric.PM_MenuPanelWidth, None, self)
        hmargin = style.pixelMetric(style.PixelMetric.PM_MenuHMargin, None, self)
        vmargin = style.pixelMetric(style.PixelMetric.PM_MenuVMargin, None, self)
        scroll_height = self.scroll_height(style)
        extent = fw + hmargin + vmargin + scroll_height
        r = self.rect().adjusted(0, extent, 0, -extent)
        geo = self.translated_action_geometry(action)
        if geo.top() < r.top():
            self.scroll_by(-(r.top() - geo.top()))
        elif geo.bottom() > r.bottom():
            self.scroll_by(geo.bottom() - r.bottom())

    def scroll_by(self, step: int) -> bool:
        if step < 0:
            new_delta = max(0, self.delta_y + step)
            if new_delta == self.delta_y:
                return False
        elif step > 0:
            new_delta = self.delta_y + step
            style = self.style()
            scroll_height = self.scroll_height(style)
            bottom = self.height() - scroll_height

            for last_action in reversed(self.actions()):
                if last_action.isVisible():
                    last_bottom = (
                        self.actionGeometry(last_action).bottom()
                        - new_delta
                        + scroll_height
                    )
                    if last_bottom < bottom:
                        new_delta -= bottom - last_bottom
                    if new_delta == self.delta_y:
                        return False
                    break
        else:
            return False

        self.delta_y = new_delta
        self.dirty = True
        self.update()
        return True

    # class methods reimplementation

    def actionAt(self, pos: QtCore.QPoint) -> QtGui.QAction | None:  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        for action, rect in self.iter_action_rects():
            if rect.contains(pos):
                return action

    def sizeHint(self) -> QtCore.QSize:  # noqa: N802
        hint = super().sizeHint()
        if hint.height() > self.maximumHeight():
            hint.setHeight(self.maximumHeight())
        return hint

    def eventFilter(self, source: QtWidgets.QObject, event: QtCore.QEvent) -> bool:  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        if event.type() == QtCore.QEvent.Type.Show:
            if self.is_scrollable() and self.delta_y:
                action = source.menuAction()
                self.ensure_visible(action)
                rect = self.translated_action_geometry(action)
                delta = rect.topLeft() - self.actionGeometry(action).topLeft()
                source.move(source.pos() + delta)
            return False
        return super().eventFilter(source, event)

    def event(self, event: QtCore.QEvent) -> bool:
        if not self.is_scrollable():
            return super().event(event)
        if event.type() == QtCore.QEvent.Type.KeyPress:
            event = cast(QtGui.QKeyEvent, event)
            if event.key() in (
                QtCore.Qt.Key.Key_Up,
                QtCore.Qt.Key.Key_Down,
            ):
                res = super().event(event)
                action = self.activeAction()
                if action:
                    self.ensure_visible(action)
                    self.update()
                return res
        elif event.type() in (
            QtCore.QEvent.Type.MouseButtonPress,
            QtCore.QEvent.Type.MouseButtonDblClick,
        ):
            event = cast(QtGui.QMouseEvent, event)
            pos = event.pos()
            if self.scroll_up_rect.contains(pos) or self.scroll_down_rect.contains(pos):
                if event.button() == QtCore.Qt.MouseButton.LeftButton:
                    step = max(2, int(self.default_item_height * 0.25))
                    if self.scroll_up_rect.contains(pos):
                        step *= -1
                    self.scroll_by(step)
                    self.scroll_timer.start(200)
                    self.ignore_auto_scroll = True
                return True
        elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
            event = cast(QtGui.QMouseEvent, event)
            pos = event.pos()
            self.scroll_timer.stop()
            if not (
                self.scroll_up_rect.contains(pos) or self.scroll_down_rect.contains(pos)
            ):
                action = self.actionAt(pos)
                if action:
                    action.trigger()
                    self.close()
            return True
        return super().event(event)

    def timerEvent(self, event: QtCore.QTimerEvent):  # noqa: N802
        if not self.is_scrollable():
            # ignore internal timer event for reopening popups
            super().timerEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):  # noqa: N802
        if not self.is_scrollable():
            super().mouseMoveEvent(event)
            return

        pos = event.pos()
        if (
            pos.y() < self.scroll_up_rect.bottom()
            or pos.y() > self.scroll_down_rect.top()
        ):
            if not self.ignore_auto_scroll and not self.scroll_timer.isActive():
                self.scroll_timer.start(200)
            return
        self.ignore_auto_scroll = False

        old_action = self.activeAction()
        if not self.rect().contains(pos):
            action = None
        else:
            y = event.y()
            for action, rect in self.iter_action_rects():
                if rect.y() <= y <= rect.y() + rect.height():
                    action = action
                    break
            else:
                action = None

        self.setActiveAction(action) if action else None
        if action and not action.isSeparator():

            def ensureVisible():  # noqa: N802
                self.delay_timer.timeout.disconnect()
                self.ensure_visible(action)

            with contextlib.suppress(Exception):
                self.delay_timer.disconnect()  # pyright: ignore[reportCallIssue]
            self.delay_timer.timeout.connect(ensureVisible)
            self.delay_timer.start(150)
        elif old_action and old_action.menu() and old_action.menu().isVisible():  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

            def closeMenu():  # noqa: N802
                self.delay_timer.timeout.disconnect()
                old_action.menu().hide()  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

            self.delay_timer.timeout.connect(closeMenu)
            self.delay_timer.start(50)
        self.update()

    def wheelEvent(self, event: QtGui.QWheelEvent):  # noqa: N802
        if not self.is_scrollable():
            return
        self.delay_timer.stop()
        if event.angleDelta().y() < 0:
            self.scroll_by(self.default_item_height)
        else:
            self.scroll_by(-self.default_item_height)

    def showEvent(self, event: QtGui.QShowEvent):  # noqa: N802
        if self.is_scrollable():
            self.delta_y = 0
            self.dirty = True
            for action in self.actions():
                if action.menu():
                    action.menu().installEventFilter(self)
            self.ignore_auto_scroll = False
        super().showEvent(event)

    def hideEvent(self, event: QtGui.QHideEvent):  # noqa: N802
        for action in self.actions():
            if action.menu():
                action.menu().removeEventFilter(self)
        super().hideEvent(event)

    def resizeEvent(self, event: QtGui.QResizeEvent):  # noqa: N802
        super().resizeEvent(event)

        style = self.style()
        margins = self.contentsMargins()
        l, t, r, b = margins.left(), margins.top(), margins.right(), margins.bottom()  # noqa: E741
        fw = style.pixelMetric(style.PixelMetric.PM_MenuPanelWidth, None, self)
        hmargin = style.pixelMetric(style.PixelMetric.PM_MenuHMargin, None, self)
        vmargin = style.pixelMetric(style.PixelMetric.PM_MenuVMargin, None, self)
        left_margin = fw + hmargin + l
        top_margin = fw + vmargin + t
        bottom_margin = fw + vmargin + b
        content_width = self.width() - (fw + hmargin) * 2 - l - r

        scroll_height = self.scroll_height(style)
        self.scroll_up_rect = QtCore.QRect(
            left_margin, top_margin, content_width, scroll_height
        )
        self.scroll_down_rect = QtCore.QRect(
            left_margin,
            self.height() - scroll_height - bottom_margin,
            content_width,
            scroll_height,
        )

    def paintEvent(self, event: QtGui.QPaintEvent):  # noqa: N802
        if not self.is_scrollable():
            super().paintEvent(event)
            return

        style = self.style()
        qp = QtGui.QPainter(self)
        rect = self.rect()
        empty_area = QtGui.QRegion(rect)

        menu_opt = QtWidgets.QStyleOptionMenuItem()
        menu_opt.initFrom(self)
        menu_opt.state = style.StateFlag.State_None  # pyright: ignore[reportAttributeAccessIssue]
        menu_opt.maxIconWidth = 0  # pyright: ignore[reportAttributeAccessIssue]
        menu_opt.tabWidth = 0  # pyright: ignore[reportAttributeAccessIssue]
        style.drawPrimitive(style.PrimitiveElement.PE_PanelMenu, menu_opt, qp, self)

        fw = style.pixelMetric(style.PixelMetric.PM_MenuPanelWidth, None, self)
        top_edge = self.scroll_up_rect.bottom()
        bottom_edge = self.scroll_down_rect.top()
        offset = self.offset()
        qp.save()
        qp.translate(0, -offset)
        # offset translation is required in order to allow correct fade animations
        action_rect = next(self.iter_action_rects())[1]
        for action, action_rect in self.iter_action_rects():
            action_rect = self.translated_action_geometry(action)
            if action_rect.bottom() < top_edge:
                continue
            if action_rect.top() > bottom_edge:
                continue

            visible = QtCore.QRect(action_rect)
            if action_rect.bottom() > bottom_edge:
                visible.setBottom(bottom_edge)
            elif action_rect.top() < top_edge:
                visible.setTop(top_edge)
            visible = QtGui.QRegion(visible.translated(0, offset))
            qp.setClipRegion(visible)
            empty_area -= visible.translated(0, -offset)

            opt = QtWidgets.QStyleOptionMenuItem()
            self.initStyleOption(opt, action)
            opt.rect = action_rect.translated(0, offset)  # pyright: ignore[reportAttributeAccessIssue]
            style.drawControl(style.ControlElement.CE_MenuItem, opt, qp, self)
        qp.restore()

        cursor = self.mapFromGlobal(QtGui.QCursor.pos())
        up_data = (False, self.delta_y > 0, self.scroll_up_rect)
        down_data = (
            True,
            action_rect.bottom() - 2 > bottom_edge,
            self.scroll_down_rect,
        )

        for is_down, enabled, scroll_rect in up_data, down_data:
            qp.setClipRect(scroll_rect)

            scroll_opt = QtWidgets.QStyleOptionMenuItem()
            scroll_opt.initFrom(self)
            scroll_opt.state = style.StateFlag.State_None  # pyright: ignore[reportAttributeAccessIssue]
            scroll_opt.state |= (  # pyright: ignore[reportAttributeAccessIssue]
                style.StateFlag.State_DownArrow
                if is_down
                else style.StateFlag.State_UpArrow
            )
            scroll_opt.checkType = scroll_opt.CheckType.NotCheckable  # pyright: ignore[reportAttributeAccessIssue]
            scroll_opt.maxIconWidth = scroll_opt.tabWidth = 0  # pyright: ignore[reportAttributeAccessIssue]
            scroll_opt.rect = scroll_rect  # pyright: ignore[reportAttributeAccessIssue]
            if enabled:
                if scroll_rect.contains(cursor):
                    frame = QtWidgets.QStyleOptionMenuItem()
                    frame.initFrom(self)
                    frame.rect = scroll_rect  # pyright: ignore[reportAttributeAccessIssue]
                    frame.state |= (  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                        style.StateFlag.State_Selected | style.StateFlag.State_Enabled
                    )
                    style.drawControl(style.ControlElement.CE_MenuItem, frame, qp, self)

                scroll_opt.state |= style.StateFlag.State_Enabled  # pyright: ignore[reportAttributeAccessIssue]
                scroll_opt.palette.setCurrentColorGroup(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                    QtGui.QPalette.ColorGroup.Active
                )
            else:
                scroll_opt.palette.setCurrentColorGroup(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                    QtGui.QPalette.ColorGroup.Disabled
                )
            style.drawControl(
                style.ControlElement.CE_MenuScroller, scroll_opt, qp, self
            )

        if fw:
            border_reg = QtGui.QRegion()
            border_reg |= QtGui.QRegion(QtCore.QRect(0, 0, fw, self.height()))
            border_reg |= QtGui.QRegion(
                QtCore.QRect(self.width() - fw, 0, fw, self.height())
            )
            border_reg |= QtGui.QRegion(QtCore.QRect(0, 0, self.width(), fw))
            border_reg |= QtGui.QRegion(
                QtCore.QRect(0, self.height() - fw, self.width(), fw)
            )
            qp.setClipRegion(border_reg)
            empty_area -= border_reg
            frame = QtWidgets.QStyleOptionFrame()
            frame.rect = rect  # pyright: ignore[reportAttributeAccessIssue]
            frame.palette = self.palette()  # pyright: ignore[reportAttributeAccessIssue]
            frame.state = style.StateFlag.State_None  # pyright: ignore[reportAttributeAccessIssue]
            frame.lineWidth = style.pixelMetric(style.PixelMetric.PM_MenuPanelWidth)  # pyright: ignore[reportAttributeAccessIssue]
            frame.midLineWidth = 0  # pyright: ignore[reportAttributeAccessIssue]
            style.drawPrimitive(style.PrimitiveElement.PE_FrameMenu, frame, qp, self)

        qp.setClipRegion(empty_area)
        menu_opt.state = style.StateFlag.State_None  # pyright: ignore[reportAttributeAccessIssue]
        menu_opt.rect = menu_opt.menuRect = rect  # pyright: ignore[reportAttributeAccessIssue]
        style.drawControl(style.ControlElement.CE_MenuEmptyArea, menu_opt, qp, self)


@property_mixin
class SearchableMenuBase(ScrollableMenuBase):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.search_popup = MPopup(self)
        self.search_popup.setVisible(False)
        self.search_bar = MLineEdit(parent=self)
        self.search_label = QtWidgets.QLabel()

        self.search_bar.textChanged.connect(self.slot_search_change)
        self.search_bar.keyPressEvent = partial(
            self.search_key_event, self.search_bar.keyPressEvent
        )
        self.aboutToHide.connect(lambda: self.search_bar.setText(""))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_bar)
        self.search_popup.setLayout(layout)

        self.setProperty("search_placeholder", self.tr("Search Action..."))
        self.setProperty("search_label", self.tr("Search Action..."))

        self.setProperty("searchable", True)
        self.setProperty("search_re", "I")

    def search_key_event(
        self, call: Callable[[QtGui.QKeyEvent], Any], event: QtGui.QKeyEvent
    ):
        key = event.key()
        # NOTES: support menu original key event on search bar
        if key in (
            QtCore.Qt.Key.Key_Up,
            QtCore.Qt.Key.Key_Down,
            QtCore.Qt.Key.Key_Return,
            QtCore.Qt.Key.Key_Enter,
        ):
            super().keyPressEvent(event)
        elif key == QtCore.Qt.Key.Key_Tab:
            self.search_bar.setFocus()
        return call(event)

    def _set_search_label(self, value: str):
        self.search_label.setText(value)

    def _set_search_placeholder(self, value: str):
        self.search_bar.setPlaceholderText(value)

    def _set_search_re(self, value: str): ...

    def slot_search_change(self, text: str):
        flags = 0
        for m in self.property("search_re") or "":
            flags |= getattr(re, m.upper(), 0)
        search_reg = re.compile(rf".*{text}.*", flags)
        self._update_search(search_reg)

    def _update_search(
        self, search_reg: str | re.Pattern[str], parent_menu: MMenu | None = None
    ):
        actions = parent_menu.actions() if parent_menu else self.actions()
        vis_list: list[QtGui.QAction] = []
        for action in actions:
            menu = cast(MMenu, action.menu())
            if not menu:
                is_match = bool(re.match(search_reg, action.text()))
                action.setVisible(is_match)
                if is_match:
                    vis_list.append(action)
            else:
                is_match = bool(re.match(search_reg, menu.title()))
                self._update_search("" if is_match else search_reg, menu)

        if parent_menu:
            parent_menu.menuAction().setVisible(bool(vis_list) or not search_reg)

    def keyPressEvent(self, event: QtGui.QKeyEvent):  # noqa: N802
        key = event.key()
        if self.property("searchable"):
            # NOTES(timmyliang): 26 character trigger search bar
            if 65 <= key <= 90:
                char = chr(key)
                self.search_bar.setText(char)
                self.search_bar.setFocus()
                self.search_bar.selectAll()
                width = self.sizeHint().width()
                width = width if width >= 50 else 50
                offset = QtCore.QPoint(width, 0)
                self.search_popup.move(self.pos() + offset)
                self.search_popup.show()
            elif key == QtCore.Qt.Key.Key_Escape:
                self.search_bar.setText("")
                self.search_popup.hide()
        return super().keyPressEvent(event)


@property_mixin
class MMenu(ScrollableMenuBase):
    value_changed = QtCore.Signal(object)

    def __init__(
        self,
        exclusive: bool = True,
        cascader: bool = False,
        title: str = "",
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(title=title, parent=parent)
        self.setProperty("cascader", cascader)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self._action_group = QtGui.QActionGroup(self)
        self._action_group.setExclusive(exclusive)
        self._action_group.triggered.connect(self.on_action_triggered)
        self._load_data_func: (
            Callable[[], Sequence[str | int | float | MenuItemData]] | None
        ) = None
        self.set_value("")
        self.set_data([])
        self.set_separator("/")

    def set_separator(self, chr: str):
        self.setProperty("separator", chr)

    def set_load_callback(
        self, func: Callable[[], Sequence[str | int | float | MenuItemData]]
    ):
        """Set the load data callback function"""
        self._load_data_func = func
        self.aboutToShow.connect(self.on_fetch_data)

    def on_fetch_data(self):
        if self._load_data_func:
            data_list = self._load_data_func()
            self.set_data(data_list)

    def set_value(self, data: list[Any] | str | int | float):
        assert isinstance(data, list | str | int | float)
        if self.property("cascader") and isinstance(data, str):
            data = data.split(self.property("separator"))
        self.setProperty("value", data)

    def _set_value(self, value: Any):
        data_list: list[Any] = value if isinstance(value, list) else [value]  # pyright: ignore[reportUnknownVariableType]
        flag = False
        for act in self._action_group.actions():
            checked = act.property("value") in data_list
            if act.isChecked() != checked:
                act.setChecked(checked)
                flag = True
        if flag:
            self.value_changed.emit(value)

    def _add_menu(self, parent_menu: MMenu, data_dict: utils.MenuItemData):
        if "children" in data_dict:
            menu = MMenu(title=data_dict.get("label", ""), parent=self)
            menu.setProperty("value", data_dict.get("value"))
            parent_menu.addMenu(menu)
            if parent_menu is not self:
                menu.setProperty("parent_menu", parent_menu)
            for i in data_dict.get("children", []):
                self._add_menu(menu, i)
        else:
            action = self._action_group.addAction(
                utils.display_formatter(data_dict.get("label"))
            )
            action.setProperty("value", data_dict.get("value"))
            action.setCheckable(True)
            action.setProperty("parent_menu", parent_menu)
            parent_menu.addAction(action)

    def set_data(self, option_list: Sequence[str | int | float | utils.MenuItemData]):
        assert isinstance(option_list, list)
        if option_list:
            if all(isinstance(i, str) for i in option_list):
                option_list = cast(list[str], option_list)
                option_list = utils.from_list_to_nested_dict(
                    option_list,
                    sep=self.property("separator"),
                )
            if all(isinstance(i, int | float) for i in option_list):
                option_list = [
                    utils.MenuItemData(value=i, label=str(i)) for i in option_list
                ]
        self.setProperty("data", option_list)

    def _set_data(self, option_list: list[utils.MenuItemData]):
        self.clear()
        for act in self._action_group.actions():
            self._action_group.removeAction(act)

        for data_dict in option_list:
            self._add_menu(self, data_dict)

    def _get_parent(self, result: list[Any], obj: QtGui.QAction):
        if obj.property("parent_menu"):
            parent_menu = obj.property("parent_menu")
            result.insert(0, parent_menu.property("value"))
            self._get_parent(result, parent_menu)

    def on_action_triggered(self, action: QtGui.QAction):
        current_data = action.property("value")
        if self.property("cascader"):
            selected_data = [current_data]
            self._get_parent(selected_data, action)
        else:
            if self._action_group.isExclusive():
                selected_data = current_data
            else:
                selected_data = [
                    act.property("value")
                    for act in self._action_group.actions()
                    if act.isChecked()
                ]
        self.set_value(selected_data)
        self.value_changed.emit(selected_data)

    def set_loader(self, func: Callable[..., Any]):
        self._load_data_func = func
