"""
mixin decorators to add Qt class feature.
"""

from typing import Any, TypeVar, cast

from qtpy import QtCore, QtGui, QtWidgets

T = TypeVar(
    "T",
    bound=QtWidgets.QWidget,
)


def property_mixin(
    cls: type[T],
) -> type[T]:
    """Run function after dynamic property value changed"""

    def _new_event(self: T, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.DynamicPropertyChange:
            event = cast(QtCore.QDynamicPropertyChangeEvent, event)
            prp = cast(str, event.propertyName().data().decode())  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            if hasattr(self, f"_set_{prp}"):
                callback = getattr(self, f"_set_{prp}")
                callback(self.property(str(prp)))
        return super(cls, self).event(event)

    cls.event = _new_event
    return cls


def cursor_mixin(cls: type[T]) -> type[T]:
    """
    Change Widget cursor:
    when user mouse in: Qt.PointingHandCursor;
    when widget is disabled and mouse in: Qt.ForbiddenCursor
    """

    old_enter_event = cls.enterEvent
    old_leave_event = cls.leaveEvent
    old_hide_event = cls.hideEvent
    old_focus_out_event = cls.focusOutEvent

    def _revert_cursor(self: T) -> None:
        if self.__dict__.get("__dayu_enter", False):
            while self.__dict__.get("__dayu_enter_count", 0) > 0:
                QtWidgets.QApplication.restoreOverrideCursor()
                self.__dict__.update(
                    {
                        "__dayu_enter_count": self.__dict__.get("__dayu_enter_count", 0)
                        - 1
                    }
                )
            self.__dict__.update({"__dayu_enter": False})

    def _new_enter_event(self: T, *args: Any, **kwargs: Any) -> None:
        self.__dict__.update({"__dayu_enter": True})
        self.__dict__.update(
            {"__dayu_enter_count": self.__dict__.get("__dayu_enter_count", 0) + 1}
        )
        QtWidgets.QApplication.setOverrideCursor(
            QtCore.Qt.CursorShape.PointingHandCursor
            if self.isEnabled()
            else QtCore.Qt.CursorShape.ForbiddenCursor
        )
        return old_enter_event(self, *args, **kwargs)

    def _new_leave_event(self: T, *args: Any, **kwargs: Any) -> None:
        _revert_cursor(self)
        return old_leave_event(self, *args, **kwargs)

    def _new_hide_event(self: T, *args: Any, **kwargs: Any) -> None:
        _revert_cursor(self)
        return old_hide_event(self, *args, **kwargs)

    def _new_focus_out_event(self: T, *args: Any, **kwargs: Any) -> None:
        _revert_cursor(self)
        return old_focus_out_event(self, *args, **kwargs)

    cls.enterEvent = _new_enter_event
    cls.leaveEvent = _new_leave_event
    cls.hideEvent = _new_hide_event
    cls.focusOutEvent = _new_focus_out_event
    return cls


def focus_shadow_mixin(cls: type[T]) -> type[T]:
    """
    Add shadow effect for decorated class when widget focused
    When focus in target widget, enable shadow effect.
    When focus out target widget, disable shadow effect.
    """
    old_focus_in_event = cls.focusInEvent
    old_focus_out_event = cls.focusOutEvent

    def _new_focus_in_event(self: T, *args: Any, **kwargs: Any) -> None:
        old_focus_in_event(self, *args, **kwargs)
        graphics_effects = self.graphicsEffect()
        if not graphics_effects:
            from .theme import MTheme

            shadow_effect = QtWidgets.QGraphicsDropShadowEffect(self)
            dayu_type = self.property("dayu_type")
            color = vars(MTheme()).get(f"{dayu_type or 'primary'}_color")
            shadow_effect.setColor(QtGui.QColor(color))
            shadow_effect.setOffset(0, 0)
            shadow_effect.setBlurRadius(5)
            shadow_effect.setEnabled(False)
            self.setGraphicsEffect(shadow_effect)
        else:
            if self.isEnabled():
                graphics_effects.setEnabled(True)

    def _new_focus_out_event(self: T, *args: Any, **kwargs: Any) -> None:
        old_focus_out_event(self, *args, **kwargs)
        graphics_effects = self.graphicsEffect()
        if graphics_effects:
            graphics_effects.setEnabled(False)

    cls.focusInEvent = _new_focus_in_event
    cls.focusOutEvent = _new_focus_out_event
    return cls


def hover_shadow_mixin(cls: type[T]) -> type[T]:
    """
    Add shadow effect for decorated class when widget hovered
    When mouse enter target widget, enable shadow effect.
    When mouse leave target widget, disable shadow effect.
    """
    old_enter_event = cls.enterEvent
    old_leave_event = cls.leaveEvent

    def _new_enter_event(self: T, *args: Any, **kwargs: Any) -> None:
        old_enter_event(self, *args, **kwargs)
        graphics_effects = self.graphicsEffect()
        if not graphics_effects:
            from .theme import MTheme

            shadow_effect = QtWidgets.QGraphicsDropShadowEffect(self)
            dayu_type = self.property("type")
            color = vars(MTheme()).get(f"{dayu_type or 'primary'}_color")
            shadow_effect.setColor(QtGui.QColor(color))
            shadow_effect.setOffset(0, 0)
            shadow_effect.setBlurRadius(5)
            shadow_effect.setEnabled(False)
            self.setGraphicsEffect(shadow_effect)
        else:
            if self.isEnabled():
                graphics_effects.setEnabled(True)

    def _new_leave_event(self: T, *args: Any, **kwargs: Any) -> None:
        old_leave_event(self, *args, **kwargs)
        graphics_effects = self.graphicsEffect()
        if graphics_effects:
            graphics_effects.setEnabled(False)

    cls.enterEvent = _new_enter_event
    cls.leaveEvent = _new_leave_event
    return cls


def _stackable(widget: Any) -> bool:
    """Used for stacked_animation_mixin to only add mixin for widget who can stacked."""
    # We use widget() to get currentWidget, use currentChanged to play the animation.
    # For now just QTabWidget and QStackedWidget can use this decorator.
    return (
        issubclass(widget, QtWidgets.QWidget)
        and hasattr(widget, "widget")
        and hasattr(widget, "currentChanged")
    )


def stacked_animation_mixin(cls: type[T]) -> type[T]:
    """
    Decorator for stacked widget.
    When Stacked widget currentChanged, show opacity and
    position animation for current widget.
    """
    if not _stackable(cls):  # If widget can't stack, return the original widget class
        return cls
    old_init = cls.__init__

    def _new_init(self: T, *args: Any, **kwargs: Any):
        old_init(self, *args, **kwargs)
        self._previous_index = 0  # pyright: ignore[reportAttributeAccessIssue]
        self._to_show_pos_ani = QtCore.QPropertyAnimation()  # pyright: ignore[reportAttributeAccessIssue]
        self._to_show_pos_ani.setDuration(400)  # pyright: ignore[reportAttributeAccessIssue]
        self._to_show_pos_ani.setPropertyName(b"pos")  # pyright: ignore[reportAttributeAccessIssue]
        self._to_show_pos_ani.setEndValue(QtCore.QPoint(0, 0))  # pyright: ignore[reportAttributeAccessIssue]
        self._to_show_pos_ani.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)  # pyright: ignore[reportAttributeAccessIssue]

        self._to_hide_pos_ani = QtCore.QPropertyAnimation()  # pyright: ignore[reportAttributeAccessIssue]
        self._to_hide_pos_ani.setDuration(400)  # pyright: ignore[reportAttributeAccessIssue]
        self._to_hide_pos_ani.setPropertyName(b"pos")  # pyright: ignore[reportAttributeAccessIssue]
        self._to_hide_pos_ani.setEndValue(QtCore.QPoint(0, 0))  # pyright: ignore[reportAttributeAccessIssue]
        self._to_hide_pos_ani.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)  # pyright: ignore[reportAttributeAccessIssue]

        self._opacity_eff = QtWidgets.QGraphicsOpacityEffect()  # pyright: ignore[reportAttributeAccessIssue]
        self._opacity_ani = QtCore.QPropertyAnimation()  # pyright: ignore[reportAttributeAccessIssue]
        self._opacity_ani.setDuration(400)  # pyright: ignore[reportAttributeAccessIssue]
        self._opacity_ani.setEasingCurve(QtCore.QEasingCurve.Type.InCubic)  # pyright: ignore[reportAttributeAccessIssue]
        self._opacity_ani.setPropertyName(b"opacity")  # pyright: ignore[reportAttributeAccessIssue]
        self._opacity_ani.setStartValue(0.0)  # pyright: ignore[reportAttributeAccessIssue]
        self._opacity_ani.setEndValue(1.0)  # pyright: ignore[reportAttributeAccessIssue]
        self._opacity_ani.setTargetObject(self._opacity_eff)  # pyright: ignore[reportAttributeAccessIssue]
        self._opacity_ani.finished.connect(self._disable_opacity)  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
        self.currentChanged.connect(self._play_anim)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

    def _play_anim(self: T, index: int):
        current_widget = self.widget(index)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
        if self._previous_index < index:  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            self._to_show_pos_ani.setStartValue(QtCore.QPoint(self.width(), 0))  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            self._to_show_pos_ani.setTargetObject(current_widget)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            self._to_show_pos_ani.start()  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        else:
            self._to_hide_pos_ani.setStartValue(QtCore.QPoint(-self.width(), 0))  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            self._to_hide_pos_ani.setTargetObject(current_widget)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            self._to_hide_pos_ani.start()  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        current_widget.setGraphicsEffect(self._opacity_eff)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        current_widget.graphicsEffect().setEnabled(True)  # pyright: ignore[reportUnknownMemberType]
        self._opacity_ani.start()  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        self._previous_index = index  # pyright: ignore[reportAttributeAccessIssue]

    def _disable_opacity(self: T):
        self.currentWidget().graphicsEffect().setEnabled(False)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

    cls.__init__ = _new_init
    cls._play_anim = _play_anim  # pyright: ignore[reportAttributeAccessIssue]
    cls._disable_opacity = _disable_opacity  # pyright: ignore[reportAttributeAccessIssue]
    return cls
