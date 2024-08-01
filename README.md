# Domscribe: Semantic Markdown Converter

[![Python Tests](https://github.com/slava-vishnyakov/domscribe/actions/workflows/python-tests.yml/badge.svg)](https://github.com/slava-vishnyakov/domscribe/actions/workflows/python-tests.yml)

> **Warning**: This is an alpha version of Domscribe. Some tests are still failing, and the API may change in future releases. Use with caution in production environments.

This Python library is a semi-automated port of [dom-to-semantic-markdown](https://github.com/romansky/dom-to-semantic-markdown). It converts HTML to semantic Markdown, preserving the structure and meaning of the original content.

## Installation

```
pip install domscribe
```

## Usage

```python
from domscribe import html_to_markdown

html = "<h1>Hello, World!</h1><p>This is a <strong>test</strong>.</p>"
markdown = html_to_markdown(html)
print(markdown)
```

For more advanced usage, you can pass options to customize the conversion:

```python
options = {
    'extract_main_content': True,
    'keep_html': ['div', 'span'],
    'refify_urls': True
}
markdown = html_to_markdown(html, options)
```

## Why Domscribe?

Domscribe aims to solve several problems associated with traditional HTML-to-Markdown converters:

1. **Semantic preservation**: Most converters lose important semantic information during conversion. Domscribe maintains the semantic structure of the original HTML.

2. **Handling complex structures**: Traditional converters often struggle with nested lists, tables, and other complex HTML structures. Domscribe handles these with ease.

3. **Customizability**: Domscribe offers various options to customize the conversion process according to your needs.

4. **Main content extraction**: It can automatically identify and extract the main content of a web page, ignoring navigation, footers, and other peripheral content.

5. **LLM-friendly output**: The generated Markdown is optimized for further processing by Language Models (LLMs), including special annotations for table columns.

### Customizable Conversion Options

Domscribe offers several options to customize the conversion process:

- `extract_main_content`: Automatically identify and extract the main content of a web page.
- `keep_html`: Preserve specified HTML tags in the Markdown output.
- `refify_urls`: Convert URLs to reference-style links for improved readability.
- `include_meta_data`: Include metadata from the HTML head in the Markdown output.
- `debug`: Enable debug logging for troubleshooting.

For example, to extract the main content and preserve the `div` and `span` tags, you can use the following options:

```python
options = {
    'extract_main_content': True,
    'keep_html': ['div', 'span']
}
converted_html = html_to_markdown(html, options)
```

### URL Refactoring

The `refify_urls` option allows you to convert inline URLs to reference-style links, improving the readability of the generated Markdown. This feature is particularly useful for documents with many links or long URLs.

For example:

```markdown
Check out [this link][1] and [another link][2].

Here's [a repeated link][1].

[1]: https://www.example.com
[2]: https://www.anotherexample.com
```

### Semantic Content Extraction

Domscribe can automatically detect and extract the main content of a web page. This feature helps in focusing on the most relevant part of the HTML document, ignoring navigation, footers, and other peripheral content. To use this feature, set the `extract_main_content` option to `True`:

```python
options = {'extract_main_content': True}
markdown = html_to_markdown(html, options)
```

The library uses various heuristics to identify the main content, including:
- Checking for `<main>` tags
- Analyzing element attributes like 'id' and 'class'
- Evaluating the density of text and other content

### Preserving Semantic HTML

Domscribe can preserve certain HTML tags that carry semantic meaning, even in Markdown output. This is useful for maintaining the structure and semantics of the original content. To enable this feature, use the `keep_html` option:

```python
options = {'keep_html': ['div', 'span']}
markdown = html_to_markdown(html, options)
```

### Table Column Identifiers

When converting tables, Domscribe adds special comments to help identify columns:

```markdown
| Header 1 <!-- colId: 1 --> | Header 2 <!-- colId: 2 --> |
| --- | --- |
| Row 1, Cell 1 <!-- colId: 1 --> | Row 1, Cell 2 <!-- colId: 2 --> |
```

These `<!-- colId: n -->` comments are designed to assist Language Models (LLMs) in understanding the structure of the table, making it easier to process and manipulate table data programmatically.

## License

This project is licensed under the MIT License.
