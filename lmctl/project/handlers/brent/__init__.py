from .brent_content import BrentContentHandlerDelegate
from .brent_src import BrentSourceHandlerDelegate, BrentSourceCreatorDelegate

source_creator = BrentSourceCreatorDelegate
source_handler = BrentSourceHandlerDelegate
content_handler = BrentContentHandlerDelegate