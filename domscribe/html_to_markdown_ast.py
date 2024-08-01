import inspect
from typing import List, Dict, Any
from bs4 import BeautifulSoup, Tag
from .markdown_types import SemanticMarkdownAST, ConversionOptions

def html_to_markdown_ast(element: Tag, options: ConversionOptions = None, indent_level: int = 0) -> List[SemanticMarkdownAST]:
    result: List[SemanticMarkdownAST] = []
    
    def debug_log(message: str):
        if options and options.get('debug'):
            print(f'{inspect.stack()[1][1]}:{inspect.stack()[1][2]}: {message}')

    for child in element.children:
        if isinstance(child, Tag):
            overridden_element_processing = options.get('override_element_processing') if options else None
            if overridden_element_processing:
                overridden_result = overridden_element_processing(child, options, indent_level)
                if overridden_result:
                    debug_log(f"Element Processing Overridden: '{child.name}'")
                    result.extend(overridden_result)
                    continue

            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(child.name[1])
                content = child.get_text().strip()
                if content:
                    debug_log(f"Heading {level}: '{content}'")
                    result.append({'type': 'heading', 'level': level, 'content': content})
            elif child.name == 'p':
                debug_log("Paragraph")
                result.extend(html_to_markdown_ast(child, options, indent_level))
                result.append({'type': 'text', 'content': '\n\n'})
            elif child.name == 'a':
                debug_log(f"Link: '{child.get('href')}' with text '{child.get_text()}'")
                href = child.get('href', '')
                if options and options.get('website_domain') and href.startswith(options['website_domain']):
                    href = href[len(options['website_domain']):]
                result.append({
                    'type': 'link',
                    'href': href,  # Keep the trailing slash
                    'content': html_to_markdown_ast(child, options, indent_level + 1)
                })
            elif child.name == 'img':
                debug_log(f"Image: src='{child.get('src')}', alt='{child.get('alt')}'")
                src = child.get('src', '')
                if options and options.get('website_domain') and src.startswith(options['website_domain']):
                    src = src[len(options['website_domain']):]
                result.append({
                    'type': 'image',
                    'src': src,
                    'alt': child.get('alt', '')
                })
            elif child.name in ['ul', 'ol']:
                debug_log(f"{'Unordered' if child.name == 'ul' else 'Ordered'} List")
                result.append({
                    'type': 'list',
                    'ordered': child.name == 'ol',
                    'items': [{'type': 'listItem', 'content': html_to_markdown_ast(li, options, indent_level + 1)} for li in child.find_all('li', recursive=False)]
                })
            elif child.name == 'br':
                debug_log("Line Break")
                result.append({'type': 'text', 'content': '\n'})
            elif child.name == 'table':
                debug_log("Table")
                rows = []
                # Find all rows in the table, including those in thead and tbody
                all_rows = child.find_all('tr', recursive=True)
                for row in all_rows:
                    cells = []
                    for col_index, cell in enumerate(row.find_all(['th', 'td'], recursive=False)):
                        cell_type = 'tableHeaderCell' if cell.name == 'th' else 'tableCell'
                        cells.append({
                            'type': cell_type,
                            'content': html_to_markdown_ast(cell, options, indent_level + 1),
                            'colId': str(col_index + 1)  # Add column number as colId
                        })
                    rows.append({'type': 'tableRow', 'cells': cells})
                result.append({'type': 'table', 'rows': rows})
            else:
                # Handle other elements
                content = child.get_text().strip()
                if child.name in ['strong', 'b']:
                    if content:
                        debug_log(f"Bold: '{content}'")
                        result.append({'type': 'bold', 'content': content})
                elif child.name in ['em', 'i']:
                    if content:
                        debug_log(f"Italic: '{content}'")
                        result.append({'type': 'italic', 'content': content})
                elif child.name in ['s', 'strike']:
                    if content:
                        debug_log(f"Strikethrough: '{content}'")
                        result.append({'type': 'strikethrough', 'content': content})
                elif child.name == 'code':
                    if content:
                        is_code_block = child.parent and child.parent.name == 'pre'
                        debug_log(f"{'Code Block' if is_code_block else 'Inline Code'}: '{content}'")
                        language = child.get('class', [])
                        language = next((cls.replace('language-', '') for cls in language if cls.startswith('language-')), '')
                        result.append({
                            'type': 'code',
                            'content': child.get_text().strip(),
                            'language': language,
                            'inline': not is_code_block
                        })
                elif child.name == 'blockquote':
                    debug_log("Blockquote")
                    result.append({
                        'type': 'blockquote',
                        'content': html_to_markdown_ast(child, options, indent_level)
                    })
                elif child.name in ['article', 'aside', 'details', 'figcaption', 'figure', 'footer', 'header', 'main', 'mark', 'nav', 'section', 'summary', 'time']:
                    debug_log(f"Semantic HTML Element: '{child.name}'")
                    result.append({
                        'type': 'semanticHtml',
                        'htmlType': child.name,
                        'content': html_to_markdown_ast(child, options, indent_level)
                    })
                else:
                    keep_html = options.get('keep_html', []) if options else []
                    if child.name in keep_html:
                        debug_log(f"Preserving HTML Element: '{child.name}'")
                        attrs = []
                        for k, v in child.attrs.items():
                            if k == 'class':
                                class_value = ' '.join(v) if isinstance(v, list) else v
                                attrs.append(f'class="{class_value}"')
                            elif v:
                                attrs.append(f'{k}="{v}"')
                        attrs = ' '.join(attrs)
                        result.append({
                            'type': 'preservedHtml',
                            'tag': child.name,
                            'attrs': attrs,
                            'content': html_to_markdown_ast(child, options, indent_level + 1)
                        })
                    else:
                        unhandled_element_processing = options.get('process_unhandled_element') if options else None
                        if unhandled_element_processing:
                            debug_log(f"Processing Unhandled Element: '{child.name}'")
                            result.extend(unhandled_element_processing(child, options, indent_level))
                        else:
                            debug_log(f"Generic HTMLElement: '{child.name}'")
                            result.extend(html_to_markdown_ast(child, options, indent_level + 1))
        elif child.string and child.string.strip():
            result.append({'type': 'text', 'content': child.string.strip()})

    return result
