# https://www.sphinx-doc.org/en/master/usage/configuration.html
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

from __future__ import annotations

from importlib import metadata

# {{{ project information

m = metadata.metadata("pycgdescent")
project = m["Name"]
author = m["Author-email"]
copyright = f"2020 {author}"  # noqa: A001
version = m["Version"]
release = version

# }}}

# {{{ general configuration

# needed extensions
extensions = [
    "autoapi.extension",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
]

try:
    import sphinxcontrib.spelling  # noqa: F401

    extensions.append("sphinxcontrib.spelling")
except ImportError:
    pass

# extension for source files
source_suffix = ".rst"
# name of the main (master) document
master_doc = "index"
# min sphinx version
needs_sphinx = "6.0"
# files to ignore
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
# highlighting
pygments_style = "sphinx"

# }}}

# {{{ internationalization

language = "en"

# sphinxcontrib.spelling options
spelling_lang = "en_US"
tokenizer_lang = "en_US"
spelling_word_list_filename = "wordlist_en.txt"

# }}

# {{{ output

# html
html_theme = "sphinx_book_theme"
html_title = "pycgdescent"
html_theme_options = {
    "show_toc_level": 2,
    "use_source_button": True,
    "use_repository_button": True,
    "navigation_with_keys": False,
    "repository_url": "https://github.com/alexfikl/pycgdescent",
    "repository_branch": "main",
    "icon_links": [
        {
            "name": "Release",
            "url": "https://github.com/alexfikl/pycgdescent/releases",
            "icon": "https://img.shields.io/github/v/release/alexfikl/pycgdescent",
            "type": "url",
        },
        {
            "name": "License",
            "url": "https://github.com/alexfikl/pycgdescent/tree/main/LICENSES",
            "icon": "https://img.shields.io/badge/License-GPL_2.0-blue.svg",
            "type": "url",
        },
        {
            "name": "CI",
            "url": "https://github.com/alexfikl/pycgdescent",
            "icon": "https://github.com/alexfikl/pycgdescent/workflows/CI/badge.svg",
            "type": "url",
        },
        {
            "name": "Issues",
            "url": "https://github.com/alexfikl/pycgdescent/issues",
            "icon": "https://img.shields.io/github/issues/alexfikl/pycgdescent",
            "type": "url",
        },
        {
            "Name": "PyPI",
            "url": "https://pypi.org/project/pycgdescent",
            "icon": "https://badge.fury.io/py/pycgdescent.svg",
            "type": "url",
        },
    ],
}

html_static_path = ["_static"]

# }}}

# {{{ extension settings

autoapi_type = "python"
autoapi_dirs = ["."]
autoapi_add_toctree_entry = False

autoapi_python_class_content = "class"
autoapi_member_order = "bysource"
autoapi_options = [
    "show-inheritance",
    "show-signatures",
]

autodoc_typehints = "description"
# NOTE: values are `(inventory, module, reftype)`
custom_type_links = {
    # NOTE: `numpy.float64` tries to link to `pycgdescent.float64` in some
    # annotations, so this will re-route it back to the numpy documentation
    "numpy.float64": ("numpy", "numpy", "attr"),
}


def process_autodoc_missing_reference(app, env, node, contnode):
    """Fix missing references due to string annotations."""
    # NOTE: only classes for now, since we just need some numpy objects
    if node["reftype"] != "class":
        return None

    target = node["reftarget"]
    if target not in custom_type_links:
        return None

    from sphinx.ext import intersphinx

    inventory, module, reftype = custom_type_links[target]
    if inventory:
        node.attributes["py:module"] = module
        node.attributes["reftype"] = reftype

        return intersphinx.resolve_reference_in_inventory(
            env, inventory, node, contnode
        )
    else:
        # TODO: put local missing references in here :D
        return None


def setup(app):
    app.connect("missing-reference", process_autodoc_missing_reference)


# }}}

# {{{ links

intersphinx_mapping = {
    "numpy": ("https://numpy.org/doc/stable", None),
    "python": ("https://docs.python.org/3", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
}

# }}}
