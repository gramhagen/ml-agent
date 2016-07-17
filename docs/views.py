# -*- coding: utf-8 -*-
"""
Container for documentation pages
"""

from flask import Blueprint
from flask import render_template


doc_app = Blueprint('docs', __name__,
                    url_prefix='/docs',
                    template_folder='_build/html',
                    static_folder='_build/html/_static')


@doc_app.route('/')
@doc_app.route('/<src>')
def docs(src='index.html'):
    """
    provides access to documentation

    Returns:
        (html): documentation
    """

    return render_template(src)
