import contextlib
import signal
import sys
from pathlib import Path
from typing import Generic, TypeVar

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtSvg import QSvgRenderer

T = TypeVar("T", bound=QtGui.QPixmap | QtGui.QIcon)


class MStaticCacheDict(Generic[T]):
    _render = QSvgRenderer()

    def __init__(self, cls: type[T]):
        super().__init__()
        self.cls = cls
        self._cache_pix_dict: dict[str, T] = {}

    def _render_svg(self, svg_path: str, replace_color: str = "") -> T:
        from ..theme import MTheme

        replace_color = replace_color or MTheme().icon_color

        data_content = Path(svg_path).read_text().replace("#555555", replace_color)
        self._render.load(QtCore.QByteArray(data_content.encode()))
        pix = QtGui.QPixmap(128, 128)
        pix.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pix)
        self._render.render(painter)
        painter.end()
        return self.cls(pix)

    def __call__(self, name: str, color: str | None = "") -> T:
        from ..utils import get_static_file

        try:
            color = color or ""
            full_path = get_static_file(name).as_posix()
            key = f"{full_path.lower()}{color}"
            pix_map = self._cache_pix_dict.get(key)
            if pix_map is None:
                if full_path.endswith("svg"):
                    pix_map = self._render_svg(full_path, color)
                else:
                    pix_map = self.cls(full_path)
                self._cache_pix_dict[key] = pix_map
            return pix_map
        except FileNotFoundError:
            return self.cls()


def get_scale_factor() -> tuple[float, float]:
    """
    Get the scale factor for the x and y dimensions.

    Args:
        None
    Returns:
        tuple[float, float]: The scale factor for the x and y dimensions.
    """
    if not QtWidgets.QApplication.instance():
        QtWidgets.QApplication([])
    standard_dpi = 96.0
    scale_factor_x = (
        QtWidgets.QApplication.primaryScreen().logicalDotsPerInchX() / standard_dpi
    )
    scale_factor_y = (
        QtWidgets.QApplication.primaryScreen().logicalDotsPerInchY() / standard_dpi
    )
    return scale_factor_x, scale_factor_y


@contextlib.contextmanager
def application():
    app = QtWidgets.QApplication.instance()

    if not app:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        app = QtWidgets.QApplication(sys.argv)
        yield app
        app.exec()
    else:
        yield app


MPixmap = MStaticCacheDict(QtGui.QPixmap)
MIcon = MStaticCacheDict(QtGui.QIcon)
