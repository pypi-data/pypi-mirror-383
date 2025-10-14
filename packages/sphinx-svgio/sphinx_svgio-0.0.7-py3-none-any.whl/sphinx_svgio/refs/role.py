import re

from sphinx.application import Sphinx
from sphinx.util.docutils import ReferenceRole

from .node import DiagramPageRefNode


class DiagramPageRef(ReferenceRole):

    def run(self):

        pattern = re.compile(r"(\w+):(\w+)")

        matched = pattern.match(self.target)

        self.name = matched.group(1)
        self.page = matched.group(2)

        node = DiagramPageRefNode(name=self.name,
                                  page=self.page,
                                  text=self.title)

        return ([node], [])


def setup_role(app: Sphinx):
    app.add_role("pageref", DiagramPageRef())
