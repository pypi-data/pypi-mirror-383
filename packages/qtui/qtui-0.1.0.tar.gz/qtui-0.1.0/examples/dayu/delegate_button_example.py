from qtpy import QtCore, QtGui, QtWidgets

import examples.dayu._mock_data as mock
from qtui.dayu import utils
from qtui.dayu.item_model import MSortFilterModel, MTableModel
from qtui.dayu.item_view import MTableView
from qtui.dayu.theme import MTheme
from qtui.dayu.types import HeaderData, ModelData


class MPushButtonDelegate(QtWidgets.QStyledItemDelegate):
    sig_clicked = QtCore.Signal(object)

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.editor = None
        self.showed = False
        self.exclusive = True
        self.parent_widget = None

    def editorEvent(  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        event: QtCore.QEvent,
        model: QtCore.QAbstractItemModel,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
            index = utils.real_index(index)
            self.sig_clicked.emit(index.internalPointer())
            return True
        return False

    def paint(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        button = QtWidgets.QStyleOptionButton()
        button.rect = option.rect  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        button.text = (  # pyright: ignore[reportAttributeAccessIssue]
            "Click Me (" + str(index.data(QtCore.Qt.ItemDataRole.DisplayRole)) + ")"
        )
        button.state = QtWidgets.QStyle.StateFlag.State_Enabled  # pyright: ignore[reportAttributeAccessIssue]

        QtWidgets.QApplication.style().drawControl(
            QtWidgets.QStyle.ControlElement.CE_PushButton, button, painter
        )


header_list: list[HeaderData] = [
    {
        "label": "Name",
        "key": "name",
        "checkable": True,
        "searchable": True,
        "width": 200,
        "font": mock.font_underline,
        "icon": "user_fill.svg",
    },
    {
        "label": "Sex",
        "key": "sex",
        "searchable": True,
        "selectable": True,
        "icon": mock.sex_icon_color,
    },
    {
        "label": "Age",
        "key": "age",
        "width": 90,
        "searchable": True,
        "editable": True,
        "display": mock.age_display,
        "font": mock.font_bold,
    },
    {
        "label": "Address",
        "key": "city",
        "selectable": True,
        "searchable": True,
        "exclusive": False,
        "width": 120,
        "display": mock.city_display,
        "bg_color": mock.city_bg_color,
    },
    {
        "label": "Score",
        "key": "score",
    },
]


class DelegateButtonExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        model_1 = MTableModel()
        model_1.set_header_list(header_list)
        model_sort = MSortFilterModel()
        model_sort.setSourceModel(model_1)

        table_grid = MTableView(size=MTheme().small, show_row_count=True)
        table_grid.setShowGrid(True)
        table_grid.setModel(model_sort)
        model_sort.set_header_list(header_list)
        table_grid.set_header_list(header_list)
        button_delegate = MPushButtonDelegate(parent=self)
        table_grid.setItemDelegateForColumn(4, button_delegate)
        button_delegate.sig_clicked.connect(self.slot_cell_clicked)
        model_1.set_data_list(
            [
                {
                    "name": "John Brown",
                    "sex": "Male",
                    "sex_list": ["Male", "Female"],
                    "age": 18,
                    "score": 89,
                    "city": "New York",
                    "city_list": ["New York", "Ottawa", "London", "Sydney"],
                    "date": "2016-10-03",
                },
                {
                    "name": "Jim Green",
                    "sex": "Male",
                    "sex_list": ["Male", "Female"],
                    "age": 24,
                    "score": 55,
                    "city": "London",
                    "city_list": ["New York", "Ottawa", "London", "Sydney"],
                    "date": "2016-10-01",
                },
            ]
        )

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(table_grid)
        self.setLayout(main_lay)

    def slot_cell_clicked(self, data_dict: ModelData):
        print(data_dict)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = DelegateButtonExample()
        MTheme().apply(test)
        test.show()
