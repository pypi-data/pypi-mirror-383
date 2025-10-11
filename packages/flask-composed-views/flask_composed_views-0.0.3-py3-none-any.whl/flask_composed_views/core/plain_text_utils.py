from ..components.plain_text import PlainText

def prepend_text(text: str | None = None,
                 children: list | None = None) -> list | None:
    if(text is None):
        return children
    text = PlainText(text)
    if(children is not None):
        children.insert(0, text)
    else:
        children = [ text, ]
    return children