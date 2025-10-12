"""Objects to connect to Dropbox."""

import os
import json
import dropbox

from dropboxdol.util import config_join, DFLT_CONFIG_FILE, config_store


def get_tokens_interactive(app_key: str, app_secret: str):
    """
    Runs an interactive OAuth flow to obtain an access token and a refresh token.

    Ensure you pass your Dropbox app key and secret. This flow will print an
    authorization URL. Visit the URL in your browser, authorize the app, then
    paste the resulting code into the prompt.

    Returns:
      A tuple (access_token, refresh_token)
    """
    flow = dropbox.DropboxOAuth2FlowNoRedirect(
        app_key, app_secret, token_access_type="offline"
    )
    authorize_url = flow.start()
    print("1. Go to: " + authorize_url)
    print("2. Click 'Allow' (you might need to log in first).")
    print("3. Copy the authorization code and paste it in the user input dialogue.")
    code = input("Enter the authorization code here: ").strip()
    oauth_result = flow.finish(code)
    return oauth_result.access_token, oauth_result.refresh_token


def get_envvar_if_upper_case_and_exists(config: str) -> str:
    """
    Retrieve a configuration value.

    First checks os.environ for the given key. If present, returns its value;
    otherwise, returns the key itself (allowing you to pass literal values).
    """
    if isinstance(config, str) and config.isupper() and config in os.environ:
        return os.environ[config]
    return config


import warnings
import dropbox


def get_client_from_args(
    oauth2_access_token: str,
    oauth2_refresh_token: str = None,
    app_key: str = None,
    app_secret: str = None,
) -> dropbox.Dropbox:
    """
    Create a Dropbox client using explicit credentials with additional validation.

    Validation includes:
      - Ensuring that oauth2_access_token is provided and is a non-empty string.
      - If any of oauth2_refresh_token, app_key, or app_secret are provided, then all must be provided
        to enable auto-refresh.
      - Issuing soft warnings if any of the parameters appear to be environment variable names
        (all uppercase), which might indicate that the caller intended to pass literal values.

    Parameters:
      oauth2_access_token (str): The Dropbox access token.
      oauth2_refresh_token (str, optional): The Dropbox refresh token.
      app_key (str, optional): Your Dropbox app key.
      app_secret (str, optional): Your Dropbox app secret.

    Returns:
      dropbox.Dropbox: A Dropbox client instance.
    """
    # Hard validation for oauth2_access_token.
    if not oauth2_access_token or not isinstance(oauth2_access_token, str):
        raise ValueError(
            "A valid oauth2_access_token must be provided as a non-empty string."
        )

    # Soft warning if oauth2_access_token is all uppercase (likely an env var name).
    if oauth2_access_token.isupper():
        warnings.warn(
            "The provided oauth2_access_token appears to be all uppercase. "
            "This is typically used for environment variable names. "
            "If you intended to pass a literal token, consider using lowercase or mixed case."
        )

    # Determine if auto-refresh is requested (i.e. any of the three additional parameters provided)
    auto_refresh_requested = any([oauth2_refresh_token, app_key, app_secret])
    if auto_refresh_requested:
        # All three must be provided if any are.
        if not (oauth2_refresh_token and app_key and app_secret):
            raise ValueError(
                "Incomplete auto-refresh configuration: "
                "if you wish to enable auto-refresh, you must supply oauth2_refresh_token, app_key, and app_secret."
            )
        # Soft warnings for each parameter if they appear to be env var names.
        if oauth2_refresh_token.isupper():
            warnings.warn(
                "The provided oauth2_refresh_token appears to be all uppercase. "
                "Ensure you are passing the actual refresh token, not just the environment variable name."
            )
        if app_key.isupper():
            warnings.warn(
                "The provided app_key appears to be all uppercase. "
                "Ensure you are passing the actual app key, not just the environment variable name."
            )
        if app_secret.isupper():
            warnings.warn(
                "The provided app_secret appears to be all uppercase. "
                "Ensure you are passing the actual app secret, not just the environment variable name."
            )
        # Instantiate an auto-refreshing Dropbox client.
        return dropbox.Dropbox(
            oauth2_access_token=oauth2_access_token,
            oauth2_refresh_token=oauth2_refresh_token,
            app_key=app_key,
            app_secret=app_secret,
        )
    else:
        # If no auto-refresh credentials are provided, create a basic client.
        return dropbox.Dropbox(oauth2_access_token=oauth2_access_token)


def config_file_to_dict(config_filepath: str) -> dict:
    if not os.path.exists(config_filepath):
        _config_filepath = config_filepath
        config_filepath = config_join(config_filepath)
        if not os.path.exists(config_filepath):
            raise FileNotFoundError(
                f"Neither configuration file '{_config_filepath}', "
                f"nor {config_filepath} were found. "
                "Please ensure it exists."
            )

    with open(config_filepath, "rt") as f:
        config = json.load(f)

    return config


def _only_non_none_values(d: dict):
    return {k: v for k, v in d.items() if v is not None}


def _assert_config_file_is_not_a_filepath(config_file: str):

    if os.path.exists(config_file):
        raise ValueError(
            "This function is for creating or editing configuration files of a "
            "dropboxdol maintained config store (config_store) only. "
            "The config_file you provided exists as an actual file, so I prefer to "
            "raise an error to bring that ambiguity to your attention."
        )


