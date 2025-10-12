# pyright: basic, reportAttributeAccessIssue=none
# ruff: noqa: N815 N802

import base64
import sys

from PySide6.QtCore import (
    QCryptographicHash,
    QDateTime,
    QDir,
    QFile,
    QFileInfo,
    QObject,
    QPoint,
    QProcess,
    QRect,
    QSettings,
    QSysInfo,
    Qt,
    QUrl,
    QUuid,
    Slot,
    qVersion,
)
from PySide6.QtGui import QColor, QCursor, QGuiApplication, QIcon, QTextDocument
from PySide6.QtQuick import QQuickWindow

from .Singleton import Singleton

if sys.platform.startswith("win"):
    from ctypes import (
        WinDLL,
        addressof,
        c_bool,
        c_uint,
        c_void_p,
        create_unicode_buffer,
        wstring_at,
    )

    user32 = WinDLL("user32")

    SystemParametersInfoW = user32.SystemParametersInfoW
    SystemParametersInfoW.argtypes = [c_uint, c_uint, c_void_p, c_uint]
    SystemParametersInfoW.restype = c_bool

    def SystemParametersInfoW():
        b_path = create_unicode_buffer(260)
        result = bool(user32.SystemParametersInfoW(0x0073, 260, b_path, 0))
        if result:
            return str(wstring_at(addressof(b_path)))
        return None


