from .base_tag import BaseTag
from ..core.plain_text_utils import prepend_text
class Div(BaseTag):
    def __init__(self,
                 text: str | None = None,
                 children: list | None = None,
                 id: str | None = None,
                 classes: str | None = None):
        super().__init__('div', id=id, classes=classes, children=prepend_text(text, children))
    
