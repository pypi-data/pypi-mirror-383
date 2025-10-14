"""
Internal API that should not be exposed outside to users.
Refrain from using this directly as there is no guarantee that this won't change
at any time.
"""

from __future__ import annotations

import builtins
import os
import typing as t


def init(api_key: str, *, workspace: str = "corridor", api_url: str | None = None) -> None:
    """Initialize SDK with provided options.

    :param api_key (str): The User API key to initialize connection to the Platform
    :param workspace (str): Optional. The workspace to use when making service calls. Defaults to `corridor`."""
    from genguardx._internal.util.networking import ApiAuth, api

    assert isinstance(api.session.auth, ApiAuth), (
        f"Unable to initialize corridor - Auth is being controlled by: {type(api.session.auth).__name__}"
    )

    api.session.auth.init_user(api_key, workspace)
    if api_url is not None:
        os.environ["CORRIDOR_API_URL"] = api_url
    whoami()  # Show the user who is logged in


def whoami() -> None:
    from genguardx._internal.util.constants import URLS
    from genguardx._internal.util.networking import ApiAuth, api, ujoin

    if isinstance(api.session.auth, ApiAuth) and api.session.auth.user_api_key is None:
        print(
            "Session not initialized.\n"
            "Fetch your API key from profile page and initialize session by running "
            "genguardx.init(api_key='your-api-key')"
        )
        return

    user_info: dict[t.Literal["visibleName", "name"], t.Any] = api.response(ujoin(URLS.USER_PATH.value, "/whoami"))[
        "result"
    ]
    workspace_name = api.session.auth.workspace

    if getattr(builtins, "__IPYTHON__", False) is True:
        from IPython import get_ipython

        ip = get_ipython()
        if ip.has_trait("kernel"):  # Need to differentiate between notebook environment and ipython shells
            # Handle environments where rich text formatting is supported by IPython. e.g. Jupyter Notebook
            from IPython.display import Markdown, display

            display(Markdown(f"Logged in as `{user_info['visibleName']}` to workspace `{workspace_name}`."))
            display(
                Markdown(f"Any changes made in this session will be **tracked** under the user `{user_info['name']}`.")
            )
            return

    # Handle environments when rich text formatting is not supported: e.g.: IPython REPLs, Python REPL, Scripts etc
    print(f"Logged in as {user_info['visibleName']!r} to workspace {workspace_name!r}.")
    print(f"Any changes made in this session will be tracked under the user {user_info['name']!r}.")
