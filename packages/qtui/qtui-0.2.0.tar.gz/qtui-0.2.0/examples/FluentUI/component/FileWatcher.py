# pyright: reportRedeclaration=none
# ruff: noqa: N815 N802

from PySide6.QtCore import Property, QFileSystemWatcher, QObject, Signal


# noinspection PyUnresolvedReferences,PyPep8Naming
class FileWatcher(QObject):
    pathChanged = Signal()
    fileChanged = Signal()

    @Property(str, notify=pathChanged)
    def path(self):
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = value
        self.pathChanged.emit()

    def __init__(self):
        QObject.__init__(self)
        self._path: str = ""
        self._watcher: QFileSystemWatcher = QFileSystemWatcher()

        def onFileChanged(path: str):
            self.fileChanged.emit()
            self.clean()
            self._watcher.addPath(path)

        self._watcher.fileChanged.connect(onFileChanged)

        def onPathChanged():
            self.clean()
            self._watcher.addPath(self._path.replace("file:///", ""))

        self.pathChanged.connect(lambda: onPathChanged())
        if self._path != "":
            self._watcher.addPath(self._path)

    def clean(self):
        for item in self._watcher.files():
            self._watcher.removePath(item)
