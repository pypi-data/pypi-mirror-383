class BaseComponent:
    def __init__(self,
                 id: str | None = None,
                 classes: str | None = None,
                 children: list[object] | None = None):
        self.id = id
        self.classes = classes if(classes) else ""
        if(not isinstance(children, list)):
            if(children is None):
                children = []
            else:
                children = [ children ]
        self.children = children

    def _merge_render(self, *rendered_elements) -> str:
        return "".join(*rendered_elements)

    def render(self) -> str: # normally to be overriden
        #rendered_children = self._merge_render(child if(isinstance(child, str)) else child.render() for child in self.children if(child is not None))
        rendered_children = self._merge_render(child.render() for child in self.children if(child is not None))
        return rendered_children
    
    def _copy_objects(self):
        # aber wofür? idc
        pass