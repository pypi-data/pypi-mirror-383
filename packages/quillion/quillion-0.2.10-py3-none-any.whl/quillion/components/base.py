import asyncio
import inspect
from typing import Optional, Dict, Any, Callable, Tuple, List
from .state import State
from .ui.element import Element


class CSS:
    def __init__(self, files: List[str]):
        self.files = files

    def to_dict(self, app) -> Dict[str, Any]:
        return {
            "tag": "link",
            "attributes": {
                "rel": "stylesheet",
                "href": self.files[0] if self.files else "",
            },
            "children": [],
        }


class Component(Element):
    def __init__(self, tag: str = "div", **kwargs):
        super().__init__(tag=tag, **kwargs)
        self.props = kwargs
        self._hook_state: Dict[int, Any] = {}
        self._hook_index: int = 0
        self._rerender_callback: Optional[Callable[[], Any]] = None

    def _reset_hooks(self):
        self._hook_index = 0

    def _request_rerender(self):
        if self._rerender_callback:
            callback_result = self._rerender_callback()
            if not inspect.iscoroutine(callback_result):
                return
            asyncio.create_task(callback_result)

    def use_state(self, initial_value: Any) -> Tuple[Any, Callable[[Any], None]]:
        current_index = self._hook_index
        self._hook_index += 1
        if current_index not in self._hook_state:
            if inspect.isclass(initial_value) and issubclass(initial_value, State):
                state_instance = initial_value.get_instance()
                state_instance._set_rerender_callback(self._request_rerender)
                self._hook_state[current_index] = state_instance
            else:
                self._hook_state[current_index] = initial_value
        state_value = self._hook_state[current_index]
        if isinstance(state_value, State):
            return state_value
        else:

            def setter(new_value: Any):
                if callable(new_value):
                    self._hook_state[current_index] = new_value(
                        self._hook_state[current_index]
                    )
                else:
                    self._hook_state[current_index] = new_value
                self._request_rerender()

            return state_value, setter

    def render_component(self) -> Element:
        raise NotImplementedError

    def to_dict(self, app) -> Dict[str, Any]:
        self._reset_hooks()
        rendered_element = self.render_component()
        if self.key:
            rendered_element.key = self.key
        if self.css_classes:
            rendered_element.css_classes.extend(self.css_classes)
        if self.inline_style_properties:
            rendered_element.inline_style_properties.update(
                self.inline_style_properties
            )
        return rendered_element.to_dict(app)
