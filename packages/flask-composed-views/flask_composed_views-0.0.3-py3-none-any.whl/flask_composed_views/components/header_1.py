from .base_tag import BaseTag
from .plain_text import PlainText
from ..core.plain_text_utils import prepend_text
class Header1(BaseTag):
    def __init__(self,
                 text: str | None = None,
                 children: list | None = None,
                 id: str | None = None,
                 classes: str | None = None):
        children = prepend_text(text)
        super().__init__('h1', id=id, classes=classes, children=children)
    
