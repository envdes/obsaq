# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OBSAQ'
copyright = '2024, Haofan Wang'
author = 'Haofan Wang'
release = 'v0.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # 'recommonmark',
    # 'sphinx_markdown_tables',
    # 'sphinx.ext.githubpages',
    'nbsphinx',
    # 'IPython.sphinxext.ipython_console_highlighting',
    # 'sphinx.ext.autodoc', 
    # 'numpydoc', 
    # 'sphinx.ext.autosummary',
    # 'sphinx.ext.mathjax',
    # 'sphinx.ext.autodoc',
    # 'sphinx.ext.napoleon'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
