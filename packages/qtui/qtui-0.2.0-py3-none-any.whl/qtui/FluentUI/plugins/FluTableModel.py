# pyright: basic, reportArgumentType=none, reportRedeclaration=none
# ruff: noqa: N815 N802

from typing import Any

from PySide6.QtCore import (
    Property,
    QAbstractTableModel,
    QModelIndex,
    Signal,
    Slot,
)


# noinspection PyPep8Naming,PyTypeChecker
class FluTableModel(QAbstractTableModel):
    columnSourceChanged = Signal()
    rowsChanged = Signal()

    def __init__(self):
        QAbstractTableModel.__init__(self)
        self._columnSource: list[dict[str, Any]] = []
        self._rows: list[dict[str, Any]] = []

    @Slot()
    def clear(self):
        self.beginResetModel()
        self._rows = []
        self.endResetModel()

    @Slot(int, result=dict)
    def getRow(self, row_index: int) -> dict[str, Any]:
        return self._rows[row_index]

    @Slot(int, dict)
    def setRow(self, row_index: int, row: dict[str, Any]):
        self._rows[row_index] = row
        self.dataChanged.emit(
            self.index(row_index, 0), self.index(row_index, self.columnCount() - 1)
        )

    @Slot(int, dict)
    def insertRow(self, row_index: int, row: dict[str, Any]):
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self._rows.insert(row_index, row)
        self.endInsertRows()

    @Slot(int)
    @Slot(int, int)
    def removeRow(self, row_index: int, rows: int | None = None):
        if rows is None:
            rows = 1
        self.beginRemoveRows(QModelIndex(), row_index, row_index + rows - 1)
        self._rows = self._rows[:row_index] + self._rows[row_index + rows :]
        self.endRemoveRows()

    @Slot("QVariant")
    def appendRow(self, row: dict[str, Any]):
        self.insertRow(self.rowCount(), row)

    def rowCount(self, parent=...):
        return len(self._rows)

    def columnCount(self, parent=...):
        return len(self._columnSource)

    def data(self, index: QModelIndex, role: int = ...) -> dict[str, Any] | None:
        if not index.isValid():
            return None
        if role == 0x101:
            return self._rows[index.row()]
        elif role == 0x102:
            return self._columnSource[index.column()]
        return None

    def roleNames(self) -> dict[int, bytes]:
        return {0x101: b"rowModel", 0x102: b"columnModel"}

    @Property(list, notify=rowsChanged)
    def rows(self) -> list[dict[str, Any]]:
        return self._rows

    @rows.setter
    def rows(self, value: list[dict[str, Any]]):
        self._rows = value
        self.rowsChanged.emit()

    @Property(list, notify=columnSourceChanged)
    def columnSource(self) -> list[dict[str, Any]]:
        return self._columnSource

    @columnSource.setter
    def columnSource(self, value: list[dict[str, Any]]):
        self._columnSource = value
        self.columnSourceChanged.emit()
