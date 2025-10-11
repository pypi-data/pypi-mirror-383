"""
tagish - A generic SGML/XML-like serialization format

Mirrors the json module API with functions to serialize and deserialize
Python objects to/from tagish format.
"""

# Import the public API functions from api module
from .api import (
    detect_format,
    detect_format_from_content,
    detect_format_from_extension,
    dump,
    dumps,
    dumps_to_format,
    load,
    load_file,
    loads,
    loads_from_format,
    output_to_stdout,
)

# Import the TransformRules class for customization
from .rules import TransformRules

# Import internal functions that are used by tests and CLI
from .serialize import append_child, create_element

# Define what's available when using "from tagish import *"
__all__ = [
    "loads",
    "dumps",
    "load",
    "dump",
    "TransformRules",
    "create_element",
    "append_child",
    "detect_format",
    "detect_format_from_extension",
    "detect_format_from_content",
    "loads_from_format",
    "dumps_to_format",
    "load_file",
    "output_to_stdout",
]
