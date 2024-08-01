from typing import Dict, List, Union
from .markdown_types import SemanticMarkdownAST

media_suffixes = ["jpeg", "jpg", "png", "gif", "bmp", "tiff", "tif", "svg",
                  "webp", "ico", "avi", "mov", "mp4", "mkv", "flv", "wmv", "webm", "mpeg",
                  "mpg", "mp3", "wav", "aac", "ogg", "flac", "m4a", "pdf", "doc", "docx",
                  "ppt", "pptx", "xls", "xlsx", "txt", "css", "js", "xml", "json",
                  "html", "htm"]

def add_ref_prefix(prefix: str, prefixes_to_refs: Dict[str, str]) -> str:
    if prefix not in prefixes_to_refs:
        prefixes_to_refs[prefix] = f"ref{len(prefixes_to_refs)}"
    return prefixes_to_refs[prefix]

def process_url(url: str, prefixes_to_refs: Dict[str, str]) -> str:
    if not url.startswith('http'):
        return url
    
    media_suffix = url.split('.')[-1]
    if media_suffix in media_suffixes:
        parts = url.split('/')
        prefix = '/'.join(parts[:-1])
        ref_prefix = add_ref_prefix(prefix, prefixes_to_refs)
        return f"{ref_prefix}://{parts[-1]}"
    elif len(url.split('/')) > 4:
        return add_ref_prefix(url, prefixes_to_refs)
    else:
        return url

from typing import Union, List, Dict
from .markdown_types import SemanticMarkdownAST, LinkNode

def refify_urls(markdown_element: Union[SemanticMarkdownAST, List[SemanticMarkdownAST]]) -> Union[SemanticMarkdownAST, List[SemanticMarkdownAST]]:
    url_map: Dict[str, int] = {}
    url_counter = 1

    def process_element(element: Union[SemanticMarkdownAST, List[SemanticMarkdownAST]]) -> Union[SemanticMarkdownAST, List[SemanticMarkdownAST]]:
        nonlocal url_counter

        if isinstance(element, list):
            return [process_element(item) for item in element]

        if isinstance(element, dict):
            if element.get('type') == 'link':
                url = element['href']
                if url not in url_map:
                    url_map[url] = url_counter
                    url_counter += 1
                ref_number = url_map[url]
                
                # Modify the original link content to use the reference style
                if element['content'] and isinstance(element['content'], list) and element['content'][0]['type'] == 'text':
                    element['content'][0]['content'] = element['content'][0]['content'].strip()
                else:
                    element['content'] = [{
                        'type': 'text',
                        'content': ''.join(item.get('content', '') for item in element.get('content', [])).strip()
                    }]
                element['href'] = f'[{ref_number}]'  # Use reference number as href
                element['type'] = 'reflink'  # Change the type to 'reflink'
                return element

            if 'content' in element:
                element['content'] = process_element(element['content'])

        return element

    processed_ast = process_element(markdown_element)

    # Add reference links at the end
    if isinstance(processed_ast, list):
        processed_ast.append({'type': 'newline'})
        reference_links = []
        for url, ref_number in url_map.items():
            reference_links.append(f"[{ref_number}]: {url}")
        processed_ast.append({
            'type': 'text',
            'content': '\n'.join(reference_links)
        })
        processed_ast.append({'type': 'newline'})

    return processed_ast
