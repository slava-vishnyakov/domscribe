from typing import List
from bs4 import BeautifulSoup, Tag

def find_main_content(document: BeautifulSoup) -> Tag:
    """
    Attempts to find the main content of a web page.
    """
    main_element = document.find('main')
    if main_element:
        return main_element
    
    return detect_main_content(document.body or document)

def detect_main_content(root_element: Tag) -> Tag:
    candidates = []
    min_score = 20
    collect_candidates(root_element, candidates, min_score)
    
    if not candidates:
        return root_element
    
    candidates.sort(key=lambda x: calculate_score(x), reverse=True)
    
    best_independent_candidate = candidates[0]
    for candidate in candidates[1:]:
        if not any(other_candidate.find(candidate) for other_candidate in candidates if other_candidate != candidate):
            if calculate_score(candidate) > calculate_score(best_independent_candidate):
                best_independent_candidate = candidate
    
    return best_independent_candidate

def collect_candidates(element: Tag, candidates: List[Tag], min_score: int):
    score = calculate_score(element)
    if score >= min_score:
        candidates.append(element)
    
    for child in element.children:
        if isinstance(child, Tag):
            collect_candidates(child, candidates, min_score)

def calculate_score(element: Tag) -> int:
    score = 0
    
    high_impact_attributes = ['article', 'content', 'main-container', 'main', 'main-content']
    for attr in high_impact_attributes:
        if attr in element.get('class', []) or attr in element.get('id', ''):
            score += 10
    
    high_impact_tags = ['article', 'main', 'section']
    if element.name in high_impact_tags:
        score += 5
    
    paragraph_count = len(element.find_all('p'))
    score += min(paragraph_count, 5)
    
    text_content_length = len(element.get_text(strip=True))
    if text_content_length > 200:
        score += min(text_content_length // 200, 5)
    
    link_density = calculate_link_density(element)
    if link_density < 0.3:
        score += 5
    
    if element.has_attr('data-main') or element.has_attr('data-content'):
        score += 10
    
    if element.get('role') == 'main':
        score += 10
    
    return score

def calculate_link_density(element: Tag) -> float:
    link_length = sum(len(link.get_text(strip=True)) for link in element.find_all('a'))
    text_length = len(element.get_text(strip=True)) or 1  # Avoid division by zero
    return link_length / text_length

def is_element_visible(element: Tag) -> bool:
    style = element.get('style', '').lower()
    return 'display:none' not in style and 'visibility:hidden' not in style and 'opacity:0' not in style

def get_visible_text(element: Tag) -> str:
    if not is_element_visible(element):
        return ''
    
    text = ''
    for child in element.children:
        if isinstance(child, str):
            text += child
        elif isinstance(child, Tag):
            text += get_visible_text(child)
    
    return text.strip()

def wrap_main_content(main_content_element: Tag, document: BeautifulSoup):
    if main_content_element.name.lower() != 'main':
        main_element = document.new_tag('main')
        main_content_element.wrap(main_element)
        main_element['id'] = 'detected-main-content'
