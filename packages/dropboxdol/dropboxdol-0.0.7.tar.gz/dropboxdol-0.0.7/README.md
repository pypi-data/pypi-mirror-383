# dropboxdol

dropbox with a simple (dict-like or list-like) interface


To install:	```pip install dropboxdol```


# Setup

Note: To use `dropboxdol`, you'll need to have a dropbox access token. 
Additionally, that token should be allowed to do the operation that you are doing. 
For example, you only need the "sharing.write" permission to CREATE a (new) shared link. 

See more information in [Dropbox's Auth Guide](https://developers.dropbox.com/oauth-guide). 


By default, `dropboxdol` looks for the access tokens and other information is 
(well, really, the dropbox API) needs)
in the `"default_dropbox_config.json"` file of the dropboxdol app data. 
You can interact with those files via `dropboxdol.config_store`, which has a dict-like interface to the files in that folder. 

If you don't have a `"default_dropbox_config.json"` file, you'll need to specify the 
connection config explicitly (by specifying a config dict, a filepath, filename of the 
`config_store`).

Note that at this point, dropbox only dishes out temporary access tokens.
This means you can't just save an access token once and be over with it. 
So to get the convenience of automatic connections, you'll need to specify not only a 
`oauth2_access_token`, but also a `oauth2_refresh_token`, an `app_key` and an `app_secret`. 

You can read all about that annoying stuff in the [Dropbox's Auth Guide](https://developers.dropbox.com/oauth-guide).

But here's a few things to make it a bit less painful:
* make an "app" in the [app console](https://www.dropbox.com/developers/apps?_tk=pilot_lp&_ad=topbar4&_camp=myapps)
* specify scope and permissions you want on it
* note down the app key and the app secret

then use the following, which will walk you through the steps to get your access and refresh tokens.

These will then be stored in the `config_file` of your choice, so that all you have to 
do is mention the file to get the connection.

```python
from dropboxdol import create_config_file

create_config_file(
    config_file='NAME_OF_YOUR_APP_OR_WHATEVER_NAME_YOU_WILL_REMEMBER.json',
    app_key='YOUR_APP_KEY', 
    app_secret='YOUR_APP_SECRET',
)
```

If you already have a config file for this app, with app_key and app_secret, 
you can update the tokens by doing this:

```python
from dropboxdol import complete_config_file_with_refresh_token

complete_config_file_with_refresh_token(
    config_file='NAME_OF_YOUR_APP_OR_WHATEVER_YOU_CALLED_THAT_CONFIG.json',
)
```

If you want to edit some configs, you can do so by editing the file directly, or use 
`create_or_edit_config_file`.

```python
from dropboxdol import create_or_edit_config_file

create_or_edit_config_file(
    config_file='CONFIG_FILE.json',
    # whatever edits you want to make... (specifying None will skip that config, leaving it unchanged)
    oauth2_access_token=None,
    oauth2_refresh_token=None,
    app_key=None,
    app_secret=None,
)
```

# Examples 


## Get a dropbox "store"

### From a link

```python
from dropboxdol import DropboxLinkReaderWithToken

s = DropboxLinkReaderWithToken(
    url="https://www.dropbox.com/sh/0ru09jmk0w9tdnr/AAA-PPON2sYmwUUoGQpBQh1Ia?dl=0"
)
keys = list(s)
keys
```

    ['inner_folder',
    'b1467f55540c4695bf483bc542e43256',
    '0b98e2af76c94a0a9cc2808866dd62de',
    '3372aa35ea444c758bfa2e4599b2576d',
    '9de9d98a4c4648cca1bc1131c307a365',
    '91c744890d374dd8bc914f1153311b0c',
    '57af886dd22f4a23a678a3de3eb996a0',
    '43ba127e5e9245ec983c9f39e4ed7306']


### From a local path (but talking to the remote files)

```python
from dropboxdol import DropboxFiles
from i2 import Sig 

t = DropboxFiles('/Apps/py2store/py2store_data')
list(t)
```

    ['/test', '/test.txt', '/another_test.txt']

```python
t['/test.txt']
```

    b'This is a test.\nSee it work.\nAnd what about unicode? \xc3\xa8\xc3\xa9\xc3\xaa\xc3\xab\xc4\x93\xc4\x97\xc4\x99?'


## Get dropbox links for local files/folders

(Your token needs the "sharing.write" permission to CREATE a (new) shared link.)

```python
>>> from dropboxdol import dropbox_link
>>> local_file = '/Users/thorwhalen/Dropbox/Apps/py2store/py2store_data/test.txt'
>>> dropbox_url = dropbox_link(local_file)
>>> print(dropbox_url)
```

    https://www.dropbox.com/scl/fi/3o8ooqje4f497npxdeiwg/test.txt?rlkey=x9jsd8u7k147x6fzc7stxozqe&dl=0

If you want to talk "relative" to the dropbox root dir, do this:

```python
>>> from functools import partial
>>> my_dropbox_link = partial(dropbox_link, dropbox_local_rootdir='/Users/thorwhalen/Dropbox')
```

If you want a "direct (download) link", do this:

```python
>>> dl1_link = my_dropbox_link('Apps/py2store/py2store_data/test.txt', dl=1)
```

    'https://www.dropbox.com/scl/fi/3o8ooqje4f497npxdeiwg/test.txt?rlkey=x9jsd8u7k147x6fzc7stxozqe&dl=1'


## Easy read/write access to your dropbox files 

A persister for dropbox.

```python
>>> import json
>>> import os
>>> from dropboxdol import DropboxPersister
>>> configs = json.load(open(os.path.expanduser('~/.py2store_configs.json')))
>>> s = DropboxPersister('/py2store_data/test/', **configs['dropbox']['__init__kwargs'])
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
```


