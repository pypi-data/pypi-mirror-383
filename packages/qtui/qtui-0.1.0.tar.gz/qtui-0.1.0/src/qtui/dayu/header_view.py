import functools

from qtpy import QtCore, QtGui, QtWidgets

from . import utils
from .menu import MMenu


class MHeaderView(QtWidgets.QHeaderView):
    def __init__(
        self,
        orientation: QtCore.Qt.Orientation,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(orientation, parent)
        self.setMovable(True)
        self.setClickable(True)
        self.setSortIndicatorShown(True)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._slot_context_menu)
        self.setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.setProperty(
            "orientation",
            "horizontal"
            if orientation == QtCore.Qt.Orientation.Horizontal
            else "vertical",
        )

    @QtCore.Slot(QtCore.QPoint)
    def _slot_context_menu(self, point: QtCore.QPoint):
        context_menu = MMenu(parent=self)
        logical_column = self.logicalIndexAt(point)
        model = utils.real_model(self.model())
        if not model:
            return
        if logical_column >= 0 and model.header_list[logical_column].get(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            "checkable", False
        ):
            action_select_all = context_menu.addAction(self.tr("Select All"))
            action_select_none = context_menu.addAction(self.tr("Select None"))
            action_select_invert = context_menu.addAction(self.tr("Select Invert"))
            action_select_all.triggered.connect(
                functools.partial(
                    self._slot_set_select, logical_column, QtCore.Qt.CheckState.Checked
                )
            )
            action_select_none.triggered.connect(
                functools.partial(
                    self._slot_set_select,
                    logical_column,
                    QtCore.Qt.CheckState.Unchecked,
                )
            )
            action_select_invert.triggered.connect(
                functools.partial(self._slot_set_select, logical_column, None)
            )
            context_menu.addSeparator()

        fit_action = context_menu.addAction(self.tr("Fit Size"))
        fit_action.triggered.connect(
            functools.partial(self._slot_set_resize_mode, True)
        )
        context_menu.addSeparator()
        for column in range(self.count()):
            action = context_menu.addAction(
                str(
                    model.headerData(
                        column,
                        QtCore.Qt.Orientation.Horizontal,
                        QtCore.Qt.ItemDataRole.DisplayRole,
                    )
                )
            )
            action.setCheckable(True)
            action.setChecked(not self.isSectionHidden(column))
            action.toggled.connect(
                functools.partial(self._slot_set_section_visible, column)
            )
        context_menu.exec(QtGui.QCursor.pos() + QtCore.QPoint(10, 10))

    @QtCore.Slot(int, int)
    def _slot_set_select(self, column: int, state: QtCore.Qt.CheckState | None):
        current_model = self.model()
        source_model = utils.real_model(current_model)
        if not source_model:
            return
        source_model.beginResetModel()
        attr = f"{source_model.header_list[column].get('key')}_checked"  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        for row in range(current_model.rowCount()):
            real_index = utils.real_index(current_model.index(row, column))
            data_obj = real_index.internalPointer()
            if state is None:
                old_state = utils.get_obj_value(data_obj, attr)
                utils.set_obj_value(
                    data_obj,
                    attr,
                    QtCore.Qt.CheckState.Unchecked
                    if old_state == QtCore.Qt.CheckState.Checked
                    else QtCore.Qt.CheckState.Checked,
                )
            else:
                utils.set_obj_value(data_obj, attr, state)
        source_model.endResetModel()
        source_model.dataChanged.emit(None, None)

    @QtCore.Slot(QtCore.QModelIndex, int)
    def _slot_set_section_visible(self, index: int, flag: bool):
        self.setSectionHidden(index, not flag)

    @QtCore.Slot(bool)
    def _slot_set_resize_mode(self, flag: bool):
        if flag:
            self.resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        else:
            self.resizeSections(QtWidgets.QHeaderView.ResizeMode.Interactive)

    def setClickable(self, flag: bool):  # noqa: N802
        QtWidgets.QHeaderView.setSectionsClickable(self, flag)

    def setMovable(self, flag: bool):  # noqa: N802
        QtWidgets.QHeaderView.setSectionsMovable(self, flag)

    def resizeMode(self, index: int):  # noqa: N802
        QtWidgets.QHeaderView.sectionResizeMode(self, index)

    def setResizeMode(self, mode: QtWidgets.QHeaderView.ResizeMode):  # noqa: N802
        QtWidgets.QHeaderView.setSectionResizeMode(self, mode)
