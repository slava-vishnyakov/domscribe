from typing import List, Dict, Union, Optional, Any
from typing_extensions import TypedDict

class BoldNode(TypedDict):
    type: str
    content: str

class ItalicNode(TypedDict):
    type: str
    content: str

class StrikethroughNode(TypedDict):
    type: str
    content: str

class HeadingNode(TypedDict):
    type: str
    level: int
    content: str

class LinkNode(TypedDict):
    type: str
    href: str
    content: List['SemanticMarkdownAST']

class ImageNode(TypedDict):
    type: str
    src: str
    alt: str

class ListItemNode(TypedDict):
    type: str
    content: List['SemanticMarkdownAST']

class ListNode(TypedDict):
    type: str
    ordered: bool
    items: List[ListItemNode]

class TableCellNode(TypedDict):
    type: str
    content: Union[str, List['SemanticMarkdownAST']]
    colId: Optional[str]

class TableRowNode(TypedDict):
    type: str
    cells: List[TableCellNode]

class TableNode(TypedDict):
    type: str
    rows: List[TableRowNode]
    colIds: Optional[List[str]]

class CodeNode(TypedDict):
    type: str
    language: Optional[str]
    content: str
    inline: bool

class BlockquoteNode(TypedDict):
    type: str
    content: List['SemanticMarkdownAST']

class CustomNode(TypedDict):
    type: str
    content: Any

class SemanticHtmlNode(TypedDict):
    type: str
    htmlType: str
    content: List['SemanticMarkdownAST']

class VideoNode(TypedDict):
    type: str
    src: str
    poster: Optional[str]
    controls: Optional[bool]

class TextNode(TypedDict):
    type: str
    content: str

class MetaDataNode(TypedDict):
    type: str
    content: Dict[str, Dict[str, str]]

SemanticMarkdownAST = Union[
    TextNode,
    BoldNode,
    ItalicNode,
    StrikethroughNode,
    HeadingNode,
    LinkNode,
    ImageNode,
    VideoNode,
    ListNode,
    TableNode,
    CodeNode,
    BlockquoteNode,
    SemanticHtmlNode,
    CustomNode,
    MetaDataNode
]

class ConversionOptions(TypedDict, total=False):
    website_domain: Optional[str]
    extract_main_content: bool
    refify_urls: bool
    url_map: Dict[str, str]
    debug: bool
    enable_table_column_tracking: bool
    override_element_processing: Optional[callable]
    process_unhandled_element: Optional[callable]
    override_node_renderer: Optional[callable]
    render_custom_node: Optional[callable]
    include_meta_data: Optional[Union[str, bool]]