def _config_store_value_or_empty_dict(config_file: str):
    _assert_config_file_is_not_a_filepath(config_file)
    return config_store.get(config_file, {})


def create_or_edit_config_file(
    config_file: str,
    *,
    oauth2_access_token=None,
    oauth2_refresh_token=None,
    app_key=None,
    app_secret=None,
):

    config = _config_store_value_or_empty_dict(config_file)

    # update config with non-None values
    edits = dict(
        oauth2_access_token=oauth2_access_token,
        oauth2_refresh_token=oauth2_refresh_token,
        app_key=app_key,
        app_secret=app_secret,
    )
    config.update(_only_non_none_values(edits))

    config_store[config_file] = config


def complete_config_file_with_refresh_token(config_file):
    config = config_store[config_file]
    app_key = config["app_key"]
    app_secret = config["app_secret"]

    access_token, refresh_token = get_tokens_interactive(app_key, app_secret)

    create_or_edit_config_file(
        config_file,
        oauth2_access_token=access_token,
        oauth2_refresh_token=refresh_token,
    )


def create_config_file(
    config_file,
    *,
    app_key,
    app_secret,
    oauth2_access_token=None,
    oauth2_refresh_token=None,
):
    """
    Create a configuration file for a Dropbox client.

    If the file already exists, a FileExistsError will be raised.
    The `config_file` must be a sring ending with '.json'.
    If oauth2_refresh_token is not given, an interactive flow will be used to obtain it,
    also replacing the oauth2_access_token.
    """
    assert config_file.endswith(".json"), "Config file must end with '.json'"
    if config_file in config_store:
        raise FileExistsError(
            f"Configuration file '{config_file}' already exists. "
            "Please use create_or_edit_config_file() to edit it, or delete it first."
        )

    create_or_edit_config_file(config_file, app_key=app_key, app_secret=app_secret)
    if oauth2_access_token is None:
        complete_config_file_with_refresh_token(config_file)
    else:
        create_or_edit_config_file(
            config_file,
            oauth2_access_token=oauth2_access_token,
            oauth2_refresh_token=oauth2_refresh_token,
        )


def copy_config_file(src_config_file, dest_config_file=None):
    """
    Copy a configuration file from one location to another.

    If the destination file already exists, a FileExistsError will be raised.
    """
    if dest_config_file is None:
        dest_config_file = f"{src_config_file}_copy.json"
    config_store[dest_config_file] = config_store[src_config_file]


def get_client_from_config_file(config_filepath: str) -> dropbox.Dropbox:
    """
    Create a Dropbox client by loading configuration from a JSON file.

    The JSON file must contain the keys:
      - "oauth2_access_token"
      - "oauth2_refresh_token"
      - "app_key"
      - "app_secret"

    Raises:
      FileNotFoundError: If the config file does not exist.
      Exception: If required keys are missing.
    """
    config = config_file_to_dict(config_filepath)

    token, refresh, key, secret = map(
        config.get,
        ("oauth2_access_token", "oauth2_refresh_token", "app_key", "app_secret"),
    )

    if not token or not refresh or not key or not secret:
        raise Exception(
            "Configuration file is missing one or more required keys: "
            "'oauth2_access_token', 'oauth2_refresh_token', 'app_key', 'app_secret'."
        )
    return get_client_from_args(token, refresh, key, secret)


def _getenv_or_none(key: str) -> str:
    if key is None:
        return None
    return os.environ.get(key)


def get_client_from_environment_vars(
    oauth2_access_token: str,
    oauth2_refresh_token: str = None,
    app_key: str = None,
    app_secret: str = None,
) -> dropbox.Dropbox:
    """
    Create a Dropbox client using configuration from environment variables.

    The provided parameter names are interpreted as the names of the environment variables.
    For example, calling:

        get_client_from_environment_vars("DROPBOX_ACCESS_TOKEN", "DROPBOX_REFRESH_TOKEN",
                                         "DROPBOX_APP_KEY", "DROPBOX_APP_SECRET")

    will use the values from os.environ (if they exist), or fall back to the literal strings.
    """
    token, refresh, key, secret = map(
        get_envvar_if_upper_case_and_exists,
        (oauth2_access_token, oauth2_refresh_token, app_key, app_secret),
    )
    return get_client_from_args(token, refresh, key, secret)


def get_client(config=DFLT_CONFIG_FILE, **kwargs) -> dropbox.Dropbox:
    """
    Return a Dropbox client using the best available configuration source.

    Priority:
      1. If an oauth2_access_token is provided and ends with '.json', load configuration from that file.
      2. Else, if the environment variable (named by oauth2_access_token) exists, use environment variables.
      3. Otherwise, use explicit parameters provided via kwargs.

    Expected keyword arguments:
      - oauth2_access_token
      - oauth2_refresh_token
      - app_key
      - app_secret
    """
    # Try to get the oauth2_access_token value

    if isinstance(config, str):
        config = config_file_to_dict(config)
    elif config is None:
        config = {}
    else:
        if not isinstance(config, dict):
            raise TypeError(
                f"Invalid config. Should be a file name/path string or a dict {config}"
            )

    # update kwargs with config
    kwargs.update(config)

    # apply get_envvar_if_upper_case_and_exists to all kwargs
    kwargs = {k: get_envvar_if_upper_case_and_exists(v) for k, v in kwargs.items()}

    return get_client_from_args(**kwargs)
