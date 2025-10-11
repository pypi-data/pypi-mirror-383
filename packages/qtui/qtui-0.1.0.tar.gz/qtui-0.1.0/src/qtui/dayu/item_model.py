import re
from collections.abc import Iterator
from typing import Any

from qtpy import QtCore, QtGui

from .types import HeaderData, ModelData
from .utils import (
    apply_formatter,
    display_formatter,
    font_formatter,
    get_obj_value,
    icon_formatter,
    set_obj_value,
)

SETTING_MAP: dict[QtCore.Qt.ItemDataRole, dict[str, Any]] = {
    QtCore.Qt.ItemDataRole.BackgroundRole: {
        "config": "bg_color",
        "formatter": QtGui.QColor,
    },
    QtCore.Qt.ItemDataRole.DisplayRole: {
        "config": "display",
        "formatter": display_formatter,
    },
    QtCore.Qt.ItemDataRole.EditRole: {"config": "edit", "formatter": None},
    QtCore.Qt.ItemDataRole.TextAlignmentRole: {
        "config": "alignment",
        "formatter": {
            "right": QtCore.Qt.AlignmentFlag.AlignRight,
            "left": QtCore.Qt.AlignmentFlag.AlignLeft,
            "center": QtCore.Qt.AlignmentFlag.AlignCenter,
        },
    },
    QtCore.Qt.ItemDataRole.ForegroundRole: {
        "config": "color",
        "formatter": QtGui.QColor,
    },
    QtCore.Qt.ItemDataRole.FontRole: {"config": "font", "formatter": font_formatter},
    QtCore.Qt.ItemDataRole.DecorationRole: {
        "config": "icon",
        "formatter": icon_formatter,
    },
    QtCore.Qt.ItemDataRole.ToolTipRole: {
        "config": "tooltip",
        "formatter": display_formatter,
    },
    QtCore.Qt.ItemDataRole.InitialSortOrderRole: {
        "config": "order",
        "formatter": {
            "asc": QtCore.Qt.SortOrder.AscendingOrder,
            "des": QtCore.Qt.SortOrder.DescendingOrder,
        },
    },
    QtCore.Qt.ItemDataRole.SizeHintRole: {
        "config": "size",
        "formatter": lambda args: QtCore.QSize(*args),  # pyright: ignore[reportUnknownLambdaType]
    },
    QtCore.Qt.ItemDataRole.UserRole: {"config": "data"},  # anything
}


