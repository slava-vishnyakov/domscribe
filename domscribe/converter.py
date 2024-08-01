import inspect
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from .html_to_markdown_ast import html_to_markdown_ast
from .markdown_ast_to_string import markdown_ast_to_string
from .dom_utils import find_main_content, wrap_main_content
from .url_utils import refify_urls
from .ast_utils import find_in_ast, find_all_in_ast
from .markdown_types import ConversionOptions, SemanticMarkdownAST

def html_to_markdown(html: str, options: Optional[ConversionOptions] = None) -> str:
    """
    Converts an HTML string to Markdown.
    
    :param html: The HTML string to convert.
    :param options: Conversion options.
    :return: The converted Markdown string.
    """
    def debug_log(message: str):
        if options and options.get('debug'):
            print(f'{inspect.stack()[1][1]}:{inspect.stack()[1][2]}: {message}')

    soup = BeautifulSoup(html, 'html.parser')
    element = soup.body or soup

    if options and options.get('extract_main_content'):
        element = find_main_content(soup)
        if options.get('include_meta_data') and soup.head and not element.find('head'):
            # Re-attach the head for meta-data extraction
            new_soup = BeautifulSoup(f"<html>{soup.head.prettify()}{element.prettify()}</html>", 'html.parser')
            element = new_soup.html

    return convert_element_to_markdown(element, options).strip() + '\n'

def convert_element_to_markdown(element: BeautifulSoup, options: Optional[ConversionOptions] = None) -> str:
    """
    Converts an HTML Element to Markdown.
    
    :param element: The BeautifulSoup element to convert.
    :param options: Conversion options.
    :return: The converted Markdown string.
    """
    ast = html_to_markdown_ast(element, options)

    if options and options.get('refify_urls'):
        ast = refify_urls(ast)

    return markdown_ast_to_string(ast, options)

def find_in_markdown_ast(ast: SemanticMarkdownAST, predicate: callable) -> Optional[SemanticMarkdownAST]:
    """
    Finds a node in the Markdown AST that matches the given predicate.
    
    :param ast: The Markdown AST to search.
    :param predicate: A function that returns True for the desired node.
    :return: The first matching node, or None if not found.
    """
    return find_in_ast(ast, predicate)

def find_all_in_markdown_ast(ast: SemanticMarkdownAST, predicate: callable) -> List[SemanticMarkdownAST]:
    """
    Finds all nodes in the Markdown AST that match the given predicate.
    
    :param ast: The Markdown AST to search.
    :param predicate: A function that returns True for the desired nodes.
    :return: A list of all matching nodes.
    """
    return find_all_in_ast(ast, predicate)
