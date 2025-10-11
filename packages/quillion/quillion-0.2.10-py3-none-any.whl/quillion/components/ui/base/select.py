from typing import Optional, Callable
from ..element import Element


class Select(Element):
    def __init__(self, *children, class_name: Optional[str] = None, **kwargs):
        super().__init__("select", *children, class_name=class_name, **kwargs)


def select(*children, **kwargs):
    return Select(*children, **kwargs)
