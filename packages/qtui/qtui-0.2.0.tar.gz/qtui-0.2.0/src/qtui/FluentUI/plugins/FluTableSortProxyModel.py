# pyright: basic, reportRedeclaration=none, reportReturnType=none, reportCallIssue=none, reportArgumentType=none
# ruff: noqa: N815 N802

from typing import Any

from PySide6.QtCore import (
    Q_ARG,
    Q_RETURN_ARG,
    Property,
    QAbstractItemModel,
    QMetaObject,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtQml import QJSValue


# noinspection PyCallingNonCallable,PyPep8Naming,PyShadowingBuiltins
class FluTableSortProxyModel(QSortFilterProxyModel):
    modelChanged = Signal()

    def __init__(self):
        QSortFilterProxyModel.__init__(self)
        self._model = None
        self._filter = None
        self._comparator = None
        self.modelChanged.connect(lambda: self.setSourceModel(self._model))  # pyright: ignore[reportArgumentType]

    # noinspection PyTypeChecker
    @Property(QAbstractItemModel, notify=modelChanged)
    def model(self):
        return self._model

    @model.setter
    def model(self, value: QAbstractItemModel):
        self._model = value
        self.modelChanged.emit()

    # noinspection PyTypeChecker
    @Slot(int, result=dict)
    def getRow(self, row_index: int) -> dict[str, Any]:
        if self._model is None:
            return {}
        return QMetaObject.invokeMethod(
            self._model,
            "getRow",
            Q_RETURN_ARG("QVariantMap"),
            Q_ARG(int, self.mapToSource(self.index(row_index, 0)).row()),
        )

    # noinspection PyTypeChecker
    @Slot(int, dict)
    def setRow(self, row_index: int, val: dict[str, Any]):
        if self._model is None:
            return
        QMetaObject.invokeMethod(
            self._model,
            "setRow",
            Q_ARG(int, self.mapToSource(self.index(row_index, 0)).row()),
            Q_ARG("QVariantMap", val),
        )

    @Slot(int, int)
    def removeRow(self, row_index: int, rows: int):
        if self._model is None:
            return
        QMetaObject.invokeMethod(
            self._model,
            "removeRow",
            Q_ARG(int, self.mapToSource(self.index(row_index, 0)).row()),
            Q_ARG(int, rows),
        )

    @Slot(QJSValue)
    def setComparator(self, comparator: QJSValue):
        if self._model is None:
            return
        column = 0
        if comparator.isUndefined():
            column = -1
        self._comparator = comparator
        if self.sortOrder() == Qt.SortOrder.AscendingOrder:
            self.sort(column, Qt.SortOrder.DescendingOrder)
        else:
            self.sort(column, Qt.SortOrder.AscendingOrder)

    @Slot(QJSValue)
    def setFilter(self, filter: QJSValue):
        self._filter = filter
        self.invalidateFilter()

    def filterAcceptsColumn(self, source_column: ..., source_parent: ...):
        return True

    def filterAcceptsRow(self, source_row: int, source_parent: ...):
        if self._filter is None or self._filter.isUndefined():
            return True
        data: list[int] = [source_row]
        return self._filter.call(data).toBool()  # pyright: ignore[reportArgumentType]

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex) -> bool:
        if self._comparator is None or self._comparator.isUndefined():
            return True
        data: list[int] = [source_left.row(), source_right.row()]
        flag = self._comparator.call(data).toBool()  # pyright: ignore[reportArgumentType]
        if self.sortOrder() == Qt.SortOrder.AscendingOrder:
            return not flag
        else:
            return flag
