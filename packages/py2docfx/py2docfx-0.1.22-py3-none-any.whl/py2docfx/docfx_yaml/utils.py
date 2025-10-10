# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
import parameter_utils
from docutils.io import StringOutput
from docutils.utils import new_document
from docutils import nodes
from inspect import signature
from collections import namedtuple

from writer import MarkdownWriter as Writer

def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.

    # From Django
    """
    value = re.sub('[^\w\s-]', '', value).strip()
    return re.sub('[-\s]+', '-', value)


def transform_string(app, string):
    ret = []
    for para in string.split('\n\n'):
        tmp = nodes.paragraph(para, para)
        ret.append(transform_node(app, tmp))
    return '\n\n'.join(ret)


def transform_node(app, node):
    destination = StringOutput(encoding='utf-8')
    doc = new_document(b'<partial node>')
    doc.append(node)

    # Resolve refs
    doc['docname'] = 'inmemory'
    app.env.resolve_references(doctree=doc, fromdocname='inmemory', builder=app.builder)

    writer = Writer(app.builder)
    writer.write(doc, destination)
    return destination.destination.decode('utf-8')

def is_built_in_type(name: str, node) -> bool:
    return parameter_utils.is_system_type(name) or parameter_utils.is_typing(name, node)