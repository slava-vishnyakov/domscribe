import pytest
from bs4 import BeautifulSoup
from domscribe import html_to_markdown, convert_element_to_markdown
from domscribe.markdown_types import ConversionOptions


def test_convert_simple_paragraph():
    html = "<p>This is a simple paragraph.</p>"
    expected = "This is a simple paragraph."
    assert html_to_markdown(html).strip() == expected

def test_convert_headings():
    html = "<h1>Heading 1</h1><h2>Heading 2</h2><h3>Heading 3</h3>"
    expected = "# Heading 1\n\n## Heading 2\n\n### Heading 3"
    assert html_to_markdown(html).strip() == expected

def test_convert_unordered_list():
    html = "<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>"
    expected = "- Item 1\n- Item 2\n- Item 3"
    assert html_to_markdown(html).strip() == expected

def test_convert_ordered_list():
    html = "<ol><li>First</li><li>Second</li><li>Third</li></ol>"
    expected = "1. First\n2. Second\n3. Third"
    assert html_to_markdown(html).strip() == expected

def test_convert_links():
    html = '<a href="https://example.com">Example</a>'
    expected = '[Example](https://example.com)'
    assert html_to_markdown(html).strip() == expected

def test_convert_links_without_trailing_slash():
    html = '<a href="https://example.com/page">Example</a>'
    expected = '[Example](https://example.com/page)'
    assert html_to_markdown(html).strip() == expected

def test_convert_images():
    html = '<img src="image.jpg" alt="An image">'
    expected = '![An image](image.jpg)'
    assert html_to_markdown(html).strip() == expected

def test_convert_bold_and_italic():
    html = '<p><strong>Bold</strong> and <em>italic</em> text</p>'
    expected = '**Bold** and *italic* text'
    assert html_to_markdown(html).strip() == expected

def test_convert_blockquotes():
    html = '<blockquote><p>This is a quote.</p></blockquote>'
    expected = '> This is a quote.'
    assert html_to_markdown(html).strip() == expected

def test_convert_code_blocks():
    html = '<pre><code>function example() {\n  return true;\n}</code></pre>'
    expected = '```\nfunction example() {\n  return true;\n}\n```'
    assert html_to_markdown(html).strip() == expected

def test_convert_code_blocks_with_language():
    html = '<pre><code class="language-javascript">function example() {\n  return true;\n}</code></pre>'
    expected = '```javascript\nfunction example() {\n  return true;\n}\n```'
    assert html_to_markdown(html).strip() == expected

def test_convert_inline_code():
    html = '<p>Use the <code>example()</code> function.</p>'
    expected = 'Use the `example()` function.'
    assert html_to_markdown(html).strip() == expected

def test_convert_tables():
    html = """
    <table>
      <thead>
        <tr><th>Header 1</th><th>Header 2</th></tr>
      </thead>
      <tbody>
        <tr><td>Row 1, Cell 1</td><td>Row 1, Cell 2</td></tr>
        <tr><td>Row 2, Cell 1</td><td>Row 2, Cell 2</td></tr>
      </tbody>
    </table>
    """
    expected = (
        "| Header 1 <!-- colId: 1 --> | Header 2 <!-- colId: 2 --> |\n"
        "| --- | --- |\n"
        "| Row 1, Cell 1 <!-- colId: 1 --> | Row 1, Cell 2 <!-- colId: 2 --> |\n"
        "| Row 2, Cell 1 <!-- colId: 1 --> | Row 2, Cell 2 <!-- colId: 2 --> |"
    )
    assert html_to_markdown(html).strip() == expected

def test_convert_nested_structures():
    html = """
    <div>
      <h1>Main Title</h1>
      <p>Here's a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
      <ul>
        <li>Item 1</li>
        <li>Item 2
          <ol>
            <li>Subitem 2.1</li>
            <li>Subitem 2.2</li>
          </ol>
        </li>
        <li>Item 3</li>
      </ul>
    </div>
    """
    expected = (
        "# Main Title\n\n"
        "Here's a paragraph with **bold** and *italic* text.\n\n"
        "- Item 1\n"
        "- Item 2\n"
        "  1. Subitem 2.1\n"
        "  2. Subitem 2.2\n"
        "- Item 3"
        "\n"
    )
    assert html_to_markdown(html) == expected

def test_convert_element_to_markdown():
    html = "<p>This is a <strong>test</strong>.</p>"
    soup = BeautifulSoup(html, 'html.parser')
    element = soup.p
    expected = "This is a **test**."
    assert convert_element_to_markdown(element).strip() == expected

def test_convert_code_blocks():
    html = """
    <pre><code>def hello_world():
    print("Hello, World!")
</code></pre>
    """
    expected = "```\ndef hello_world():\n    print(\"Hello, World!\")\n```\n"
    assert html_to_markdown(html) == expected

def test_convert_blockquotes():
    html = "<blockquote><p>This is a quote.</p><p>With multiple paragraphs.</p></blockquote>"
    expected = "> This is a quote.\n> \n> With multiple paragraphs.\n"
    assert html_to_markdown(html) == expected

def test_convert_links():
    html = '<p>Check out <a href="https://example.com">this link</a>.</p>'
    expected = "Check out [this link](https://example.com).\n"
    assert html_to_markdown(html) == expected

def test_convert_images():
    html = '<img src="image.jpg" alt="An example image">'
    expected = "![An example image](image.jpg)\n"
    assert html_to_markdown(html) == expected

def test_preserve_html_tags():
    html = '<p>This is a <span class="highlight">highlighted</span> text.</p>'
    options = {'keep_html': ['span']}
    expected = 'This is a <span class="highlight">highlighted</span> text.\n'
    assert html_to_markdown(html, options) == expected

def test_refify_urls_basic():
    html = '<a href="https://example.com">Link 1</a>'
    options = {'refify_urls': True}
    expected = '[Link 1][1]\n\n[1]: https://example.com\n'
    assert html_to_markdown(html, options) == expected

def test_refify_urls():
    html = '<p><a href="https://example.com">Link 1</a> and <a href="https://example.org">Link 2</a></p>'
    options = {'refify_urls': True}
    expected = "[Link 1][1] and [Link 2][2]\n\n[1]: https://example.com\n[2]: https://example.org\n"
    assert html_to_markdown(html, options) == expected

def test_extract_main_content():
    html = """
    <html>
        <body>
            <header>Header content</header>
            <main>
                <h1>Main Content</h1>
                <p>This is the main content.</p>
            </main>
            <footer>Footer content</footer>
        </body>
    </html>
    """
    options = {'extract_main_content': True}
    expected = "# Main Content\n\nThis is the main content.\n"
    assert html_to_markdown(html, options) == expected

def test_refify_urls_with_repeated_links():
    html = '''
    <p><a href="https://example.com">Link 1</a> and <a href="https://example.org">Link 2</a></p>
    <p>Here's <a href="https://example.com">Link 1</a> again.</p>
    '''
    options = {'refify_urls': True}
    expected = '''
[Link 1][1] and [Link 2][2]

Here's [Link 1][1] again.

[1]: https://example.com
[2]: https://example.org
'''.strip() + '\n'
    assert html_to_markdown(html, options) == expected

def test_refify_urls_with_different_text_same_url():
    html = '''
    <p><a href="https://example.com">First link</a> and <a href="https://example.com">Second link</a></p>
    '''
    options = {'refify_urls': True}
    expected = '''
[First link][1] and [Second link][1]

[1]: https://example.com
'''.strip() + '\n'
    assert html_to_markdown(html, options) == expected
