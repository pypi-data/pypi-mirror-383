""" "
In order to output nice and common sense tags from general objecs, a few rules
are needed. This class encapsulates all the heuristics and overrides for
converting Python objects to XML/tagish format.
Usage Example:

    # Use defaults
    rules = TransformRules()
    result = tagish.dumps(data, transform_rules=rules)

    # Customize for specific domain
    rules = TransformRules(
        tag_content_from_attrs=["content", "body", "description"],
        sequence_items_names={"endpoints": "url", "configs": "setting"},
        xml_name_validation=False  # Allow any tag names
    )
    result = tagish.dumps(data, transform_rules=rules)
"""

from dataclasses import dataclass, field


@dataclass
class TransformRules:
    """
    Configuration for JSON to XML transformation rules.

    This class  holds the configuration for controling how tagish tags are created, and does not include the logic itself, which is in the serializer and deserializer modules.
    """

    tag_content_from_attrs: list[str] = field(
        default_factory=lambda: ["value", "text", "content"]
    )
    """
    list of attribute names that should become tag content instead of attributes.
    
    When processing a dictionary, the first attribute name found in this list
    (with a simple value) will be used as the tag's text content, and that
    attribute will be consumed (not appear as an XML attribute).
    
    Examples:
        ["value", "text", "content"] (default)
        {"name": "button", "text": "Click me"} → <tag name="button">Click me</tag>
        
    Set to empty list [] to disable content extraction - all simple values
    become attributes.
    
    Rationale: XML naturally supports both attributes and text content, but
    JSON only has key-value pairs. This heuristic identifies which JSON
    values represent semantic "content" vs "metadata".
    """

    tag_name_from_attrs: list[str] = field(default_factory=lambda: ["label"])
    """
    list of attribute names that should become the XML tag name.
    
    When processing a dictionary, the first attribute name found in this list
    will be used as the tag name instead of a generic name, and that attribute
    will be consumed (not appear as an XML attribute).
    
    Examples:
        ["label"] (default)
        {"label": "xml-viewer", "version": "1.0"} → <xml-viewer version="1.0"/>
        
    Set to empty list [] to disable semantic tag naming.
    
    Rationale: Sometimes JSON data contains semantic type information that
    should be reflected in the XML structure rather than buried in attributes.
    Common in plugin systems, component definitions, etc.
    """

    irregular_plurals: dict[str, str] = field(
        default_factory=lambda: {
            "children": "child",
            "people": "person",
            "mice": "mouse",
            "feet": "foot",
            "teeth": "tooth",
            "geese": "goose",
            "men": "man",
            "women": "woman",
        }
    )
    """
    dictionary mapping irregular plural forms to their singular equivalents.
    
    Used when processing sequences (lists) to determine the XML tag name for
    individual items. English has many irregular plurals that don't follow
    the simple "remove s" rule.
    
    Examples:
        {"children": "child"} → children: [...] becomes <children><child>...</child></children>
        
    Users can extend this dictionary for domain-specific plurals or other languages.
    
    Rationale: Natural language pluralization is irregular and context-dependent.
    A dictionary provides exact control while covering the most common cases.
    """

    non_plural_words: set[str] = field(
        default_factory=lambda: {
            "process",
            "address",
            "success",
            "class",
            "pass",
            "access",
            "express",
            "stress",
            "press",
            "dress",
            "mass",
            "glass",
            "grass",
            "cross",
            "loss",
            "boss",
            "gross",
            "discuss",
        }
    )
    """
    Set of words ending in 's' that are NOT plural forms.
    
    Prevents the sequence processing rule from incorrectly removing the 's'
    from words that happen to end in 's' but aren't plural.
    
    Examples:
        "process" stays "process", not "proces"
        "address" stays "address", not "addres"
        
    Users can extend this set for domain-specific terminology.
    
    Rationale: Many English words end in 's' but aren't plural. Without this
    safeguard, the simple "remove s" rule would create invalid tag names.
    """

    sequence_items_names: dict[str, str] = field(default_factory=dict)
    """
    Direct mapping from sequence names to their item tag names.
    
    Provides explicit control over sequence item naming, overriding all
    other pluralization rules. This is the highest-priority override.
    
    Examples:
        {"files": "path", "data": "record", "items": "element"}
        files: [...] → <files><path>...</path></files>
        
    Use this for domain-specific naming or when the automatic rules don't
    produce the desired result.
    
    Rationale: Sometimes the natural relationship between container and item
    names isn't captured by linguistic pluralization rules. Direct mapping
    provides ultimate control.
    """

    min_word_length_for_s_removal: int = 2
    """
    Minimum word length before attempting to remove trailing 's' for sequences.
    
    Prevents the sequence rule from creating empty or single-character tag
    names, which would be invalid XML.
    
    Examples:
        With min_length=2: "s" → stays "s", "is" → becomes "i"
        With min_length=3: both "s" and "is" stay unchanged
        
    Rationale: Very short words ending in 's' are likely not plural forms,
    and removing 's' from them creates invalid or meaningless tag names.
    """

    xml_name_space_replacement: str = "-"
    """
    Character to replace spaces with in XML tag names.
    
    When an attribute value is used as a tag name, spaces must be replaced
    since XML tag names cannot contain spaces.
    
    Examples:
        "my component" → "my-component"
        "user input" → "user-input"
        
    Rationale: Hyphens are the most common and readable way to represent
    multi-word identifiers in XML. Users can change to "_" or other
    characters if preferred.
    """

    xml_name_validation: bool = True
    """
    Whether to validate and potentially reject invalid XML tag names.
    
    When True, tag names derived from attributes are validated for XML
    compliance. Invalid names (containing reserved characters) will raise
    an error rather than producing malformed XML.
    
    Reserved characters: ! @ # $ % & * ( ) + = { } [ ] | ` ; ' " < > / ?
    
    When False, tag names are used as-is (may produce invalid XML).
    
    Rationale: Producing valid XML is usually more important than preserving
    exact tag names. However, some users may want to handle validation
    themselves or have different requirements.

    See: 
        tests/data/transform.json
        tests/data/transform.xml

        For a full pair of input/output examples demonstrating all rules.
    
    """


