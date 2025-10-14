from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger

from .nodes import ListItemNode, ListNode

LOGGER = getLogger(__name__)


class SvgioPageDirective(SphinxDirective):

    option_spec = {
        "page": directives.positive_int,
    }

    has_content = True

    def run(self):

        node = ListItemNode(page_id=self.options.get("page")-1)

        self.set_source_info(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class SvgioListDirective(SphinxDirective):

    option_spec = {
        "name": directives.unchanged_required,
        "expand": directives.flag
    }

    has_content = True

    def _validate_content(self, node: ListNode):

        ids = []
        for page in node.children:
            try:
                ids.append(page.page_id)
            except AttributeError:
                LOGGER.warning(
                    "All children of a 'svgio-list' "
                    "should be 'svgio-page'",
                    location=page,
                    type="svgio",
                    subtype="list",
                )
                return

        if len(ids) > len(set(ids)):
            LOGGER.warning(
                "Dublicates among page descriptions",
                location=node,
                type="svgio",
                subtype="list",
                )

    def run(self):
        node = ListNode(
            diagram_name=self.options.get("name"),
            expand="expand" in self.options.keys()
            )

        self.set_source_info(node)
        self.state.nested_parse(self.content, self.content_offset, node)

        self._validate_content(node)
        return [node]


def setup_directives(app: Sphinx):

    app.add_directive("svgio-list", SvgioListDirective)
    app.add_directive("svgio-page", SvgioPageDirective)
