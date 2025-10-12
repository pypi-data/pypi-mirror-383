"""Base functions for dropboxdol."""

from typing import Union

import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.sharing import SharedLinkSettings, RequestedVisibility
from dropboxdol.util import (
    # get_access_token,
    # DFLT_ACCESS_TOKEN,
    get_local_full_path,
    modify_url_dl,
    compute_dbx_file_path,
)
from dropboxdol.connection import get_client, DFLT_CONFIG_FILE


def create_or_get_shared_link(dbx: dropbox.Dropbox, dbx_file_path: str) -> str:
    """
    Create a shared link for the given Dropbox file path.

    If a shared link already exists, list and return the first one.
    Raises an exception with detailed information on authentication errors.
    """
    settings = SharedLinkSettings(requested_visibility=RequestedVisibility.public)
    try:
        link_metadata = dbx.sharing_create_shared_link_with_settings(
            dbx_file_path, settings
        )
        return link_metadata.url
    except ApiError as err:
        # If the error indicates a shared link already exists, retrieve it.
        if err.error.is_shared_link_already_exists():
            try:
                links = dbx.sharing_list_shared_links(
                    path=dbx_file_path, direct_only=True
                ).links
                if links:
                    return links[0].url
                else:
                    raise Exception(
                        "A shared link for the file exists but could not be retrieved."
                    )
            except Exception as list_err:
                raise Exception(
                    f"Failed to list existing shared links for '{dbx_file_path}': {list_err}"
                )
        elif isinstance(err, AuthError):
            raise Exception(
                "Authentication failed. The access token provided (or retrieved from environment variable) appears invalid. "
                "First attempted to fetch the token from os.environ using the provided key; if not found, used the given access token. "
                "Please verify that your access token is correct and has the necessary scopes."
            )
        else:
            raise Exception(
                f"Failed to create shared link for '{dbx_file_path}': {err}"
            )


def dropbox_link(
    path: str,
    *,
    dropbox_local_rootdir: str = None,
    dl: int = 0,
    access_config: Union[str, dict] = DFLT_CONFIG_FILE,
) -> str:
    """
    Returns a shareable Dropbox URL for the file at the given local path.

    The function:
      1. Retrieves the access token from os.environ using the given key or uses the provided token.
      2. Determines the absolute local file path (using dropbox_path if needed).
      3. Computes the Dropbox file path relative to the Dropbox folder.
      4. Attempts to create a shared link, or retrieves an existing one if it already exists.
      5. Modifies the URL to include the specified 'dl' parameter (e.g., dl=1 for direct download).

    Parameters:
      path (str): The file path (absolute or relative).
      dropbox_local_rootdir (Optional[str]): The local root Dropbox folder. If not provided, it will be inferred.
      dl (int): The value for the 'dl' parameter in the shared URL (default is 0).
      access_config (str): The access configuration (dict or file path)

    Returns:
      str: The modified shared URL.

    Raises:
      FileNotFoundError: If the file does not exist.
      Exception: For issues with path computation or Dropbox API errors.
    """
    # Get the access token

    # Determine the local full path and Dropbox folder
    local_full_path, dbx_root = get_local_full_path(path, dropbox_local_rootdir)

    # Compute the Dropbox file path
    dbx_file_path = compute_dbx_file_path(local_full_path, dbx_root)

    # Initialize the Dropbox client
    client = get_client(access_config)

    # Create or retrieve the shared link
    shared_url = create_or_get_shared_link(client, dbx_file_path)

    # Modify the URL with the desired dl parameter
    final_url = modify_url_dl(shared_url, dl)

    return final_url


# -----------------------------------------------------------------------------
# Old stuff


from dropbox import Dropbox
from dropbox.files import DownloadError
from dropbox.files import LookupError as DropboxLookupError
from dropbox.exceptions import ApiError
from dropbox.files import WriteMode, SharedLink

from dol.base import Persister
from dol.mixins import ReadOnlyMixin


def _is_file_not_found_error(error_object):
    if isinstance(error_object, ApiError):
        if len(error_object.args) >= 2:
            err = error_object.args[1]
            if isinstance(err, DownloadError) and isinstance(
                err.get_path(), DropboxLookupError
            ):
                return True
    return False


