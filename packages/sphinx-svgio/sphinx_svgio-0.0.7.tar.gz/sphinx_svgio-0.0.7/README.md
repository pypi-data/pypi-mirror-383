# Sphinx SVG.IO Package

This is a simple extension for embedding draw.io diagramms into sphinx docs.

### Usage


In conf.py:
```python
extensions = ["sphinx_svgio"]

drawio_js_offline_path = "path/to/viewer-static.min.js" # relative to conf.py or absolute
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


Also it is possible to add a description for every diagramm page:

```rst
.. svgio-list::
    :name: scheme_1

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

:name: option must be the same as in the target `svgio::` directive
