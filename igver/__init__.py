import os

from .igver import load_screenshots, run_igv, create_batch_script

try:
    from importlib.metadata import version
except ImportError:  # For Python <3.8
    from importlib_metadata import version

__version__ = version("igver")
__file__ = os.path.abspath(__file__)  # Store absolute path of this file
__all__ = ["load_screenshots", "run_igv", "create_batch_script"]
