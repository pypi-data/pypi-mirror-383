from flask_composed_views.components import Header1, Link, Div, Span, Paragraph

def test_header1():
    header = Header1(text='this is the text')
    assert(header.render() == '<h1>this is the text</h1>')
    par = Paragraph(text='some par')
    assert(par.render().replace('\n', '') == '<p>some par</p>')

def test_attributes():
    par0_text = 'content 000'
    par1_text = 'content 1'
    par0 = Paragraph(text=par0_text)
    par1 = Paragraph(text=par1_text)
    div = Div(children=[par0, par1], classes='test-class', id='test-id')
    div_text = div.render()
    div_text = div_text.replace('\n', '')
    assert(div_text == f'<div id="test-id" class="test-class"><p>{par0_text}</p><p>{par1_text}</p></div>')

def test_no_text_arg():
    link = Link(text='the link', href='to.nowhere.com')
    span = Span(children=[link,], classes='my-span-class, another-class')
    assert(span.render() == '<span class="my-span-class, another-class"><a href="to.nowhere.com">the link</a></span>')

