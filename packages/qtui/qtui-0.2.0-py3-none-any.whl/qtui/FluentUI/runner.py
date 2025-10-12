import asyncio
import importlib.util
import os
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QGuiApplication, QIcon, QScreen
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface
from qasync import QEventLoop

from .plugins.FluentUI import registerTypes
from .plugins.FluLogger import Logger, LogSetup


class QFluentGuiApplication(QGuiApplication):
    def __init__(
        self,
        arguments: list[str],
        /,
        *,
        window_icon: QIcon | None = None,
        application_display_name: str | None = None,
        desktop_file_name: str | None = None,
        layout_direction: Qt.LayoutDirection | None = None,
        platform_name: str | None = None,
        quit_on_last_window_closed: bool = True,
        primary_screen: QScreen | None = None,
    ):
        super().__init__(
            arguments,
            windowIcon=window_icon,
            applicationDisplayName=application_display_name,
            desktopFileName=desktop_file_name,
            layoutDirection=layout_direction,
            platformName=platform_name,
            quitOnLastWindowClosed=quit_on_last_window_closed,
            primaryScreen=primary_screen,
        )
        if application_display_name is not None:
            self.setApplicationName(application_display_name)

        self.engine = QQmlApplicationEngine()
        self.event_loop = QEventLoop(self)
        self._base_path: str | Path

    def run(
        self,
        root_path: str | Path,
        base_path: str | Path | None = None,
        debug: bool = False,
    ) -> None:
        LogSetup(name=self.applicationName())

        self._base_path = base_path if base_path else os.getcwd()
        Logger().debug(f"Using resource base path: {self._base_path}")

        if debug:
            self._convert_qrc_to_rcpy(self._base_path)
        self._import_resource_files(self._base_path)

        os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
        os.environ["QT_DEBUG_PLUGINS"] = "1" if debug else "0"
        QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.OpenGL)

        asyncio.set_event_loop(self.event_loop)
        app_close_event = asyncio.Event()

        self.aboutToQuit.connect(self.engine.deleteLater)
        self.aboutToQuit.connect(app_close_event.set)

        registerTypes(self.engine)
        Logger().debug("registerTypes")
        self.engine.load(str(root_path))
        Logger().debug(f"Loaded QML file: {root_path}")

        if not self.engine.rootObjects():
            Logger().error("Failed to load QML file")
            sys.exit(-1)

        with self.event_loop:
            result = self.event_loop.run_until_complete(app_close_event.wait())  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            if result == 931:
                QProcess.startDetached(
                    self.applicationFilePath(),
                    self.arguments(),
                )
            Logger().debug(f"Exiting with result: {result}")
            sys.exit(result)  # pyright: ignore[reportUnknownArgumentType]

    def _import_resource_files(self, target_path: str | Path) -> None:
        target_path = Path(target_path)
        search_path = target_path
        Logger().debug(f"Searching for resource files (*_rc.py) in: {search_path}")

        for file_path in search_path.rglob("*_rc.py"):
            try:
                module_name = file_path.stem
                spec = importlib.util.spec_from_file_location(
                    module_name, str(file_path)
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    sys.modules[module_name] = module
                    Logger().debug(f"Successfully imported resource file: {file_path}")
                else:
                    Logger().warning(
                        f"Could not create spec for resource file: {file_path}"
                    )
            except Exception as e:
                Logger().error(f"Failed to import resource file {file_path}: {e}")

    def _convert_qrc_to_rcpy(self, target_path: str | Path) -> None:
        from .utils import rcc

        target_path = Path(target_path)
        search_path = target_path
        Logger().debug(f"Searching for resource files (*.qrc) in: {search_path}")

        for file_path in search_path.rglob("*.qrc"):
            Logger().debug(f"Converting {file_path} to rc.py")
            rcc(
                [
                    str(file_path),
                    "-o",
                    str(file_path.with_name(f"{file_path.stem}_rc.py")),
                ],
            )
