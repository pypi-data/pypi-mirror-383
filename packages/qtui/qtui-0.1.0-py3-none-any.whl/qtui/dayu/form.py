from qtpy import QtCore, QtWidgets

from .label import MLabel


class MForm(QtWidgets.QWidget):
    Horizontal = "horizontal"
    Vertical = "vertical"
    Inline = "inline"

    def __init__(
        self, layout: str | None = None, parent: QtWidgets.QWidget | None = None
    ):
        super().__init__(parent)
        layout = layout or MForm.Horizontal
        if layout == MForm.Inline:
            self._main_layout = QtWidgets.QHBoxLayout()
        elif layout == MForm.Vertical:
            self._main_layout = QtWidgets.QVBoxLayout()
        else:
            self._main_layout = QtWidgets.QFormLayout()
        self._model = None
        self._label_list: list[MLabel] = []

    def set_model(self, m: QtCore.QAbstractItemModel):
        self._model = m

    def set_label_align(self, align: QtCore.Qt.AlignmentFlag):
        for label in self._label_list:
            label.setAlignment(align)
        if isinstance(self._main_layout, QtWidgets.QFormLayout):
            self._main_layout.setLabelAlignment(align)

    @classmethod
    def horizontal(cls):
        return cls(layout=cls.Horizontal)

    @classmethod
    def vertical(cls):
        return cls(layout=cls.Vertical)

    @classmethod
    def inline(cls):
        return cls(layout=cls.Inline)
