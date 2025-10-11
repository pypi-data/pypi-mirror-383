"""
Serialization functions for tagish - converting Python objects to tagish format.

Contains functions for converting Python objects to element dictionaries and then to XML strings.
"""

import html
from typing import Any, Dict, Optional, Union

from .rules import TransformRules


def create_element(
    tag: str, attrib: Optional[Dict[str, str]] = None, text: Optional[str] = None
) -> Dict[str, Any]:
    """Create a tagish element dictionary."""
    return {"tag": tag, "attrib": attrib or {}, "text": text, "children": []}


def append_child(element: Dict[str, Any], child: Dict[str, Any]) -> None:
    """Add a child element to an element."""
    element["children"].append(child)


def get_sequence_item_name(sequence_name: str, rules: TransformRules) -> str:
    """
    Determine the XML tag name for items in a sequence.

    Applies the full hierarchy of rules:
    1. Direct mapping (sequence_items_names)
    2. Irregular plurals dictionary
    3. Non-plural words set (no change)
    4. Standard rule: remove 's' if word length >= min_word_length_for_s_removal
    5. Fallback: use sequence_name unchanged

    Args:
        sequence_name: The name of the sequence/list attribute
        rules: TransformRules configuration object

    Returns:
        The tag name to use for individual items in the sequence

    Examples:
        "files" → "file" (standard rule)
        "children" → "child" (irregular plural)
        "process" → "process" (non-plural word)
        "data" → "entry" (if sequence_items_names = {"data": "entry"})
    """
    # Priority 1: Direct mapping override
    if sequence_name in rules.sequence_items_names:
        return rules.sequence_items_names[sequence_name]

    # Priority 2: Irregular plurals
    if sequence_name in rules.irregular_plurals:
        return rules.irregular_plurals[sequence_name]

    # Priority 3: Non-plural words (no change)
    if sequence_name in rules.non_plural_words:
        return sequence_name

    # Priority 4: Standard rule (remove 's' if long enough)
    if len(
        sequence_name
    ) >= rules.min_word_length_for_s_removal and sequence_name.endswith("s"):
        return sequence_name[:-1]

    # Priority 5: Fallback (no change)
    return sequence_name


def validate_xml_name(name: str, rules: TransformRules) -> str:
    """
    Validate and sanitize a string for use as an XML tag name.

    Applies the configured validation and sanitization rules:
    1. Replace spaces with xml_name_space_replacement
    2. If xml_name_validation is True, check for reserved characters
    3. Raise ValueError if invalid characters found

    Args:
        name: The proposed tag name
        rules: TransformRules configuration object

    Returns:
        The sanitized tag name

    Raises:
        ValueError: If xml_name_validation is True and name contains
                    reserved characters that cannot be sanitized

    Examples:
        "my component" → "my-component"
        "user@domain" → ValueError (if validation enabled)
        "valid-name" → "valid-name" (no change)
    """
    if not name:
        raise ValueError("Tag name cannot be empty")

    # Replace spaces with configured replacement
    sanitized = name.replace(" ", rules.xml_name_space_replacement)

    if rules.xml_name_validation:
        # Check for reserved characters
        reserved_chars = set("!@#$%&*()+={}[]|`;'\"<>/?")
        if any(char in reserved_chars for char in sanitized):
            invalid_chars = [char for char in sanitized if char in reserved_chars]
            raise ValueError(
                f"Invalid XML tag name '{name}': contains reserved characters {invalid_chars}"
            )

    return sanitized


def handle_primitive(obj: Any, tag: str) -> Dict[str, Any]:
    """Handle primitive types: None, bool, int, float, str."""
    elem = create_element(tag)

    if obj is None:
        elem["text"] = ""
    elif isinstance(obj, bool):
        elem["text"] = str(obj).lower()
    elif isinstance(obj, (int, float)):
        elem["text"] = str(obj)
    elif isinstance(obj, str):
        elem["text"] = obj
    else:
        elem["text"] = str(obj)  # fallback for unknown types

    return elem


