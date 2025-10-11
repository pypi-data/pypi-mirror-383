from typing import TYPE_CHECKING, Any, cast

from qtpy import QtCore, QtGui, QtWidgets

from . import utils
from .header_view import MHeaderView
from .item_model import MTableModel
from .menu import MMenu
from .qt import MPixmap, get_scale_factor
from .theme import MTheme
from .types import HeaderData, ItemViewMenuEvent

HEADER_SORT_MAP = {
    "asc": QtCore.Qt.SortOrder.AscendingOrder,
    "desc": QtCore.Qt.SortOrder.DescendingOrder,
}


class MAbstractView(QtWidgets.QAbstractItemView if TYPE_CHECKING else object):
    sig_context_menu = QtCore.Signal(object)

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__()
        self.header_list: list[HeaderData] = []
        self.header_view: MHeaderView | None = None
        self._no_data_text = self.tr("No Data")
        self._no_data_image: QtGui.QPixmap | None = None

    def set_header_list(self, header_list: list[HeaderData]):
        scale_x, _ = get_scale_factor()
        self.header_list = header_list
        if self.header_view:
            for index, i in enumerate(header_list):
                self.header_view.setSectionHidden(index, i.get("hide", False))
                self.header_view.resizeSection(
                    index, int(i.get("width", 100) * scale_x)
                )
                if "order" in i:
                    order = i.get("order")
                    if order in HEADER_SORT_MAP.values():
                        self.header_view.setSortIndicator(
                            index, cast(QtCore.Qt.SortOrder, order)
                        )
                    elif order in HEADER_SORT_MAP:
                        self.header_view.setSortIndicator(index, HEADER_SORT_MAP[order])
                if i.get("selectable", False):
                    delegate = MOptionDelegate(parent=self)
                    delegate.set_exclusive(i.get("exclusive", True))
                    self.setItemDelegateForColumn(index, delegate)
                elif self.itemDelegateForColumn(index):
                    self.setItemDelegateForColumn(index, None)  # pyright: ignore[reportArgumentType]

    @QtCore.Slot(QtCore.QPoint)
    def slot_context_menu(self, point: QtCore.QPoint):
        proxy_index = self.indexAt(point)
        if proxy_index.isValid():
            selection: list[QtCore.QItemSelection] = []
            for index in (
                self.selectionModel().selectedRows()
                or self.selectionModel().selectedIndexes()
            ):
                data_obj = utils.real_index(index).internalPointer()
                selection.append(data_obj)
            event = ItemViewMenuEvent(view=self, selection=selection, extra={})
            self.sig_context_menu.emit(event)
        else:
            event = ItemViewMenuEvent(view=self, selection=[], extra={})
            self.sig_context_menu.emit(event)

    def enable_context_menu(self, enable: bool):
        if enable:
            self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self.slot_context_menu)
        else:
            self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)

    def set_no_data_text(self, text: str):
        self._no_data_text = text

    def set_no_data_image(self, image: QtGui.QPixmap):
        self._no_data_image = image

    def paintEvent(self, event: QtGui.QPaintEvent, /):  # noqa: N802
        """
        Override paintEvent when there is no data to show,
        draw the preset picture and text.
        """
        model = utils.real_model(self.model())
        if model is None or (
            isinstance(model, MTableModel) and not model.get_data_list()
        ):
            draw_empty_content(self.viewport(), self._no_data_text, self._no_data_image)
        return super().paintEvent(event)


