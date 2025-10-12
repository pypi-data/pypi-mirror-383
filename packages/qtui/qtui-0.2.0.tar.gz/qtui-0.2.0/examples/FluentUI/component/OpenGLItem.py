# pyright: reportRedeclaration=none
# ruff: noqa: N815 N802

from collections.abc import Sequence

from OpenGL import GL
from PySide6.QtCore import Property, QSize, QTimerEvent, Signal
from PySide6.QtGui import QOpenGLFunctions
from PySide6.QtOpenGL import (
    QOpenGLFramebufferObject,
    QOpenGLFramebufferObjectFormat,
    QOpenGLShader,
    QOpenGLShaderProgram,
)
from PySide6.QtQuick import QQuickFramebufferObject


# noinspection PyTypeChecker,PyPep8Naming
class OpenGLItem(QQuickFramebufferObject):
    tChanged = Signal()

    def __init__(self):
        QQuickFramebufferObject.__init__(self)
        self.__render = None
        self.setMirrorVertically(True)
        self.startTimer(1)
        self._t = 0

    def timerEvent(self, event: QTimerEvent):
        self.update()

    def createRenderer(self):
        self.__render = OpenGLItem.FBORenderer(self)
        return self.__render

    @Property(float, notify=tChanged)
    def t(self) -> float:
        return self._t

    @t.setter
    def t(self, value: float):
        self._t = value
        self.tChanged.emit()

    class FBORenderer(QQuickFramebufferObject.Renderer, QOpenGLFunctions):
        def __init__(self, item: "OpenGLItem"):
            QQuickFramebufferObject.Renderer.__init__(self)
            QOpenGLFunctions.__init__(self)
            self.item: OpenGLItem = item
            self.program = QOpenGLShaderProgram()
            self.__openGLFb = None
            self.initializeOpenGLFunctions()
            self.program.addCacheableShaderFromSourceCode(
                QOpenGLShader.ShaderTypeBit.Vertex,
                "attribute highp vec4 vertices;"
                "varying highp vec2 coords;"
                "void main() {"
                "    gl_Position = vertices;"
                "    coords = vertices.xy;"
                "}",
            )
            self.program.addCacheableShaderFromSourceCode(
                QOpenGLShader.ShaderTypeBit.Fragment,
                "uniform lowp float t;"
                "varying highp vec2 coords;"
                "void main() {"
                "    lowp float i = 1. - (pow(abs(coords.x), 4.) + pow(abs(coords.y), 4.));"  # noqa: E501
                "    i = smoothstep(t - 0.8, t + 0.8, i);"
                "    i = floor(i * 20.) / 20.;"
                "    gl_FragColor = vec4(coords * .5 + .5, i, i);"
                "}",
            )
            self.program.bindAttributeLocation("vertices", 0)
            self.program.link()

        def createFramebufferObject(self, size: QSize) -> QOpenGLFramebufferObject:
            fmt = QOpenGLFramebufferObjectFormat()
            fmt.setAttachment(QOpenGLFramebufferObject.Attachment.CombinedDepthStencil)
            fmt.setSamples(4)
            self.__openGLFb = QOpenGLFramebufferObject(size, fmt)
            return self.__openGLFb

        def render(self):
            pixel_ratio = self.item.window().devicePixelRatio()
            self.glClearColor(0, 0, 0, 0)
            self.glEnable(GL.GL_DEPTH_TEST)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # pyright: ignore[reportUnknownMemberType, reportOperatorIssue, reportUnknownArgumentType]
            self.program.bind()
            self.program.enableAttributeArray(0)
            self.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]

            values: Sequence[float] = [-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0]
            self.program.setAttributeArray(0, values, 2, 0)
            self.program.setUniformValue1f("t", float(self.item._t))  # pyright: ignore[reportCallIssue, reportArgumentType]
            self.glViewport(
                0,
                0,
                int(self.item.width() * pixel_ratio),
                int(self.item.height() * pixel_ratio),
            )
            self.glDisable(GL.GL_DEPTH_TEST)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            self.glEnable(GL.GL_BLEND)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            self.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            self.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            self.program.disableAttributeArray(0)
            self.program.release()
