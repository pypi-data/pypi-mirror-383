"""
MClickBrowserFilePushButton, MClickBrowserFileToolButton
MClickBrowserFolderPushButton, MClickBrowserFolderToolButton
Browser files or folders by selecting.
MDragFileButton, MDragFolderButton
Browser files or folders by dragging.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from qtpy import QtCore, QtGui, QtWidgets

from .mixin import cursor_mixin, property_mixin
from .push_button import MPushButton
from .theme import MTheme
from .tool_button import MToolButton


class MBrowserButton(QtWidgets.QWidget if TYPE_CHECKING else object):
    """
    Browser button mixin class.

    WARNING: This class must be used with multiple inheritance
    alongside a QWidget subclass (MPushButton, MToolButton, etc.)

    Example:
        class MyButton(MPushButton, MBrowserButton):  # Correct
            pass

        class WrongButton(MBrowserButton):  # Wrong - will not work
            pass
    """

    sig_file_changed = QtCore.Signal(str)
    sig_files_changed = QtCore.Signal(list)
    sig_folder_changed = QtCore.Signal(str)
    sig_folders_changed = QtCore.Signal(list)

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__()
        self._path: str = ""
        self._multiple: bool = False
        self._filters: list[str] = []

    def get_dayu_filters(self) -> list[str]:
        return self._filters

    def set_dayu_filters(self, value: list[str]) -> None:
        if value != self._filters:
            self._filters = value

    def get_dayu_path(self) -> str:
        return self._path

    def set_dayu_path(self, value: str) -> None:
        if value != self._path:
            self._path = value

    def get_dayu_multiple(self) -> bool:
        return self._multiple

    def set_dayu_multiple(self, value: bool) -> None:
        if value != self._multiple:
            self._multiple = value

    dayu_path = QtCore.Property(str, get_dayu_path, set_dayu_path)
    dayu_multiple = QtCore.Property(bool, get_dayu_multiple, set_dayu_multiple)
    dayu_filters = QtCore.Property(list, get_dayu_filters, set_dayu_filters)

    @QtCore.Slot()
    def slot_browser_file(self) -> None:
        filter_list = (
            f"File({' '.join(['*' + e for e in self.get_dayu_filters()])})"
            if self.get_dayu_filters()
            else "Any File(*)"
        )
        if self.get_dayu_multiple():
            r_files, _ = QtWidgets.QFileDialog.getOpenFileNames(
                self, "Browser File", self.get_dayu_path(), filter_list
            )
            if r_files:
                self.sig_files_changed.emit(r_files)
                self.set_dayu_path(r_files[0])
        else:
            r_file, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Browser File", self.get_dayu_path(), filter_list
            )
            if r_file:
                self.sig_file_changed.emit(r_file)
                self.set_dayu_path(r_file)

    @QtCore.Slot()
    def slot_browser_folder(self) -> None:
        r_folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Browser Folder", self.get_dayu_path()
        )
        if r_folder:
            self.sig_folder_changed.emit(r_folder)
            self.set_dayu_path(r_folder)

    @QtCore.Slot()
    def slot_save_file(self) -> None:
        filter_list = (
            f"File({' '.join(['*' + e for e in self.get_dayu_filters()])})"
            if self.get_dayu_filters()
            else "Any File(*)"
        )
        r_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", self.get_dayu_path(), filter_list
        )
        if r_file:
            self.sig_file_changed.emit(r_file)
            self.set_dayu_path(r_file)


class MClickBrowserFilePushButton(MPushButton, MBrowserButton):
    """A Clickable push button to browser files"""

    def __init__(
        self,
        text: str = "Browser",
        multiple: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(text=text, parent=parent)
        self.set_dayu_multiple(multiple)
        self.setToolTip("Click to browser file")
        self.clicked.connect(self.slot_browser_file)


class MClickBrowserFileToolButton(MToolButton, MBrowserButton):
    """A Clickable tool button to browser files"""

    def __init__(
        self,
        multiple: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.set_dayu_multiple(multiple)
        self.setToolTip("Click to browser file")
        self.svg("cloud_line.svg").icon_only()
        self.clicked.connect(self.slot_browser_file)


class MClickSaveFileToolButton(MToolButton, MBrowserButton):
    """A Clickable tool button to browser files"""

    def __init__(
        self,
        multiple: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.set_dayu_multiple(multiple)
        self.setToolTip("Click to save file")
        self.svg("save_line.svg").icon_only()
        self.clicked.connect(self.slot_browser_file)


class MDragFileButton(MToolButton, MBrowserButton):
    """A Clickable and draggable tool button to upload files"""

    def __init__(
        self,
        text: str = "",
        multiple: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.set_dayu_multiple(multiple)
        self.setToolTip("Click or drag file here")
        self.svg("cloud_line.svg").text_under_icon().setText(text)

        size = MTheme().drag_size
        self.set_dayu_size(size)
        self.setIconSize(QtCore.QSize(size, size))

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.clicked.connect(self.slot_browser_file)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:  # noqa: N802
        """Override dragEnterEvent. Validate dragged files"""
        if event.mimeData().hasFormat("text/uri-list"):
            count = len(event.mimeData().urls())
            if count == 1 or (count > 1 and self.get_dayu_multiple()):
                event.acceptProposedAction()
                return

    def dropEvent(self, event: QtGui.QDropEvent) -> None:  # noqa: N802
        """Override dropEvent to accept the dropped files"""
        file_list = self._get_valid_file_list(event.mimeData().urls())
        if not file_list:
            return
        if self.get_dayu_multiple():
            self.sig_files_changed.emit(file_list)
        else:
            self.sig_file_changed.emit(file_list[0])
        self.set_dayu_path(file_list[0])

    def _get_valid_file_list(self, url_list: list[QtCore.QUrl]) -> list[str]:
        file_list: list[str] = []
        for url in url_list:
            path = Path(url.toLocalFile())
            if path.is_file() and (
                not self.get_dayu_filters() or path.suffix in self.get_dayu_filters()
            ):
                file_list.append(path.as_posix())
        return file_list


class MClickBrowserFolderPushButton(MPushButton, MBrowserButton):
    """A Clickable push button to browser folders"""

    def __init__(
        self,
        text: str = "",
        multiple: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(text=text, parent=parent)
        self.set_dayu_multiple(multiple)
        self.setToolTip("Click to browser folder")
        self.clicked.connect(self.slot_browser_folder)


@property_mixin
class MClickBrowserFolderToolButton(MToolButton, MBrowserButton):
    """A Clickable tool button to browser folders"""

    def __init__(
        self,
        multiple: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.set_dayu_multiple(multiple)
        self.setToolTip("Click to browser folder")
        self.svg("folder_line.svg").icon_only()
        self.clicked.connect(self.slot_browser_folder)


@property_mixin
@cursor_mixin
class MDragFolderButton(MToolButton, MBrowserButton):
    """A Clickable and draggable tool button to browser folders"""

    def __init__(
        self,
        multiple: bool = False,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.set_dayu_multiple(multiple)
        self.setToolTip("Click or drag folder here")
        self.svg("folder_line.svg").text_under_icon().setText(
            "Click or drag folder here"
        )

        size = MTheme().drag_size
        self.set_dayu_size(size)
        self.setIconSize(QtCore.QSize(size, size))
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        self.clicked.connect(self.slot_browser_folder)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:  # noqa: N802
        """Override dragEnterEvent. Validate dragged folders"""
        if event.mimeData().hasFormat("text/uri-list"):
            count = len(event.mimeData().urls())
            if count == 1 or (count > 1 and self.get_dayu_multiple()):
                event.acceptProposedAction()
                return

    def dropEvent(self, event: QtGui.QDropEvent) -> None:  # noqa: N802
        """Override dropEvent to accept the dropped folders"""
        folder_list: list[str] = []
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.is_dir():
                folder_list.append(path.as_posix())

        if not folder_list:
            return

        if self.get_dayu_multiple():
            self.sig_folders_changed.emit(folder_list)
        else:
            self.sig_folder_changed.emit(folder_list[0])
        self.set_dayu_path(folder_list[0])
