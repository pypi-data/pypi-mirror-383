"""Initialize the backend server extension"""

try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings
    warnings.warn("Importing 'fileglancer' outside a proper installation.")
    __version__ = "dev"

import os
from fileglancer.app import Fileglancer

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "fileglancer"
    }]

def _jupyter_server_extension_points():
    """
    Returns a list of dictionaries with metadata describing
    where to find the `_load_jupyter_server_extension` function.
    """
    return [
        {
            "module": "fileglancer.app",
            "app": Fileglancer
        }
    ]
