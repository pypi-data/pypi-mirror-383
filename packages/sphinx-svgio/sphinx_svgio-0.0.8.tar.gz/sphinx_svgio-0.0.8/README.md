# Sphinx SVG.IO Package

This is a simple extension for embedding draw.io diagramms into sphinx docs.

## Usage

### Diagram Embedding

In conf.py:
```python
extensions = ["sphinx_svgio"]
```

In rst:

```rst
.. svgio:: path/to/scheme.drawio.svg
    :name: scheme_1
    :page: 2
    :caption: some caption
```

With `page` option you can choose an initial page of complex draw.io scheme.
By default it is page `1`


### Diagram Descriptions

It is possible to add a description for every diagramm page.
Content of relevant `svgio-page::` will be moved right under diagram for convenience:

```rst
.. svgio:: path/to/scheme.drawio.svg
    :name: scheme_1

.. svgio-list::
    :name: scheme_1
    :expand:

    .. svgio-page::
        :page: 1

        page 1 description

    .. svgio-page::
        :page: 2

        page 2 description


    .. svgio-page::
        :page: 3

        page 3 description
```

`:name:` option must be the same as in the target `svgio::` directive

Presence of `:expand:` option keeps all pages in a list visible.

### Diagram Page references

Page in a list can be referenced using for example:

```rst
:pageref:`Link title <scheme_1:2>`
```