def handle_list(
    obj: list, tag: str, rules: Union[TransformRules, None]
) -> Dict[str, Any]:
    """Handle list serialization."""
    elem = create_element(tag)

    # Determine item tag using transformation rules
    if rules:
        item_tag = get_sequence_item_name(tag, rules)
    else:
        # Default behavior: use "item" as tag name
        item_tag = "item"
    # Special case: if tag is "root", use "item" as default
    if item_tag == "root":
        item_tag = "item"

    for item in obj:
        if isinstance(item, dict):
            child = handle_dict(item, item_tag, rules)
        else:
            child = to_taghish(item, item_tag, rules)
        append_child(elem, child)

    return elem


def to_taghish(
    obj: Any, tag: str = "root", rules: Union[TransformRules, None] = None
) -> Dict[str, Any]:
    """Main orchestrator: Convert Python object to tagish element dictionary."""
    # Don't create default rules - pass None through to allow no-transformation behavior

    # Dispatch to appropriate handler based on type
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return handle_primitive(obj, tag)
    elif isinstance(obj, list):
        return handle_list(obj, tag, rules)
    elif isinstance(obj, dict):
        return handle_dict(obj, tag, rules)
    else:
        # Fallback for unknown types
        return handle_primitive(obj, tag)


def should_apply_transformations(obj: Dict[str, Any], rules: TransformRules) -> bool:
    """Determine if transformation rules should be applied to this dictionary."""
    has_tag_name_attr = any(attr in obj for attr in rules.tag_name_from_attrs)
    has_content_attr = any(attr in obj for attr in rules.tag_content_from_attrs)

    # Apply transformations if:
    # 1. There's a tag name attribute (explicit intent to transform), OR
    # 2. There's a content attribute AND multiple keys (avoid single-key content-only transformations)
    return has_tag_name_attr or (has_content_attr and len(obj) > 1)


def extract_tag_name(
    obj: Dict[str, Any], rules: TransformRules, default_tag: str
) -> str:
    """Extract tag name from transformation rules."""
    for attr_name in rules.tag_name_from_attrs:
        if attr_name in obj and isinstance(obj[attr_name], str):
            return validate_xml_name(obj[attr_name], rules)
    return default_tag


def extract_text_content(obj: Dict[str, Any], rules: TransformRules) -> Optional[str]:
    """Extract text content from transformation rules."""
    for attr_name in rules.tag_content_from_attrs:
        if attr_name in obj and not isinstance(obj[attr_name], (dict, list)):
            return str(obj[attr_name])
    return None