def reverse_sequence_item_name(item_name: str, rules: TransformRules) -> str:
    """
    Reverse transform: determine the sequence name from an item name.

    This is the inverse of get_sequence_item_name from serialize module.
    Attempts to find the plural/collection form of an item name.

    Args:
        item_name: The tag name of individual items
        rules: TransformRules configuration object

    Returns:
        The sequence/collection name that would generate this item name

    Examples:
        "item" → "items" (standard pluralization)
        "child" → "children" (irregular plural)
        "process" → "process" (non-plural word, no change)
    """
    # Priority 1: Check if this item name maps to any custom sequence mapping
    for sequence_name, mapped_item_name in rules.sequence_items_names.items():
        if mapped_item_name == item_name:
            return sequence_name

    # Priority 2: Check if this is a known irregular plural singular form
    for plural_name, singular_name in rules.irregular_plurals.items():
        if singular_name == item_name:
            return plural_name

    # Priority 3: Check if this word is in non-plural set (return as-is)
    if item_name in rules.non_plural_words:
        return item_name

    # Priority 4: Standard pluralization (add 's' if long enough)
    if len(item_name) >= rules.min_word_length_for_s_removal:
        return item_name + "s"

    # Priority 5: Fallback (return as-is)
    return item_name


def should_apply_reverse_transformations(
    elem_tag: str, elem_attrib: dict, elem_text: str, rules: TransformRules
) -> bool:
    """
    Determine if reverse transformation rules should be applied to this XML element.

    Reverse transformations should be applied if:
    1. The element has both text content AND attributes (clear transformation sign)
    2. The element has only attributes but tag name looks like a transformed label

    We avoid transforming elements that just have attributes without text, unless
    the tag name suggests it was transformed from a label/name attribute.

    Args:
        elem_tag: XML tag name
        elem_attrib: XML attributes dictionary
        elem_text: XML text content (or None)
        rules: TransformRules configuration object

    Returns:
        True if reverse transformations should be applied
    """
    # If transformation rules are disabled, never apply reverse transformations
    if not rules.tag_name_from_attrs and not rules.tag_content_from_attrs:
        return False

    has_attributes = bool(elem_attrib)
    has_text_content = bool(elem_text and elem_text.strip())

    # Strong signals for transformation
    # 1. Both text and attributes (definitely from transformation)
    if has_text_content and has_attributes:
        return True

    # 2. Text content with semantic tag name (like <btn>text</btn>)
    if has_text_content and not has_attributes:
        # Check if tag name suggests transformation
        tag_looks_transformed = (
            "-" in elem_tag  # kebab-case suggests transformation
            or (
                elem_tag != elem_tag.lower() and any(c.isupper() for c in elem_tag[1:])
            )  # camelCase
        )

        # More conservative list - include natural XML names that shouldn't be transformed
        natural_names = {
            "root",
            "item",
            "element",
            "data",
            "value",
            "entry",
            "node",
            "name",
            "title",
            "text",
            "content",
            "description",
            "id",
            "type",
            "age",
            "active",
            "enabled",
            "disabled",
            "visible",
            "hidden",
            "status",
            "state",
            "version",
            "size",
            "count",
            "total",
        }
        tag_looks_semantic = elem_tag not in natural_names and len(elem_tag) > 1

        if tag_looks_transformed or tag_looks_semantic:
            return True

    # Weaker signal: only attributes, but tag name might be a transformed label
    # Apply if tag name contains transformation markers OR if it's not a generic container name
    if has_attributes and not has_text_content:
        # Check if tag name contains characters that suggest it was a transformed label
        # Focus on clear transformation markers: hyphens and camelCase (but not just Capitalized)
        tag_looks_transformed = (
            "-" in elem_tag  # kebab-case suggests transformation
            or (
                elem_tag != elem_tag.lower() and any(c.isupper() for c in elem_tag[1:])
            )  # camelCase
        )

        # Also check if tag name is not a generic container name
        # Generic names like "root", "item", "element" suggest no transformation
        # More conservative list - include natural XML names that shouldn't be transformed
        natural_names = {
            "root",
            "item",
            "element",
            "data",
            "value",
            "entry",
            "node",
            "name",
            "title",
            "text",
            "content",
            "description",
            "id",
            "type",
            "age",
            "active",
            "enabled",
            "disabled",
            "visible",
            "hidden",
            "status",
            "state",
            "version",
            "size",
            "count",
            "total",
        }
        tag_looks_semantic = elem_tag not in natural_names and len(elem_tag) > 1

        return tag_looks_transformed or tag_looks_semantic

    # Even weaker signal: no attributes and no text, but tag name suggests transformation
    # This handles cases like <btn/> from {"label": "btn"}
    if not has_attributes and not has_text_content:
        # Same logic as above for tag name evaluation
        tag_looks_transformed = (
            "-" in elem_tag  # kebab-case suggests transformation
            or (
                elem_tag != elem_tag.lower() and any(c.isupper() for c in elem_tag[1:])
            )  # camelCase
        )

        # More conservative list - include natural XML names that shouldn't be transformed
        natural_names = {
            "root",
            "item",
            "element",
            "data",
            "value",
            "entry",
            "node",
            "name",
            "title",
            "text",
            "content",
            "description",
            "id",
            "type",
            "age",
            "active",
            "enabled",
            "disabled",
            "visible",
            "hidden",
            "status",
            "state",
            "version",
            "size",
            "count",
            "total",
        }
        tag_looks_semantic = elem_tag not in natural_names and len(elem_tag) > 1

        return tag_looks_transformed or tag_looks_semantic

    return False


