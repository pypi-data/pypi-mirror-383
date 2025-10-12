from os import environ
from uuid import uuid4
from dropboxdol.tests.base_test import BasePersisterTest

from dol import Store
from dol.errors import OverWritesNotAllowedError, DeletionsNotAllowed
from dropboxdol.base import DropboxPersister, DropboxLinkReaderWithToken

ROOT_DIR = environ.get("DROPBOX_ROOT_DIR", "/test_data")

TEST_DROPBOX_ACCESS_TOKEN = environ.get("TEST_DROPBOX_ACCESS_TOKEN")
TEST_DROPBOX_REFRESH_TOKEN = environ.get("TEST_DROPBOX_ACCESS_TOKEN")
TEST_DROPBOX_APP_KEY = environ.get("TEST_DROPBOX_ACCESS_TOKEN")
TEST_DROPBOX_APP_SECRET = environ.get("TEST_DROPBOX_ACCESS_TOKEN")

test_config = {
    "oauth2_access_token": environ.get("TEST_DROPBOX_ACCESS_TOKEN"),
    "oauth2_refresh_token": environ.get("TEST_DROPBOX_REFRESH_TOKEN"),
    "app_key": environ.get("TEST_DROPBOX_APP_KEY"),
    "app_secret": environ.get("TEST_DROPBOX_APP_SECRET"),
}

if any(val is None for val in test_config.values()):
    raise ValueError(
        "To run tests, you must set the following environment variables: "
        "TEST_DROPBOX_ACCESS_TOKEN, TEST_DROPBOX_REFRESH_TOKEN, TEST_DROPBOX_APP_KEY, TEST_DROPBOX_APP_SECRET"
    )


class TestDropboxPersister(BasePersisterTest):
    db = DropboxPersister(rootdir=ROOT_DIR, connection_config=test_config)

    key = "/".join((ROOT_DIR, uuid4().hex))
    data = b"Some binary data here."
    data_updated = b"Smth completely different."
    inexistent_key = "/".join((ROOT_DIR, uuid4().hex, "x"))


class TestDropboxLinkPersister(TestDropboxPersister):
    db = DropboxLinkReaderWithToken(
        url="https://www.dropbox.com/sh/0ru09jmk0w9tdnr/AAA-PPON2sYmwUUoGQpBQh1Ia?dl=0",
        connection_config=test_config,
    )

    def _create_test_file(self):
        db = DropboxPersister(rootdir=ROOT_DIR, connection_config=test_config)
        db[self.key] = self.data

    def test_crud(self):
        # Read-a-file test only, since LinkPersister has a read-only access.
        self._create_test_file()
        self._test_read()

        all_objects = list(self.db)
        key = all_objects[0]
        # assert self.db[key]  # TODO: Fix this assertion


def _delete_keys_from_store(store, keys_to_delete):
    for k in keys_to_delete:
        if k in store:  # if key already in s, delete it
            del store[k]


def _test_ops_on_store(store):
    s = store  # just to be able to use shorthand "s"

    _delete_keys_from_store(s, ["_foo", "_hello", "_non_existing_key_"])

    # test "not in"
    assert (
        "_non_existing_key_" not in s
    ), "I really wasn't expecting that key to be in there!"

    s["_foo"] = "bar"  # store 'bar' in '_foo'
    assert "_foo" in s, '"_foo" in s'
    assert s["_foo"] == "bar"

    s["_hello"] = "world"  # store 'world' in '_hello'

    if hasattr(s, "keys"):
        assert set(s.keys()).issuperset({"_foo", "_hello"})
    if hasattr(s, "values"):
        assert set(s.values()).issuperset({"bar", "world"})
    if hasattr(s, "items"):
        assert set(s.items()).issuperset({("_foo", "bar"), ("_hello", "world")})
    if hasattr(s, "get"):
        for k in s:
            assert s.get(k) == s[k]
        assert s.get("_hello") == "world"
        assert s.get("_non_existing_key_", "some default") == "some default"
        assert s.get("_non_existing_key_", None) is None
    if hasattr(s, "setdefault"):
        assert s.setdefault("_hello", "this_will_never_be_used") == "world"
        assert s.setdefault("_non_existing_key_", "this_will") == "this_will"
        assert s["_non_existing_key_"] == "this_will"
        del s["_non_existing_key_"]

    # test "not in" when there's something
    assert (
        "_non_existing_key_" not in s
    ), "I really wasn't expecting that key to be in there!"

    # wraped in try/except in case deleting is not allowed
    try:
        # testing deletion
        del s["_hello"]  # delet _hello
        assert "_hello" not in s
        s["_hello"] = "world"  # put it back

        if hasattr(s, "pop"):
            v = s.pop("_hello")
            assert v == "world"
            assert "_hello" not in s
            s["_hello"] = "world"  # put it back
    except DeletionsNotAllowed:
        pass

    # wraped in try/except in case overwriting is not allowed
    try:
        s["_foo"] = "a different value"
        assert s["_foo"] == "a different value"
    except OverWritesNotAllowedError:
        pass

    _delete_keys_from_store(s, ["_foo", "_hello"])


def _test_len(store):
    s = store  # just to be able to use shorthand "s"

    _delete_keys_from_store(s, ["_foo", "_hello"])

    n = len(s)  # remember how many items there are

    s["_foo"] = "bar"  # store 'bar' in '_foo'
    assert len(s) == n + 1, "You should have an extra item in the store"

    s["_hello"] = "world"  # store 'world' in '_hello'
    assert len(s) == n + 2, "You should have had two extra items in the store"

    try:
        # testing deletion
        del s["_hello"]  # delet _hello
        assert len(s) == n + 1
        s["_hello"] = "world"  # put it back

        if hasattr(s, "pop"):
            _ = s.pop("_hello")
            assert len(s) == n + 1
            s["_hello"] = "world"  # put it back
    except DeletionsNotAllowed:
        pass

    # wraped in try/except in case overwriting is not allowed
    try:
        s["_foo"] = "a different value"
        assert len(s) == n + 2
    except OverWritesNotAllowedError:
        pass

    _delete_keys_from_store(s, ["_foo", "_hello"])


def _multi_test(store):
    _test_ops_on_store(store)
    _test_len(store)
    s = Store.wrap(store)  # empty wrapping of an instance
    _test_ops_on_store(s)
    _test_len(s)


# def test_dropbox():
#     from dol.util import ModuleNotFoundIgnore

#     with ModuleNotFoundIgnore():
#         from dropboxdol import DropboxTextFiles
#         import json
#         import os

#         try:
#             FAK = '$fak'
#             filepath = os.path.expanduser(
#                 '~/.py2store_configs/stores/json/dropbox.json'
#             )
#             configs = json.load(open(filepath))
#             store = DropboxTextFiles('/py2store_data/test/', **configs[FAK]['k'])
#             _multi_test(store)
#         except FileNotFoundError:
#             from warnings import warn

#             warn(f'FileNotFoundError: {filepath}')
