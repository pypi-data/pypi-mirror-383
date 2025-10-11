from typing import List, Iterable
from markdown_it import MarkdownIt
from mdformat.renderer import MDRenderer

from .Logging import get_logger

logger = get_logger(__name__)


def remove_markdown(
    text: str,
    remove_types: Iterable[str] = [
        "heading",
        "emphasis",
        "strong",
        "horizontal_rule",
        "block_quote",
    ],
) -> str:
    """Remove markdown formatting from the text content.

    Args:
        text (str): The text content.
        remove_types (Iterable[str], optional): The type of format to be removed. Defaults to [ "heading", "emphasis", "strong", "horizontal_rule", "block_quote", ].

    Returns:
        str: The text content without markdown formatting.
    """
    markdown_match = {
        "heading": ["heading_open", "heading_close"],
        "emphasis": ["em_open", "em_close"],
        "strong": ["strong_open", "strong_close"],
        "horizontal_rule": ["hr"],
        "block_quote": ["blockquote_open", "blockquote_close"],
    }
    for remove_type in remove_types:
        if remove_type not in markdown_match:
            raise ValueError(
                f"Invalid remove type: {remove_type}, must be one of {list(markdown_match.keys())}"
            )

    try:

        def traverse_ast_tree(node):
            for remove_type in remove_types:
                if node.type in markdown_match[remove_type]:
                    return None
            new_children = []
            if node.children:
                for child in node.children:
                    new_child = traverse_ast_tree(child)
                    if new_child:
                        new_children.append(new_child)
            node.children = new_children
            return node

        md = MarkdownIt()
        tokens = []
        for token in md.parse(text):
            new_token = traverse_ast_tree(token)
            if new_token:
                tokens.append(new_token)

        renderer = MDRenderer()
        output_markdown = renderer.render(tokens, {}, {})
        return output_markdown
    except Exception as e:
        logger.error(f"Error removing markdown: {e}")
        return text


def split_ordered_list(
    text: str,
    remove_markdown_types=[
        "heading",
        "emphasis",
        "strong",
        "horizontal_rule",
        "block_quote",
    ],
    **kwargs,
) -> List[str]:
    text = remove_markdown(text, remove_markdown_types, **kwargs)

    try:
        order_list_count = 0
        order_list_open_idx = -1
        order_list_close_idx = -1

        md = MarkdownIt()
        tokens = md.parse(text)
        for idx, token in enumerate(tokens):
            if token.type == "ordered_list_open":
                order_list_count += 1
                if order_list_open_idx == -1:
                    order_list_open_idx = idx
            if token.type == "ordered_list_close":
                order_list_count -= 1
                if order_list_count == 0:
                    order_list_close_idx = idx
                    break

        tokens = tokens[order_list_open_idx : order_list_close_idx + 1]

        res = []
        renderer = MDRenderer()

        list_item_count = 0
        list_item_open_idx = -1
        for idx, token in enumerate(tokens):
            if token.type == "list_item_open":
                list_item_count += 1
                if list_item_open_idx == -1:
                    list_item_open_idx = idx
            if token.type == "list_item_close":
                list_item_count -= 1
                if list_item_count == 0:
                    list_item_close_idx = idx
                    res.append(
                        renderer.render(
                            tokens[list_item_open_idx + 1 : list_item_close_idx], {}, {}
                        )
                    )
                    list_item_open_idx = -1

        return res
    except Exception as e:
        logger.error(f"Error splitting ordered list: {e}")
        return [text]