def create_reverse_transformed_dict(
    elem_tag: str, elem_attrib: dict, elem_text: str, rules: TransformRules
) -> dict:
    """
    Create a dictionary with reverse transformations applied.

    Converts XML structure back to original dictionary format:
    - Tag name becomes a label/name attribute (prefers "label" over "name")
    - Text content becomes a content attribute (prefers "content" over others)
    - XML attributes become dictionary items

    Args:
        elem_tag: XML tag name
        elem_attrib: XML attributes dictionary
        elem_text: XML text content (or None)
        rules: TransformRules configuration object

    Returns:
        Dictionary with reverse transformations applied
    """
    result = {}

    # Add tag name as label attribute if we have tag name attributes configured
    if rules.tag_name_from_attrs and elem_tag != "root":
        # Use first configured tag name attribute (typically "label")
        tag_attr_name = rules.tag_name_from_attrs[0]
        result[tag_attr_name] = elem_tag

    # Add text content as content attribute if we have content and content attributes configured
    if elem_text and elem_text.strip() and rules.tag_content_from_attrs:
        # Use the first configured content attribute (maintains priority order)
        content_attr_name = rules.tag_content_from_attrs[0]
        result[content_attr_name] = elem_text.strip()

    # Add all XML attributes as dictionary items (convert string values back to appropriate types)
    from .deserialize import convert_text_to_python_type

    for attr_key, attr_value in elem_attrib.items():
        result[attr_key] = convert_text_to_python_type(attr_value)

    return result


def detect_list_from_xml_structure(
    child_tags: list[str], children: list, rules: TransformRules, parent_tag: str = None
) -> bool:
    """
    Enhanced list detection that considers transformation rules.

    In addition to the standard list detection (all same tags), also considers:
    1. If tags look like pluralized item names that could have been transformed
    2. If multiple children have both attributes and text (likely transformed list items)

    Args:
        child_tags: List of child tag names
        children: List of actual XML elements
        rules: TransformRules configuration object

    Returns:
        True if this should be treated as a list structure
    """
    # Standard detection: all same tags with multiple children
    if len(set(child_tags)) == 1 and len(child_tags) > 1:
        return True

    # Enhanced detection 1: check if all tags could be item names for the same sequence
    if len(child_tags) > 1:
        # Try to reverse-transform all tag names to see if they point to the same sequence
        potential_sequences = set()
        for tag in child_tags:
            sequence_name = reverse_sequence_item_name(tag, rules)
            potential_sequences.add(sequence_name)

        # If all tags reverse-transform to the same sequence name, it's likely a list
        if len(potential_sequences) == 1:
            return True

    # Enhanced detection 2: if multiple children have transformation signatures, treat as list
    # This handles cases where list items had different labels but similar structure
    if len(children) > 1:
        transformed_children = 0
        for child in children:
            if should_apply_reverse_transformations(
                child.tag, child.attrib, child.text, rules
            ):
                transformed_children += 1

        # If most children look like they were transformed, treat as list
        if transformed_children >= len(children) * 0.5:  # At least 50% look transformed
            return True

    # Enhanced detection 3: Single child where parent-child suggests collection-item relationship
    if len(child_tags) == 1 and parent_tag:
        child_tag = child_tags[0]
        # Check if child tag could be the singular form of the parent tag
        expected_parent = reverse_sequence_item_name(child_tag, rules)
        if expected_parent == parent_tag:
            return True

    return False