def draw_empty_content(
    view: QtWidgets.QWidget,
    text: str | None = None,
    pix_map: QtGui.QPixmap | None = None,
):
    pix_map = pix_map or MPixmap("empty.svg")
    text = text or view.tr("No Data")
    painter = QtGui.QPainter(view)
    font_metrics = painter.fontMetrics()
    painter.setPen(QtGui.QPen(QtGui.QColor(MTheme().secondary_text_color)))
    content_height = pix_map.height() + font_metrics.height()
    padding = 10
    proper_min_size = min(
        view.height() - padding * 2, view.width() - padding * 2, content_height
    )
    if proper_min_size < content_height:
        pix_map = pix_map.scaledToHeight(
            proper_min_size - font_metrics.height(),
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        content_height = proper_min_size
    painter.drawText(
        int(view.width() / 2 - font_metrics.boundingRect(text).width() / 2),
        int(view.height() / 2 + content_height / 2 - font_metrics.height() / 2),
        text,
    )
    painter.drawPixmap(
        int(view.width() / 2 - pix_map.width() / 2),
        int(view.height() / 2 - content_height / 2),
        pix_map,
    )
    painter.end()


class MOptionDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.showed = False
        self.exclusive = True
        self.parent_widget: QtWidgets.QWidget | None = None
        self.arrow_space = 20
        self.arrow_height = 6

    def set_exclusive(self, flag: bool):
        self.exclusive = flag

    def createEditor(  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        self.parent_widget = parent
        editor = MMenu(exclusive=self.exclusive, parent=parent)
        editor.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Window
        )
        model = cast(MAbstractView, utils.real_model(index))
        real_index = utils.real_index(index)
        data_obj = real_index.internalPointer()
        attr = f"{model.header_list[real_index.column()].get('key')}_list"

        editor.set_data(utils.get_obj_value(data_obj, attr, []))
        editor.value_changed.connect(
            self._slot_finish_edit,
        )
        return editor

    def setEditorData(  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self, editor: MMenu, index: QtCore.QModelIndex
    ):
        editor.set_value(index.data(QtCore.Qt.ItemDataRole.EditRole))

    def setModelData(  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self, editor: MMenu, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex
    ):
        model.setData(index, editor.property("value"))

    def updateEditorGeometry(  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        editor: MMenu,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        if self.parent_widget is None:
            return
        editor.move(
            self.parent_widget.mapToGlobal(
                QtCore.QPoint(option.rect.x(), option.rect.y() + option.rect.height())  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
            )
        )

    def paint(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        painter.save()
        icon_color = MTheme().icon_color
        if option.state & QtWidgets.QStyle.StateFlag.State_MouseOver:  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            painter.fillRect(option.rect, QtGui.QColor(MTheme().primary_5))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
            icon_color = "#fff"
        if option.state & QtWidgets.QStyle.StateFlag.State_Selected:  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            painter.fillRect(option.rect, QtGui.QColor(MTheme().primary_6))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
            icon_color = "#fff"
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.white))
        pix = MPixmap("down_fill.svg", icon_color)
        h = cast(int, option.rect.height())  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        pix = pix.scaledToWidth(
            int(h * 0.5), QtCore.Qt.TransformationMode.SmoothTransformation
        )
        painter.drawPixmap(
            int(option.rect.x() + option.rect.width() - h),  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportAttributeAccessIssue]
            int(option.rect.y() + h / 4),  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportAttributeAccessIssue]
            pix,
        )
        painter.restore()
        super().paint(painter, option, index)

    @QtCore.Slot(object)
    def _slot_finish_edit(self, obj: Any):
        self.commitData.emit(self.sender())

    def sizeHint(  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
    ):
        orig = super().sizeHint(option, index)
        return QtCore.QSize(orig.width() + self.arrow_space, orig.height())


class MTableView(QtWidgets.QTableView, MAbstractView):
    def __init__(
        self,
        size: int | None = None,
        show_row_count: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        size = size or MTheme().default_size
        ver_header_view = MHeaderView(QtCore.Qt.Orientation.Vertical, parent=self)
        ver_header_view.setDefaultSectionSize(size)
        ver_header_view.setSortIndicatorShown(False)
        self.setVerticalHeader(ver_header_view)
        self.header_view = MHeaderView(QtCore.Qt.Orientation.Horizontal, parent=self)
        self.header_view.setFixedHeight(size)
        if not show_row_count:
            ver_header_view.hide()
        self.setHorizontalHeader(self.header_view)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)

    def setShowGrid(self, flag: bool):  # noqa: N802
        if self.header_view is None:
            return
        self.header_view.setProperty("grid", flag)
        self.verticalHeader().setProperty("grid", flag)
        self.header_view.style().polish(self.header_view)

        return super().setShowGrid(flag)


class MTreeView(QtWidgets.QTreeView, MAbstractView):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._no_data_image: QtGui.QPixmap | None = None
        self._no_data_text = self.tr("No Data")
        self.header_view = MHeaderView(QtCore.Qt.Orientation.Horizontal)
        self.setHeader(self.header_view)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)

    def set_no_data_text(self, text: str):
        self._no_data_text = text


class MBigView(QtWidgets.QListView, MAbstractView):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.setMovement(QtWidgets.QListView.Movement.Static)
        self.setSpacing(10)
        default_size = MTheme().big_view_default_size
        self.setIconSize(QtCore.QSize(default_size, default_size))

    def scale_size(self, factor: float):
        """Scale the icon size."""
        new_size = self.iconSize() * factor
        max_size = MTheme().big_view_max_size
        min_size = MTheme().big_view_min_size
        if new_size.width() > max_size:
            new_size = QtCore.QSize(max_size, max_size)
        elif new_size.width() < min_size:
            new_size = QtCore.QSize(min_size, min_size)
        self.setIconSize(new_size)

    def wheelEvent(self, event: QtGui.QWheelEvent):  # noqa: N802
        """Override wheelEvent while user press ctrl, zoom the list view icon size."""
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            num_degrees = event.angleDelta().y() / 8.0
            num_steps = num_degrees / 15.0
            factor = pow(1.125, num_steps)
            self.scale_size(factor)
        else:
            super().wheelEvent(event)


class MListView(QtWidgets.QListView, MAbstractView):
    def __init__(
        self, size: int | None = None, parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        self.setProperty("dayu_size", size or MTheme().default_size)
        self.setModelColumn(0)
        self.setAlternatingRowColors(True)

    def set_show_column(self, attr: str):
        for index, attr_dict in enumerate(self.header_list):
            if attr_dict.get("key") == attr:
                self.setModelColumn(index)
                break
        else:
            self.setModelColumn(0)
