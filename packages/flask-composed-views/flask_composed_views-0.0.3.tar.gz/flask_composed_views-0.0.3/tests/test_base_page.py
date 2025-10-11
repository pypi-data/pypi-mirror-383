from flask_composed_views.components import Header1
from flask_composed_views.utils import BasePage

def test_default_base_page():
    page = BasePage(title='test <b>title</b>',
                    stylesheets=[ 'url.to.stylesheet1.css', 'style/other.css', ],
                    children=[ Header1('some header'), ])
    rendered_page = page.render()
    assert(isinstance(rendered_page, str))
    rendered_page = rendered_page.replace('\n', '')
    assert(rendered_page == '<html><head><meta charset="UTF-8"><title>test &lt;b&gt;title&lt;/b&gt;</title><link rel="stylesheet" href="url.to.stylesheet1.css"><link rel="stylesheet" href="style/other.css"></head><body><h1>some header</h1></body></html>')