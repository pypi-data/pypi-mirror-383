from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

from .nodes import ListItemNode, ListNode


class SvgioPageDirective(SphinxDirective):

    option_spec = {
        "page": directives.positive_int,
    }

    required_arguments = 0
    has_content = True

    def run(self):

        node = ListItemNode(page_id=self.options.get("page")-1)

        self.set_source_info(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class SvgioListDirective(SphinxDirective):

    option_spec = {
        "name": directives.unchanged_required,
    }

    required_arguments = 0
    has_content = True

    def run(self):

        node = ListNode(diagram_name=self.options.get("name"))

        self.set_source_info(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def setup_directives(app: Sphinx):

    app.add_directive("svgio-list", SvgioListDirective)
    app.add_directive("svgio-page", SvgioPageDirective)
