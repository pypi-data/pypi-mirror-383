import functools
from collections.abc import Callable
from typing import Any

from qtpy import QtWidgets

from .types import MixinComputed, MixinData, MixinProps
from .utils import qbytearray_to_str


class MFieldMixin:
    def __init__(self):
        self.computed_dict: dict[str, MixinComputed] = {}
        self.props_dict: dict[str, MixinProps] = {}

    def register_field(
        self,
        name: str,
        getter: Callable[[], Any] | Any = None,
        setter: Callable[[Any], None] | None = None,
        required: bool = False,
    ):
        if callable(getter):
            value = getter()
            self.computed_dict[name] = {
                "value": value,
                "getter": getter,
                "setter": setter,
                "required": required,
                "bind": [],
            }
        else:
            self.props_dict[name] = {"value": getter, "required": required, "bind": []}
        return

    def bind(
        self,
        data_name: str,
        widget: QtWidgets.QWidget,
        qt_property: str,
        index: int | None = None,
        signal: str | None = None,
        callback: Callable[[], Any] | None = None,
    ):
        # data_dict = {
        #     "data_name": data_name,
        #     "widget": widget,
        #     "widget_property": qt_property,
        #     "index": index,
        #     "callback": callback,
        # }
        data_dict = MixinData(
            data_name=data_name,
            widget=widget,
            widget_property=qt_property,
            index=index,
            callback=callback,
        )
        if data_name in self.computed_dict:
            self.computed_dict[data_name]["bind"].append(data_dict)
        else:
            self.props_dict[data_name]["bind"].append(data_dict)
        if signal:  # 用户操作绑定数据
            getattr(widget, signal).connect(
                functools.partial(self._slot_changed_from_user, data_dict)
            )
        self._data_update_ui(data_dict)
        return widget

    def fields(self):
        return self.props_dict.keys() | self.computed_dict.keys()

    def field(self, name: str) -> Any:
        if name in self.props_dict:
            return self.props_dict[name]["value"]
        elif name in self.computed_dict:
            computed = self.computed_dict[name]
            getter = computed["getter"]
            if getter:
                new_value = getter()
                self.computed_dict[name]["value"] = new_value
                return new_value
            return computed["value"]
        else:
            raise KeyError(f'There is no field named "{name}"')

    def set_field(self, name: str, value: Any):
        if name in self.props_dict:
            self.props_dict[name]["value"] = value
            self._slot_prop_changed(name)

        elif name in self.computed_dict:
            self.computed_dict[name]["value"] = value
            self._slot_prop_changed(name)

    def _data_update_ui(self, data_dict: MixinData):
        data_name = data_dict.get("data_name")
        widget = data_dict["widget"]
        index = data_dict["index"]
        widget_property = data_dict["widget_property"]
        callback = data_dict["callback"]
        value = None
        if index is None:
            value = self.field(data_name)
        elif isinstance(self.field(data_name), dict):
            value = self.field(data_name).get(index)
        elif isinstance(self.field(data_name), list):
            value = (
                self.field(data_name)[index]
                if index < len(self.field(data_name))
                else None
            )
        if widget.metaObject().indexOfProperty(
            widget_property
        ) > -1 or widget_property in [
            qbytearray_to_str(b) for b in widget.dynamicPropertyNames()
        ]:
            widget.setProperty(widget_property, value)
        else:
            if hasattr(widget, "set_field"):
                widget.set_field(widget_property, value)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        if callable(callback):
            callback()

    def _slot_prop_changed(self, property_name: str):
        for key, setting_dict in self.props_dict.items():
            if key == property_name:
                for data_dict in setting_dict["bind"]:
                    self._data_update_ui(data_dict)

        for setting_dict in self.computed_dict.values():
            for data_dict in setting_dict["bind"]:
                self._data_update_ui(data_dict)

    def _slot_changed_from_user(self, data_dict: MixinData, ui_value: Any):
        self._ui_update_data(data_dict, ui_value)

    def _ui_update_data(self, data_dict: MixinData, ui_value: Any):
        data_name = data_dict.get("data_name")
        index = data_dict.get("index", None)
        if index is None:
            self.set_field(data_name, ui_value)
        else:
            old_value = self.field(data_name)
            old_value[index] = ui_value
            self.set_field(data_name, old_value)
        if data_name in self.props_dict.keys():
            self._slot_prop_changed(data_name)

    def _is_complete(self):
        for name, data_dict in self.computed_dict.items() | self.props_dict.items():
            if data_dict["required"] and not self.field(name):
                return False
        return True