class DropboxPersister(Persister):
    """
    A persister for dropbox.
    You need to have the python connector (if you don't: pip install dropbox)
    You also need to have a token for your dropbox app. If you don't it's a google away.
    Finally, for the test below, you need to put this token in ~/.py2store_configs.json' under key
    dropbox.__init__kwargs, and have a folder named /py2store_data/test/ in your app space.

    >>> from dropboxdol.tests.test_dropbox import test_config
    >>> from dropboxdol import DropboxPersister
    >>> s = DropboxPersister('/py2store_data/test/', connection_config=test_config)
    >>> if '/py2store_data/test/_can_remove' in s:
    ...     del s['/py2store_data/test/_can_remove']
    ...
    >>>
    >>> n = len(s)
    >>> if n == 1:
    ...     assert list(s) == ['/py2store_data/test/_can_remove']
    ...
    >>> s['/py2store_data/test/_can_remove'] = b'this is a test'
    >>> assert len(s) == n + 1
    >>> assert s['/py2store_data/test/_can_remove'] == b'this is a test'
    >>> '/py2store_data/test/_can_remove' in s
    True
    >>> del s['/py2store_data/test/_can_remove']
    """

    def __init__(
        self,
        rootdir="",
        *,
        connection_config=DFLT_CONFIG_FILE,
        files_upload_kwargs=None,
        files_list_folder_kwargs=None,
        rev=None,
    ):

        if connection_config is None:
            connection_config = {}
        if files_upload_kwargs is None:
            files_upload_kwargs = {"mode": WriteMode.overwrite}
        if files_list_folder_kwargs is None:
            files_list_folder_kwargs = {
                "recursive": True,
                "include_non_downloadable_files": False,
            }

        self._prefix = rootdir
        self._con = get_client(connection_config)
        self._connection_config = connection_config
        self._files_upload_kwargs = files_upload_kwargs
        self._files_list_folder_kwargs = files_list_folder_kwargs
        self._rev = rev

    # TODO: __len__ is taken from Persister, which iterates and counts. Not efficient. Find direct api for this!

    def __iter__(self):
        r = self._con.files_list_folder(self._prefix)
        yield from (x.path_display for x in r.entries)
        cursor = r.cursor
        if r.has_more:
            r = self._con.files_list_folder_continue(cursor)
            yield from (x.path_display for x in r.entries)

    def __getitem__(self, k):
        try:
            metadata, contents_response = self._con.files_download(k)
        except ApiError as e:
            if _is_file_not_found_error(e):
                raise KeyError(f"Key doesn't exist: {k}")
            raise

        if not contents_response.status_code:
            raise ValueError(
                "Response code wasn't 200 when trying to download a file (yet the file seems to exist)."
            )

        return contents_response.content

    def __setitem__(self, k, v):
        return self._con.files_upload(v, k, **self._files_upload_kwargs)

    def __delitem__(self, k):
        return self._con.files_delete_v2(k, self._rev)


def _entry_is_dir(entry):
    return not hasattr(entry, "is_downloadable")


def _entry_is_file(entry):
    return hasattr(entry, "is_downloadable")


def _extend_path(path, extension):
    extend_path = "/" + path + "/" + extension + "/"
    extend_path.replace("//", "/")
    return extend_path


class DropboxLinkReaderWithToken(ReadOnlyMixin, DropboxPersister):
    def __init__(
        self,
        url,
        connection_config=DFLT_CONFIG_FILE,
        *,
        # copied from DropboxBase.files_list_folder
        path="",
        recursive=False,
        include_media_info=False,
        include_deleted=False,
        include_has_explicit_shared_members=False,
        include_mounted_folders=True,
        limit=None,
        include_property_groups=None,
        include_non_downloadable_files=True,
    ):
        self._con = get_client(connection_config)
        self.url = url
        self.shared_link = SharedLink(url=url)
        self.files_list_folder_kwargs = dict(
            path=path,
            recursive=recursive,
            include_media_info=include_media_info,
            include_deleted=include_deleted,
            include_has_explicit_shared_members=include_has_explicit_shared_members,
            include_mounted_folders=include_mounted_folders,
            limit=limit,
            include_property_groups=include_property_groups,
            include_non_downloadable_files=include_non_downloadable_files,
        )

    def __iter__(self):
        return (x.name for x in self._raw_iter())

    def _raw_iter(self):
        client = self._con

        result = client.files_list_folder(
            shared_link=self.shared_link, **self.files_list_folder_kwargs
        )

        yield from result.entries

        while result.has_more:
            result = client.files_list_folder_continue(result.cursor)
            yield from result.entries

    # TODO: Old. Delete when sure not needed

    # def _yield_from_files_list_folder(self, path, path_gen):
    #     """
    #     yield paths from path_gen, which can be a files_list_folder or a files_list_folder_continue,
    #     in a depth search manner.
    #     """
    #     for x in path_gen.entries:
    #         if _entry_is_file(x):
    #             yield x.path_display
    #         else:
    #             folder_path = _extend_path(path, x.name)
    #             yield from self._get_path_gen_from_path(path=folder_path)

    #     if path_gen.has_more:
    #         yield from self._get_path_gen_from_cursor(path_gen.cursor, path=path)

    # def _get_path_gen_from_path(self, path):
    #     path_gen = self._con.files_list_folder(
    #         path=path, recursive=False, shared_link=self.shared_link
    #     )
    #     yield from self._yield_from_files_list_folder(path, path_gen)

    # def _get_path_gen_from_cursor(self, cursor, path):
    #     path_gen = self._con.files_list_folder_continue(cursor)
    #     yield from self._yield_from_files_list_folder(path, path_gen)

    # def __iter__(self):
    #     yield from self._get_path_gen_from_path(path="")


from functools import wraps

from dol.base import Store
from dol.paths import PrefixRelativizationMixin


class DropboxFiles(PrefixRelativizationMixin, Store, DropboxPersister):
    # def __init__(
    #     self,
    #     rootdir='',
    #     *,
    #     connection_config=DFLT_CONFIG_FILE,
    #     files_upload_kwargs=None,
    #     files_list_folder_kwargs=None,
    #     rev=None,
    # ):
    #     kwargs = {k: v for k, v in locals().items() if k != "self"}
    #     super().__init__(store=DropboxPersister(**kwargs))
    #     self._prefix = self.store._prefix

    @wraps(DropboxPersister.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(store=DropboxPersister(*args, **kwargs))
        self._prefix = self.store._prefix


DropboxBinaryStore = DropboxFiles  # backwards compatibility


class DropboxTextFiles(DropboxFiles):
    def _obj_of_data(self, data):
        return data.decode()

    def _data_of_obj(self, obj):
        return obj.encode()


DropboxTextStore = DropboxTextFiles  # backwards compatibility
