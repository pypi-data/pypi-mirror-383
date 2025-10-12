"""
Access dropbox with dict-like interface.

"""

from dropboxdol.base import (
    dropbox_link,
    DropboxPersister,
    DropboxFiles,
    DropboxTextFiles,
    DropboxLinkReaderWithToken,
    DropboxBinaryStore,  # deprecated: Use DropboxFiles instead
    DropboxTextStore,  # deprecated: Use DropboxTextFiles instead
)

from dropboxdol.util import (
    config_store,
)

from dropboxdol.connection import (
    create_config_file,
    create_or_edit_config_file,
    complete_config_file_with_refresh_token,
    get_client,
)
