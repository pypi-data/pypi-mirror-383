# tagish

A generic SGML tag-based serializer that uses tags to encode nodes. It shares the xml syntax for tags and attributes but forgoes the xml specifics as namespaces, cdata, and so on.  No tag nor attribute names carry special meaning.

```json
{ "title": "tagish", "section": {"title": "Introduction", "p":"A generic SGML tag-based format."}
```

As tagish:

```xml
<document>  
    <title>tagish</title>
    <section>
        <title>Introduction</title>
        <p>A generic SGML tag-based format.</p>
    </section>
</document>

```

Produces well formed nodes and is parsable by regular xml parsers. The api mirrors json's `dump` and `load` including indenting support.

## Controlling Tag Output: Names, Attributes and Sequences

A strict transformation rule, where simple types become attributes whereas complex ones tags generate documents with no tag contents, not the kind of documents we'd expect.
Tagish includes some common sense rules for these: where to get  tag's  content, when to use an attribute as a tag name and how to name items in a sequences. While (hopefully) useful, these can be configured.

### Basic Transformation Rules

By default, tagish follows these principles:

- Simple types (strings, numbers, booleans) become XML attributes
- Complex types (objects, arrays) become child elements
- All elements use generic tag names based on JSON keys

Additional rules can be configured through TransformRules, namely:

- Tag contents comes from the first attributes name present as  defined in tag_contents (default value, text and content)
- Tag names will be generated from attributes names as defined in `tag_names_from_attrs`.
- Sequence items' tag names are the sequence attribute name in naive singular form, that is a final 's' if present is removed. For more finer-grained control  you can customize this by defining `irregular_plurals`, `non_plural_words` or the direct maping by `sequence_items_names`.  See the [the transform rules](./tagish/rules.py) for the full details.

For example, the dict:

```python
data = {
    "books": ["To Kill a Mocking Bird", "If traveler on a Winter's Night a Traveler" ],
    "button": {
        "text": "click me" ,
        "class": "active"
    }
}
```

Serializes to

```xml
<document>
    <book>To Kill a Mocking Bird</book>
    <book>If a Traveler on a Winters Night</book>
    <button class="active">click me</button>
</document>
```

## The Cli

Tagish includes a cli:

```bash

# outputs the tagish encoded path, for json, toml and yaml files.
$ tagish <path> 
#  Outputs tagish to other formats
$ tagish <path> --format (json|toml)
```

## Install

tagish is available on Pypi and can be installed as one would so hope:

```bash
pipx install tagish
pip install tagish
```

## Project

It's MIT Licensed, and [contributions](https://github.com/arthur-debert/tagish) are welcome.
