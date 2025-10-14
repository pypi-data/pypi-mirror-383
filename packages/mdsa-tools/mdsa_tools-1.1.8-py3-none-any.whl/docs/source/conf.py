exclude_patterns = ["_api/*"]

# docs/source/conf.py
import os, sys
sys.path.insert(0, os.path.abspath("../.."))

# Setting our titles and stuff
project = "mdsa-tools"
html_title = "mdsa-tools"
html_short_title = "mdsa-tools"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_design",
    "numpydoc",
    'sphinx_rtd_theme',
]

autosummary_generate = True

# Reduce duplication from numpydoc:
numpydoc_show_class_members = True
numpydoc_class_members_toctree = True

# So I can get attributes to work
napoleon_custom_sections = [
    ('Warnings', 'admonition'),
    ('Yield', 'params_style'),
    'API Notes'
]

# Reduces overhead
autodoc_mock_imports = [
    "mdtraj", "matplotlib", "seaborn", "sklearn", "umap", "pandas", "scipy",
    "pycircos"
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}



html_theme_options = {
    # Keep the logo/title at the left
    "navbar_start": ["navbar-logo"],

    # Keep search + theme switcher etc. on the right (optional)
    "navbar_end": ["search-field.html", "theme-switcher", "navbar-icon-links"],
    "show_nav_level": 2,
    "show_toc_level": 2,
}

templates_path = ["_templates"]

html_sidebars = {
    "**": [
        "globaltoc.html",     # RTD global ToC
        "searchbox.html",     # RTD search box
        "github-badge.html",  # your custom partial
    ]
}
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Theme settings 
html_theme = "renku"
html_show_sourcelink = False



root_doc = "index"

# Static files (e.g., CSS) for customization
html_static_path = ["_static"]
html_css_files = ["fullwidth.css"]

mdsa = "mdsa_tools.cli:main"
