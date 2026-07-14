"""Near-earth object monitoring tools."""

import logging


# Library modules may record diagnostic details, but importing this package must
# never change a caller's terminal output. The CLI replaces this with its own
# handlers only when --verbose or --log-file is requested.
logging.getLogger(__name__).addHandler(logging.NullHandler())
