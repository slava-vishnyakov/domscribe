import inspect
from typing import List, Dict, Any
from .markdown_types import SemanticMarkdownAST, ConversionOptions

def markdown_ast_to_string(nodes: List[SemanticMarkdownAST], options: ConversionOptions = None, indent_level: int = 0) -> str:
    markdown_string = ''

    def debug_log(message: str):
        if options and options.get('debug'):
            print(f'{inspect.stack()[1][1]}:{inspect.stack()[1][2]}: {message}')

    for node in nodes:
        indent = ' ' * (indent_level * 2)
        debug_log(f"Processing node of type: {node['type']}")

        node_rendering_override = options.get('override_node_renderer') if options else None
        if node_rendering_override:
            debug_log("Using node rendering override")
            override_result = node_rendering_override(node, options, indent_level)
            if override_result:
                markdown_string += override_result
                continue

        if node['type'] in ['text', 'bold', 'italic', 'strikethrough', 'link', 'reflink']:
            debug_log(f"Processing inline element: {node['type']}")
            is_last_whitespace = markdown_string[-1].isspace() if markdown_string else False
            is_starts_with_whitespace = node['content'][0].isspace() if node['content'] and isinstance(node['content'], str) else False

            if not is_last_whitespace and node['content'] != '.' and not is_starts_with_whitespace:
                markdown_string += ' '

            if node['type'] == 'text':
                markdown_string += f"{indent}{node['content']}"
            elif node['type'] == 'bold':
                markdown_string += f"**{node['content']}**"
            elif node['type'] == 'italic':
                markdown_string += f"*{node['content']}*"
            elif node['type'] == 'strikethrough':
                markdown_string += f"~~{node['content']}~~"
            elif node['type'] == 'link':
                if len(node['content']) == 1 and node['content'][0]['type'] == 'text':
                    markdown_string += f"[{node['content'][0]['content']}]({node['href']})"
                else:
                    link_content = markdown_ast_to_string(node['content'], options, indent_level + 1)
                    markdown_string += f"<a href=\"{node['href']}\">{link_content}</a>"
            elif node['type'] == 'reflink':
                link_content = markdown_ast_to_string(node['content'], options, indent_level + 1).strip()
                markdown_string += f"[{link_content}]{node['href']}\n"

        elif node['type'] == 'heading':
            debug_log(f"Processing heading level {node['level']}")
            if not markdown_string.endswith('\n'):
                markdown_string += '\n'
            markdown_string += f"{'#' * node['level']} {node['content']}\n\n"

        elif node['type'] == 'image':
            debug_log("Processing image")
            if node['alt'].strip() or node['src'].strip():
                markdown_string += f"![{node['alt']}]({node['src']})"

        elif node['type'] == 'list':
            debug_log(f"Processing {'ordered' if node['ordered'] else 'unordered'} list")
            for i, item in enumerate(node['items']):
                list_item_prefix = f"{i + 1}. " if node['ordered'] else "- "
                item_content = item['content']

                # Check if the item contains a nested list
                nested_list = next((subitem for subitem in item_content if subitem['type'] == 'list'), None)

                if nested_list:
                    debug_log("Processing list item with nested list")
                    # Handle item with nested list
                    non_list_content = [subitem for subitem in item_content if subitem['type'] != 'list']
                    markdown_string += f"{indent}{list_item_prefix}{markdown_ast_to_string(non_list_content, options, indent_level).strip()}\n"
                    markdown_string += markdown_ast_to_string([nested_list], options, indent_level + 1)
                else:
                    debug_log("Processing regular list item")
                    # Handle regular item
                    item_markdown = markdown_ast_to_string(item_content, options, indent_level + 1)
                    markdown_string += f"{indent}{list_item_prefix}{item_markdown.strip()}\n"

            # Add an extra newline after processing all list items
            if indent_level == 0:
                markdown_string += '\n'
        
        elif node['type'] == 'table':
            debug_log("Processing table")
            if not node['rows']:
                debug_log("Skipping empty table")
                continue  # Skip empty tables
            debug_log(f"Processing table with {len(node['rows'])} rows: {node['rows']}")
            for row_index, row in enumerate(node['rows']):
                markdown_string += '|'
                for cell in row['cells']:
                    cell_content = markdown_ast_to_string(cell['content'], options, indent_level + 1).strip() if isinstance(cell['content'], list) else str(cell['content'])
                    if cell.get('colId'):
                        cell_content += f" <!-- colId: {cell['colId']} -->"
                    markdown_string += f" {cell_content} |"
                markdown_string += '\n'
                if row_index == 0:
                    debug_log("Adding table header separator")
                    markdown_string += '|' + '|'.join([' --- ' for _ in row['cells']]) + '|\n'
            markdown_string += '\n'
        
        elif node['type'] == 'code':
            debug_log(f"Processing {'inline' if node['inline'] else 'block'} code")
            if node['inline']:
                if not markdown_string[-1].isspace():
                    markdown_string += ' '
                markdown_string += f"`{node['content']}`"
            else:
                markdown_string += f"\n```{node.get('language', '')}\n{node['content']}\n```\n\n"
        
        elif node['type'] == 'blockquote':
            debug_log("Processing blockquote")
            markdown_string += f"> {markdown_ast_to_string(node['content'], options).strip()}\n\n"
        
        elif node['type'] == 'semanticHtml':
            debug_log(f"Processing semantic HTML: {node['htmlType']}")
            if node['htmlType'] == 'article':
                markdown_string += '\n\n' + markdown_ast_to_string(node['content'], options)
            elif node['htmlType'] in ['summary', 'time', 'aside', 'nav', 'figcaption', 'main', 'mark', 'header', 'footer', 'details', 'figure']:
                markdown_string += f"\n\n<-{node['htmlType']}->\n{markdown_ast_to_string(node['content'], options)}\n\n</-{node['htmlType']}->\n"
            elif node['htmlType'] == 'section':
                markdown_string += '---\n\n'
                markdown_string += markdown_ast_to_string(node['content'], options)
                markdown_string += '\n\n---\n\n'
        
        elif node['type'] == 'custom':
            debug_log("Processing custom node")
            custom_node_rendering = options.get('render_custom_node')
            if custom_node_rendering:
                markdown_string += custom_node_rendering(node, options, indent_level)
        
        elif node['type'] == 'preservedHtml':
            debug_log(f"Processing preserved HTML: {node['tag']}")
            content = markdown_ast_to_string(node['content'], options, indent_level)
            # Ensure proper spacing before the opening tag
            if markdown_string and not markdown_string.endswith(' '):
                markdown_string += ' '
            attrs = node['attrs'] if node['attrs'] else ''
            markdown_string += f"<{node['tag']}{' ' + attrs if attrs else ''}>{content.strip()}</{node['tag']}>"
            # Ensure proper spacing after the closing tag
            if not content.endswith(' '):
                markdown_string += ' '
    
    return markdown_string
