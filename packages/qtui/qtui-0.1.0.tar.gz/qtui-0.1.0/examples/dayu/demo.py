import codecs
import importlib
import os
from pathlib import Path

from qtpy import QtCore, QtWidgets

from qtui.dayu.dock_widget import MDockWidget
from qtui.dayu.item_view_set import MItemViewSet
from qtui.dayu.theme import MTheme
from qtui.dayu.types import ModelData


def get_test_widget() -> list[tuple[str, type[QtWidgets.QWidget], list[str]]]:
    result: list[tuple[str, type[QtWidgets.QWidget], list[str]]] = []
    file = Path(__file__)
    directory = file.parent
    for f in directory.iterdir():
        if f.stem.startswith("__") or (not f.suffix == ".py") or f.name == file.name:
            continue
        name = f.stem
        module_name = f"examples.dayu.{name}"
        class_name = "".join(x.title() for x in name.split("_"))
        module = importlib.import_module(module_name, class_name)
        if hasattr(module, class_name):
            with codecs.open(
                os.path.join(directory, f"{name}.py"), encoding="utf-8"
            ) as f:
                result.append((name, getattr(module, class_name), f.readlines()))
    return result


class MDemo(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Dayu Widgets Demo")
        self._init_ui()

    def _init_ui(self):
        self.text_edit = QtWidgets.QTextEdit()
        self.stacked_widget = QtWidgets.QStackedWidget()

        list_widget = MItemViewSet(view_type=MItemViewSet.ListViewType)
        list_widget.set_header_list(
            [{"key": "name", "label": "Name", "icon": "list_view.svg"}]
        )
        list_widget.sig_left_clicked.connect(self.slot_change_widget)
        data_list: list[ModelData] = []
        for _index, (name, cls, code) in enumerate(get_test_widget()):
            data_list.append({"name": name[:-8], "data": code})
            if not callable(cls):
                continue
            widget = cls()
            widget.setProperty("code", code)
            self.stacked_widget.addWidget(widget)
        list_widget.setup_data(data_list)

        test_widget = MDockWidget("Example List")
        test_widget.setWidget(list_widget)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, test_widget)

        code_widget = MDockWidget("Example Code")
        code_widget.setWidget(self.text_edit)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, code_widget)
        self.setCentralWidget(self.stacked_widget)

    def slot_change_widget(self, index: QtCore.QModelIndex):
        self.stacked_widget.setCurrentIndex(index.row())
        widget = self.stacked_widget.widget(index.row())
        self.text_edit.setPlainText("".join(widget.property("code")))


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.append(Path(__file__).parents[2].as_posix())

    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = MDemo()
        MTheme().apply(test)
        test.show()
