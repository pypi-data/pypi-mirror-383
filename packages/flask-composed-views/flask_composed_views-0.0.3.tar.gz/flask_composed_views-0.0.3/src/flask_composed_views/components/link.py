from .base_tag import BaseTag
from ..core.plain_text_utils import prepend_text

class Link(BaseTag):
    def __init__(self,
                 text: str | None = None,
                 children = None,
                 id = None,
                 classes = None,
                 href: str | None = None):
        other_attributes = {}
        if(href):
            other_attributes['href'] = href
        super().__init__('a',
                         id=id,
                         classes=classes,
                         other_attributes=other_attributes,
                         children=prepend_text(text, children),)

