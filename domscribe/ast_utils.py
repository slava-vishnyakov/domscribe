from typing import List, Callable, Union, Optional
from .markdown_types import SemanticMarkdownAST

def find_in_ast(markdown_element: Union[SemanticMarkdownAST, List[SemanticMarkdownAST]], 
                checker: Callable[[SemanticMarkdownAST], bool]) -> Optional[SemanticMarkdownAST]:
    def loop_check(elements: List[SemanticMarkdownAST]) -> Optional[SemanticMarkdownAST]:
        for element in elements:
            found = find_in_ast(element, checker)
            if found:
                return found
        return None

    if isinstance(markdown_element, list):
        return loop_check(markdown_element)
    else:
        if checker(markdown_element):
            return markdown_element
        
        if markdown_element['type'] == 'link':
            return loop_check(markdown_element['content'])
        elif markdown_element['type'] == 'list':
            return loop_check([item for item in markdown_element['items'] for content in item['content']])
        elif markdown_element['type'] == 'table':
            return loop_check([content for row in markdown_element['rows'] 
                               for cell in row['cells'] 
                               for content in (cell['content'] if isinstance(cell['content'], list) else [])])
        elif markdown_element['type'] in ['blockquote', 'semanticHtml']:
            return loop_check(markdown_element['content'])
        
        return None

def find_all_in_ast(markdown_element: Union[SemanticMarkdownAST, List[SemanticMarkdownAST]], 
                    checker: Callable[[SemanticMarkdownAST], bool]) -> List[SemanticMarkdownAST]:
    def loop_check(elements: List[SemanticMarkdownAST]) -> List[SemanticMarkdownAST]:
        out = []
        for element in elements:
            found = find_all_in_ast(element, checker)
            out.extend(found)
        return out

    if isinstance(markdown_element, list):
        return loop_check(markdown_element)
    else:
        if checker(markdown_element):
            return [markdown_element]
        
        if markdown_element['type'] == 'link':
            return loop_check(markdown_element['content'])
        elif markdown_element['type'] == 'list':
            return loop_check([item for item in markdown_element['items'] for content in item['content']])
        elif markdown_element['type'] == 'table':
            return loop_check([content for row in markdown_element['rows'] 
                               for cell in row['cells'] 
                               for content in (cell['content'] if isinstance(cell['content'], list) else [])])
        elif markdown_element['type'] in ['blockquote', 'semanticHtml']:
            return loop_check(markdown_element['content'])
        
        return []

def get_main_content(markdown_str: str) -> str:
    if '<-main->' in markdown_str:
        start = markdown_str.index('<-main->') + len('<-main->')
        end = markdown_str.index('</-main->')
        return markdown_str[start:end].strip()
    else:
        sections_to_remove = ['<-nav->', '<-footer->', '<-header->', '<-aside->']
        for section in sections_to_remove:
            start = markdown_str.find(section)
            if start != -1:
                end = markdown_str.find(f'</-{section[2:-2]}>', start)
                if end != -1:
                    markdown_str = markdown_str[:start] + markdown_str[end + len(f'</-{section[2:-2]}>'):]
        return markdown_str.strip()
