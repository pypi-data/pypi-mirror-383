from ..components import BaseComponent, PlainText

class BasePage(BaseComponent):
    def __init__(self,
                 title: str = "",
                 stylesheets: list[str] | None = None,
                 children=None):
        """Don't use user input in the definition of stylesheets: not safe!!!
        """
        self.title = PlainText(title)
        self.stylesheets = stylesheets
        if(children is None):
            children = []
        elif(not isinstance(children, list)):
            children = [ children, ]
        super().__init__(children=children)

    def _build_header(self) -> str:
        header = '<head>\n<meta charset="UTF-8">\n'
        header += f'<title>{self.title.render()}</title>'
        if(self.stylesheets):
            for stylesheet_url in self.stylesheets:
                header += f'<link rel="stylesheet" href="{stylesheet_url}">' # TODO: make this safe?
        header += '</head>'
        return header
    
    def render(self) -> str:
        page_content = [
            f'<html>{self._build_header()}<body>', 
            super().render(),
            '</body></html>',
        ]
        return "".join(page_content)