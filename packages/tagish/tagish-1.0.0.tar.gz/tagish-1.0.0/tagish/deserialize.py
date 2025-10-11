"""
Deserialization functions for tagish - converting tagish format back to Python objects.

Contains functions for converting XML elements to Python objects with optional
reverse transformation rules for symmetric serialization/deserialization.
"""

import xml.etree.ElementTree as ET
from typing import Any, Union

from .rules import (
    TransformRules,
    create_reverse_transformed_dict,
    detect_list_from_xml_structure,
    should_apply_reverse_transformations,
)


def convert_text_to_python_type(text: str) -> Any:
    """Convert text content to appropriate Python type."""
    if not text:
        return ""

    # Try to infer type from text content
    if text.lower() in ("true", "false"):
        return text.lower() == "true"
    elif text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
        return int(text)
    elif "." in text:
        try:
            return float(text)
        except ValueError:
            return text
    else:
        return text


def handle_leaf_node(
    elem: ET.Element, rules: Union[TransformRules, None] = None
) -> Any:
    """Handle leaf nodes (no children) - return None or converted text."""
    # Check if reverse transformations should be applied
    if rules and should_apply_reverse_transformations(
        elem.tag, elem.attrib, elem.text, rules
    ):
        # Create a dictionary with reverse transformations
        return create_reverse_transformed_dict(elem.tag, elem.attrib, elem.text, rules)

    # Standard behavior: if element has no children and no text, return None
    if not elem.text:
        return None

    # Convert text content to appropriate Python type
    return convert_text_to_python_type(elem.text or "")


def is_list_structure(
    child_tags: list[str],
    children: list = None,
    rules: Union[TransformRules, None] = None,
    parent_tag: str = None,
) -> bool:
    """Determine if children represent a list structure."""
    # Enhanced detection with transformation rules
    if rules and children is not None:
        return detect_list_from_xml_structure(child_tags, children, rules, parent_tag)

    # Standard detection: if all children have the same tag name AND there are multiple children, it's likely a list
    return len(set(child_tags)) == 1 and len(child_tags) > 1


def handle_list_node(
    elem: ET.Element, rules: Union[TransformRules, None] = None
) -> list[Any]:
    """Handle nodes that represent lists (repeated child tags)."""
    return [from_taghish(child, rules) for child in elem]


def handle_dict_node(
    elem: ET.Element, rules: Union[TransformRules, None] = None
) -> dict[str, Any]:
    """Handle nodes that represent dictionaries (varied child tags)."""
    result = {}

    # If this element has text content AND children, and we have transformation rules,
    # we might need to preserve the text content as an attribute
    if elem.text and elem.text.strip() and len(elem) > 0 and rules:
        # Check if this looks like a transformed element (either by normal detection or tag name pattern)
        looks_transformed = should_apply_reverse_transformations(
            elem.tag, elem.attrib, elem.text, rules
        ) or (
            "-" in elem.tag
        )  # kebab-case tag names suggest transformation

        if looks_transformed:
            # Add tag name as label attribute if configured
            if rules.tag_name_from_attrs:
                tag_attr_name = rules.tag_name_from_attrs[0]
                result[tag_attr_name] = elem.tag

            # Add text content as content attribute if configured
            if rules.tag_content_from_attrs:
                content_attr_name = rules.tag_content_from_attrs[0]
                result[content_attr_name] = elem.text.strip()

    # Process child elements
    for child in elem:
        key = child.tag
        value = from_taghish(child, rules)

        # Handle multiple children with same tag (becomes a list)
        if key in result:
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(value)
        else:
            result[key] = value

    return result


def handle_complex_node(
    elem: ET.Element, rules: Union[TransformRules, None] = None
) -> Any:
    """Handle nodes with children - determine if list or dict structure."""
    children = list(elem)
    child_tags = [child.tag for child in children]

    if is_list_structure(child_tags, children, rules, elem.tag):
        return handle_list_node(elem, rules)
    else:
        return handle_dict_node(elem, rules)


def from_taghish(elem: ET.Element, rules: Union[TransformRules, None] = None) -> Any:
    """Main orchestrator: Convert XML Element back to Python object."""
    # If element has no children, handle as leaf node
    if len(elem) == 0:
        return handle_leaf_node(elem, rules)

    # If element has children, handle as complex node
    return handle_complex_node(elem, rules)
