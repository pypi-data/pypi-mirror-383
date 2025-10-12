# ruff: noqa: N815 N802

from PySide6.QtCore import QObject, Signal


# noinspection PyPep8Naming
class Callback(QObject):
    start = Signal()
    finish = Signal()
    error = Signal(int, str, str)
    success = Signal(str)

    def __init__(self):
        QObject.__init__(self)

    def onStart(self):
        self.start.emit()

    def onFinish(self):
        self.finish.emit()

    def onSuccess(self, result: str = ""):
        self.success.emit(result)

    def onError(self, code: int = -1, error_string: str = "", result: str = ""):
        self.error.emit(code, error_string, result)