class MTableModel(QtCore.QAbstractItemModel):
    def __init__(self, parent: QtCore.QObject | None = None):
        super().__init__(parent)
        self.origin_count = 0
        self.root_item: ModelData = {"name": "root", "children": []}
        self.data_generator: Iterator[ModelData] | None = None
        self.header_list: list[HeaderData] = []
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.fetchMore)

    def set_header_list(self, header_list: list[HeaderData]):
        self.header_list = header_list

    def set_data_list(self, data_list: list[ModelData] | Iterator[ModelData] | None):
        if isinstance(data_list, Iterator):
            self.beginResetModel()
            self.root_item["children"] = []
            self.endResetModel()
            self.data_generator = data_list
            self.origin_count = 0
            self.timer.start()
        else:
            self.beginResetModel()
            self.root_item["children"] = data_list if data_list is not None else []
            self.endResetModel()
            self.data_generator = None

    def clear(self):
        self.beginResetModel()
        self.root_item["children"] = []
        self.endResetModel()

    def get_data_list(self):
        return self.root_item["children"]

    def append(self, data_dict: ModelData):
        self.root_item["children"].append(data_dict)
        self.fetchMore()

    def remove(self, data_dict: ModelData):
        row = self.root_item["children"].index(data_dict)
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self.root_item["children"].remove(data_dict)
        self.endRemoveRows()

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:  # pyright: ignore[reportIncompatibleMethodOverride]
        result = QtCore.QAbstractItemModel.flags(self, index)
        if not index.isValid():
            return QtCore.Qt.ItemFlag.ItemIsEnabled
        if self.header_list[index.column()].get("checkable", False):
            result |= QtCore.Qt.ItemFlag.ItemIsUserCheckable
        if self.header_list[index.column()].get("selectable", False):
            result |= QtCore.Qt.ItemFlag.ItemIsEditable
        if self.header_list[index.column()].get("editable", False):
            result |= QtCore.Qt.ItemFlag.ItemIsEditable
        if self.header_list[index.column()].get("draggable", False):
            result |= QtCore.Qt.ItemFlag.ItemIsDragEnabled
        if self.header_list[index.column()].get("droppable", False):
            result |= QtCore.Qt.ItemFlag.ItemIsDropEnabled
        return QtCore.Qt.ItemFlag(result)

    def headerData(  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if orientation == QtCore.Qt.Orientation.Vertical:
            return super().headerData(section, orientation, role)
        if not self.header_list or section >= len(self.header_list):
            return None
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.header_list[section]["label"]
        return None

    def index(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, row: int, column: int, parent_index: QtCore.QModelIndex | None = None
    ) -> QtCore.QModelIndex:
        if parent_index and parent_index.isValid():
            parent_item = parent_index.internalPointer()
        else:
            parent_item = self.root_item

        children_list = get_obj_value(parent_item, "children")
        if children_list and len(children_list) > row:
            child_item = children_list[row]
            if child_item:
                set_obj_value(child_item, "_parent", parent_item)
                return self.createIndex(row, column, child_item)
        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = index.internalPointer()
        parent_item = get_obj_value(child_item, "_parent")

        if parent_item is None:
            return QtCore.QModelIndex()

        grand_item = get_obj_value(parent_item, "_parent")
        if grand_item is None:
            return QtCore.QModelIndex()
        parent_list = get_obj_value(grand_item, "children")
        return self.createIndex(parent_list.index(parent_item), 0, parent_item)

    def rowCount(self, parent_index: QtCore.QModelIndex | None = None) -> int:  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        if parent_index and parent_index.isValid():
            parent_item = parent_index.internalPointer()
        else:
            parent_item = self.root_item
        children_obj = get_obj_value(parent_item, "children")
        if hasattr(children_obj, "next") or (children_obj is None):
            return 0
        else:
            return len(children_obj)

    def hasChildren(self, parent_index: QtCore.QModelIndex | None = None) -> bool | int:  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        if parent_index and parent_index.isValid():
            parent_data = parent_index.internalPointer()
        else:
            parent_data = self.root_item
        children_obj = get_obj_value(parent_data, "children")
        if children_obj is None:
            return False
        if hasattr(children_obj, "__next__"):
            return True
        else:
            return len(children_obj)

    def columnCount(self, parent_index: QtCore.QModelIndex | None = None) -> int:  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        return len(self.header_list)

    def canFetchMore(self, index: QtCore.QModelIndex | None = None) -> bool:  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        try:
            if self.data_generator:
                data = next(self.data_generator)
                self.root_item["children"].append(data)
                return True
            return False
        except StopIteration:
            if self.timer.isActive():
                self.timer.stop()
            return False

    def fetchMore(self, index: QtCore.QModelIndex | None = None) -> None:  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self.beginResetModel()
        self.endResetModel()

    def data(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        index: QtCore.QModelIndex,
        role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid():
            return None

        attr_dict = self.header_list[index.column()]
        data_obj = index.internalPointer()
        attr = attr_dict.get("key")
        if role in SETTING_MAP:
            role_key = SETTING_MAP[role].get("config")
            formatter_from_config = attr_dict.get(role_key)  # pyright: ignore[reportCallIssue, reportArgumentType, reportUnknownVariableType]
            if not formatter_from_config and role not in [
                QtCore.Qt.ItemDataRole.DisplayRole,
                QtCore.Qt.ItemDataRole.EditRole,
                QtCore.Qt.ItemDataRole.ToolTipRole,
            ]:
                return None
            else:
                value = apply_formatter(
                    formatter_from_config, get_obj_value(data_obj, attr), data_obj
                )
            formatter_from_model = SETTING_MAP[role].get("formatter", None)
            result = apply_formatter(formatter_from_model, value)
            return result

        if role == QtCore.Qt.ItemDataRole.CheckStateRole and attr_dict.get(
            "checkable", False
        ):
            state = get_obj_value(data_obj, attr + "_checked")
            return QtCore.Qt.CheckState.Unchecked if state is None else state
        return None

    def setData(  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        index: QtCore.QModelIndex,
        value: Any,
        role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.EditRole,
    ) -> bool:
        if index.isValid() and role in [
            QtCore.Qt.ItemDataRole.CheckStateRole,
            QtCore.Qt.ItemDataRole.EditRole,
        ]:
            attr_dict = self.header_list[index.column()]
            key = attr_dict.get("key")
            data_obj = index.internalPointer()
            if role == QtCore.Qt.ItemDataRole.CheckStateRole and attr_dict.get(
                "checkable", False
            ):
                key += "_checked"
                set_obj_value(data_obj, key, value)
                self.dataChanged.emit(index, index)

                for row, sub_obj in enumerate(get_obj_value(data_obj, "children", [])):
                    set_obj_value(sub_obj, key, value)
                    sub_index = self.index(row, index.column(), index)
                    self.dataChanged.emit(sub_index, sub_index)

                parent_index = index.parent()
                if parent_index.isValid():
                    parent_obj = parent_index.internalPointer()
                    new_parent_value = value
                    old_parent_value = get_obj_value(parent_obj, key)
                    for sibling_obj in get_obj_value(
                        get_obj_value(data_obj, "_parent"), "children", []
                    ):
                        if value != get_obj_value(sibling_obj, key):
                            new_parent_value = 1
                            break
                    if new_parent_value != old_parent_value:
                        set_obj_value(parent_obj, key, new_parent_value)
                        self.dataChanged.emit(parent_index, parent_index)
            else:
                set_obj_value(data_obj, key, value)
                self.dataChanged.emit(index, index)
            return True
        else:
            return False


class MSortFilterModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent: QtCore.QObject | None = None):
        super().__init__(parent)
        if hasattr(self, "setRecursiveFilteringEnabled"):
            self.setRecursiveFilteringEnabled(True)
        self.header_list: list[HeaderData] = []
        self.search_reg: re.Pattern[str] | None = None

    def set_header_list(self, header_list: list[HeaderData]):
        self.header_list = header_list
        for head in self.header_list:
            head.update({"reg": None})

    def filterAcceptsRow(  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self, source_row: int, source_parent: QtCore.QModelIndex
    ) -> bool:
        if self.search_reg:
            for index, data_dict in enumerate(self.header_list):
                if data_dict.get("searchable", False):
                    model_index = self.sourceModel().index(
                        source_row, index, source_parent
                    )
                    value = self.sourceModel().data(model_index)
                    if self.search_reg.match(str(value)) is not None:
                        break
            else:
                return False

        for index, data_dict in enumerate(self.header_list):
            model_index = self.sourceModel().index(source_row, index, source_parent)
            value = self.sourceModel().data(model_index)
            reg_exp = data_dict.get("reg", None)
            if reg_exp and (not reg_exp.match(value)):
                return False

        return True

    def set_search_pattern(self, pattern: str):
        self.search_reg = re.compile(pattern)
        self.invalidateFilter()

    def set_filter_attr_pattern(self, attr: str, pattern: str):
        for data_dict in self.header_list:
            if data_dict.get("key") == attr:
                data_dict["reg"] = re.compile(pattern)
                break
        self.invalidateFilter()