# noinspection PyPep8Naming
@Singleton
class FluTools(QObject):
    def __init__(self):
        QObject.__init__(self, QGuiApplication.instance())

    @Slot(str)
    def clipText(self, val: str):
        QGuiApplication.clipboard().setText(val)

    @Slot(result=str)
    def uuid(self):
        return (
            QUuid.createUuid()
            .toString()
            .replace("-", "")
            .replace("{", "")
            .replace("}", "")
        )

    @Slot(result=bool)
    def isMacos(self):
        return sys.platform.startswith("darwin")

    @Slot(result=bool)
    def isLinux(self):
        return sys.platform.startswith("linux")

    @Slot(result=bool)
    def isWin(self):
        return sys.platform.startswith("win")

    @Slot(result=int)
    def qtMajor(self):
        return int(qVersion().split(".")[0])

    @Slot(result=int)
    def qtMinor(self):
        return int(qVersion().split(".")[1])

    @Slot(bool)
    def setQuitOnLastWindowClosed(self, val):
        QGuiApplication.setQuitOnLastWindowClosed(val)

    @Slot(int)
    def setOverrideCursor(self, val):
        QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape(val)))

    @Slot()
    def restoreOverrideCursor(self):
        QGuiApplication.restoreOverrideCursor()

    @Slot(QObject)
    def deleteLater(self, val: QObject):
        if val is not None:
            val.deleteLater()

    @Slot(QUrl, result=str)
    def toLocalPath(self, url: QUrl):
        return url.toLocalFile()

    @Slot(QUrl, result=str)
    def getFileNameByUrl(self, url: QUrl):
        return QFileInfo(url.toLocalFile()).fileName()

    @Slot(str, result=str)
    def html2PlantText(self, html: str):
        text_document = QTextDocument()
        text_document.setHtml(html)
        return text_document.toPlainText()

    @Slot(result=QRect)
    def getVirtualGeometry(self):
        return QGuiApplication.primaryScreen().virtualGeometry()

    @Slot(result=str)
    def getApplicationDirPath(self):
        return QGuiApplication.applicationDirPath()

    @Slot(str, result=QUrl)
    def getUrlByFilePath(self, path: str):
        return QUrl.fromLocalFile(path)

    @Slot(QColor, float, result=QColor)
    def withOpacity(self, color: QColor, opacity: float) -> QColor:
        alpha = int(opacity * 255) & 0xFF
        return QColor.fromRgba((alpha << 24) | (color.rgba() & 0xFFFFFF))

    @Slot(str, result=str)
    def md5(self, val: str):
        return QCryptographicHash.hash(
            bytearray(val, "utf-8"), QCryptographicHash.Algorithm.Md5
        ).toHex()

    @Slot(str, result=str)
    def sha256(self, val: str):
        return QCryptographicHash.hash(
            bytearray(val, "utf-8"), QCryptographicHash.Algorithm.Sha256
        ).toHex()

    @Slot(str, result=str)
    def toBase64(self, val):
        return base64.b64encode(val)

    @Slot(str, result=str)
    def fromBase64(self, val):
        return base64.b64decode(val)

    @Slot(str, result=bool)
    def removeDir(self, path: str):
        target = QDir(path)
        return target.removeRecursively()

    @Slot(str, result=bool)
    def removeFile(self, path: str):
        target = QFile(path)
        return target.remove()

    @Slot(str)
    def showFileInFolder(self, path: str):
        if sys.platform.startswith("win"):
            process = "explorer.exe"
            arguments = ["/select,", QDir.toNativeSeparators(path)]
            QProcess.startDetached(process, arguments)
        elif sys.platform.startswith("linux"):
            file_info = QFileInfo(path)
            process = "xdg-open"
            arguments = [file_info.absoluteDir().absolutePath()]
            QProcess.startDetached(process, arguments)
        elif sys.platform.startswith("darwin"):
            process = "/usr/bin/osascript"
            arguments = [
                "-e",
                'tell application "Finder" to reveal POSIX file "' + path + '"',
            ]
            QProcess.execute(process, arguments)
            arguments = ["-e", 'tell application "Finder" to activate']
            QProcess.execute(process, arguments)

    @Slot(result=bool)
    def isSoftware(self):
        return QQuickWindow.sceneGraphBackend == "software"

    @Slot(result=QPoint)
    def cursorPos(self):
        return QCursor.pos()

    @Slot(result=int)
    def currentTimestamp(self):
        return QDateTime.currentDateTime()

    @Slot(result=QIcon)
    def windowIcon(self):
        return QGuiApplication.windowIcon()

    @Slot(result=int)
    def cursorScreenIndex(self):
        screen_index = 0
        screen_count = len(QGuiApplication.screens())
        if screen_count > 1:
            pos = QCursor.pos()
            for i in range(screen_count):
                if QGuiApplication.screens()[i].geometry().contains(pos):
                    screen_index = i
                    break
        return screen_index

    @Slot(result=int)
    def windowBuildNumber(self):
        if self.isWin():
            reg_key = QSettings(
                "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
                QSettings.Format.NativeFormat,
            )
            if reg_key.contains("CurrentBuildNumber"):
                build_number = int(reg_key.value("CurrentBuildNumber"))
                return build_number
        return -1

    @Slot(result=bool)
    def isWindows11OrGreater(self):
        var = getattr(self, "_isWindows11OrGreater", None)
        if var is None:
            if self.isWin():
                build_number = self.windowBuildNumber()
                if build_number >= 22000:
                    var = True
                else:
                    var = False
            else:
                var = False
            self._isWindows11OrGreater = var
        return bool(var)

    @Slot(result=bool)
    def isWindows10OrGreater(self):
        var = getattr(self, "_isWindows10OrGreater", None)
        if var is None:
            if self.isWin():
                build_number = self.windowBuildNumber()
                if build_number >= 10240:
                    var = True
                else:
                    var = False
            else:
                var = False
            self._isWindows10OrGreater = var
        return bool(var)

    @Slot(QQuickWindow, result=QRect)
    def desktopAvailableGeometry(self, window: QQuickWindow):
        return window.screen().availableGeometry()

    @Slot(result=str)
    def getWallpaperFilePath(self) -> str:
        if self.isWin():
            path = SystemParametersInfoW()
            if path is not None:
                return path
        elif self.isLinux():
            product_type = QSysInfo.productType()
            if product_type == "UOS":
                process = QProcess()
                args = [
                    "--session",
                    "--type=method_call",
                    "--print-reply",
                    "--dest=com.deepin.wm",
                    "/com/deepin/wm",
                    "com.deepin.wm.GetCurrentWorkspaceBackgroundForMonitor",
                    f"string:'${self.currentTimestamp()}'",
                ]
                process.start("dbus-send", args)
                process.waitForFinished()
                result = process.readAllStandardOutput().trimmed()
                start_index = result.indexOf(b"file:///")
                if start_index != -1:
                    path = result.mid(
                        start_index + 7, result.length() - start_index - 8
                    )
                    return str(path)
        elif self.isMacos():
            process = QProcess()
            args = [
                "-e",
                'tell application "Finder" to get POSIX path of (desktop picture as alias)',  # noqa: E501
            ]
            process.start("osascript", args)
            process.waitForFinished()
            path = process.readAllStandardOutput().trimmed()
            if path.isEmpty():
                return "/System/Library/CoreServices/DefaultDesktop.heic"
            return str(path)
        return ""