def partition_dict_items(
    obj: Dict[str, Any], rules: TransformRules
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Partition dictionary items into consumed (by rules) and remaining items."""
    consumed = {}
    remaining = {}

    for key, value in obj.items():
        is_consumed = False

        # Check if this key was used for tag name
        for attr_name in rules.tag_name_from_attrs:
            if key == attr_name and isinstance(value, str):
                consumed[key] = value
                is_consumed = True
                break

        # Check if this key was used for content (only the highest priority one)
        if not is_consumed:
            text_content_attr = None
            for attr_name in rules.tag_content_from_attrs:
                if attr_name in obj and not isinstance(obj[attr_name], (dict, list)):
                    text_content_attr = attr_name
                    break  # First match wins (highest priority)

            if key == text_content_attr:
                consumed[key] = value
                is_consumed = True

        if not is_consumed:
            remaining[key] = value

    return consumed, remaining


def handle_dict_simple(
    obj: Dict[str, Any], tag: str, rules: Union[TransformRules, None]
) -> Dict[str, Any]:
    """Handle dictionary without transformation rules."""
    elem = create_element(tag)
    for key, value in obj.items():
        child = to_taghish(value, key, rules)
        append_child(elem, child)
    return elem


def handle_dict_with_transformations(
    obj: Dict[str, Any], tag: str, rules: TransformRules
) -> Dict[str, Any]:
    """Handle dictionary with transformation rules applied."""
    final_tag = extract_tag_name(obj, rules, tag)
    text_content = extract_text_content(obj, rules)
    consumed, remaining = partition_dict_items(obj, rules)

    elem = create_element(final_tag, text=text_content)

    # Process remaining attributes and child elements
    for key, value in remaining.items():
        if isinstance(value, (dict, list)):
            # Complex values become child elements
            child = to_taghish(value, key, rules)
            append_child(elem, child)
        else:
            # Simple values become attributes when transformations are active
            if value is None:
                elem["attrib"][key] = ""
            elif isinstance(value, bool):
                elem["attrib"][key] = str(value).lower()
            else:
                elem["attrib"][key] = str(value)

    return elem


def handle_dict(
    obj: Dict[str, Any], tag: str, rules: Union[TransformRules, None]
) -> Dict[str, Any]:
    """Handle dictionary serialization with optional transformation rules."""
    if rules and should_apply_transformations(obj, rules):
        return handle_dict_with_transformations(obj, tag, rules)
    else:
        return handle_dict_simple(obj, tag, rules)


def format_attributes(attrib: Dict[str, str]) -> str:
    """Format attributes for XML tag."""
    if not attrib:
        return ""
    return " " + " ".join(f'{k}="{html.escape(v)}"' for k, v in attrib.items())


def format_opening_tag(
    tag: str, attrib: Dict[str, str], current_indent: str = ""
) -> str:
    """Format opening XML tag with attributes."""
    attrib_str = format_attributes(attrib)
    return f"{current_indent}<{tag}{attrib_str}>"


def format_self_closing_tag(
    tag: str, attrib: Dict[str, str], current_indent: str = ""
) -> str:
    """Format self-closing XML tag."""
    attrib_str = format_attributes(attrib)
    return f"{current_indent}<{tag}{attrib_str}/>"


def format_text_element(
    tag: str, attrib: Dict[str, str], text: str, current_indent: str = ""
) -> str:
    """Format text-only XML element."""
    opening = format_opening_tag(tag, attrib, current_indent)
    return f"{opening}{html.escape(text)}</{tag}>"


def format_container_element_compact(elem: Dict[str, Any]) -> str:
    """Format container element in compact mode (single line)."""
    opening = format_opening_tag(elem["tag"], elem["attrib"], "")
    parts = [opening]
    for child in elem["children"]:
        parts.append(element_to_xml(child, "", ""))
    parts.append(f"</{elem['tag']}>")
    return "".join(parts)


def format_container_element_indented(
    elem: Dict[str, Any], indent: str, current_indent: str
) -> str:
    """Format container element with indentation."""
    lines = []
    opening = format_opening_tag(elem["tag"], elem["attrib"], current_indent)
    lines.append(opening)

    # Add text content if present
    if elem["text"] and elem["text"].strip():
        lines.append(f"{current_indent}{indent}{html.escape(elem['text'])}")

    # Add children
    for child in elem["children"]:
        lines.append(element_to_xml(child, indent, current_indent + indent))

    lines.append(f"{current_indent}</{elem['tag']}>")
    return "\n".join(lines)


def element_to_xml(
    elem: Dict[str, Any], indent: str = "", current_indent: str = ""
) -> str:
    """Main orchestrator: Convert element dictionary to XML string."""
    # Handle self-closing tags (only for elements with None text and no children)
    if elem["text"] is None and not elem["children"]:
        return format_self_closing_tag(elem["tag"], elem["attrib"], current_indent)

    # Text-only elements (including empty string text)
    if elem["text"] is not None and not elem["children"]:
        return format_text_element(
            elem["tag"], elem["attrib"], elem["text"], current_indent
        )

    # Elements with children
    if not indent:
        # No indentation - put everything on one line for simple cases
        if elem["children"] and all(
            not child["children"] for child in elem["children"]
        ):
            return format_container_element_compact(elem)

    # Default: format with indentation
    return format_container_element_indented(elem, indent, current_indent)
