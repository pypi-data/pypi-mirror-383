# pyright: reportRedeclaration=none, reportCallIssue=none, reportArgumentType=none
# ruff: noqa: N815 N802

import sys
from pathlib import Path

sys.path.append(Path(__file__).parents[2].as_posix())

from PySide6.QtCore import Property, QObject, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import qmlRegisterType
from qasync import asyncSlot  # pyright: ignore[reportUnknownVariableType]

from examples.FluentUI import PROJECT_ROOT
from examples.FluentUI.component.Callback import Callback
from examples.FluentUI.component.CircularReveal import CircularReveal
from examples.FluentUI.component.FileWatcher import FileWatcher
from examples.FluentUI.component.FpsItem import FpsItem
from examples.FluentUI.component.OpenGLItem import OpenGLItem
from examples.FluentUI.helper import Async
from examples.FluentUI.helper.SettingsHelper import SettingsHelper
from examples.FluentUI.helper.TranslateHelper import TranslateHelper
from qtui.FluentUI import QFluentGuiApplication, Singleton

_uri = "demo"
_major = 1
_minor = 0


@Singleton
class AppInfo(QObject):
    versionChanged = Signal()

    @Property(str, notify=versionChanged)
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str):
        self._version = value
        self.versionChanged.emit()

    def __init__(self):
        super().__init__(QGuiApplication.instance())
        self._version = "1.7.6"

    @asyncSlot(Callback)
    async def checkUpdate(self, callback: Callback):
        callback.onStart()
        try:
            r = await Async.http().get(
                "https://api.github.com/repos/zhuzichu520/FluentUI/releases/latest"
            )
            callback.onSuccess(await r.text())
        except Exception as exc:
            callback.onError(error_string=f"Error: {exc}")
        finally:
            callback.onFinish()


# noinspection PyTypeChecker
def main():
    app = QFluentGuiApplication(sys.argv, application_display_name="FluentUI Demo")

    qmlRegisterType(Callback, _uri, _major, _minor, "Callback")
    qmlRegisterType(CircularReveal, _uri, _major, _minor, "CircularReveal")
    qmlRegisterType(FileWatcher, _uri, _major, _minor, "FileWatcher")
    qmlRegisterType(FpsItem, _uri, _major, _minor, "FpsItem")
    qmlRegisterType(OpenGLItem, _uri, _major, _minor, "OpenGLItem")

    app.event_loop.create_task(Async.boot())
    app.aboutToQuit.connect(lambda: app.event_loop.create_task(Async.delete()))

    TranslateHelper().init(app.engine)
    context = app.engine.rootContext()
    context.setContextProperty("AppInfo", AppInfo())
    context.setContextProperty("SettingsHelper", SettingsHelper())
    context.setContextProperty("TranslateHelper", TranslateHelper())

    app.run("qrc:/example/qml/App.qml", base_path=PROJECT_ROOT, debug=True)


if __name__ == "__main__":
    main()
