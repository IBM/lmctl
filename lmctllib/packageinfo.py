from pathlib import Path
import os
from lmctllib.utils.logging import *

logger = logging.getLogger(__name__)

def determine_root_path ():
  """Borrowed from wxglade.py"""
  try:
    root = __file__
    if os.path.islink (root):
        root = os.path.realpath (root)
    return os.path.dirname (os.path.abspath (root))
  except:
    logger.error("Cannot get the package root path.")
    sys.exit (-1)
