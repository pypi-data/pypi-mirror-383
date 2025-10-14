from __future__ import annotations

import json as json_module
import os

import importlib_metadata
import requests
from requests.auth import AuthBase

from genguardx._internal import whoami


def ujoin(base: str, url: str) -> str:
    return str(base).rstrip("/") + "/" + str(url).lstrip("/")


class SessionConfig:
    """
    Note that this is only the configs set for the requests Session. So, for example: timeout, user, workspace
    are not kept here.
    - timeout is a request level config, can change for every API call
    - user, workspace is for auth in the request, can change for every API call
    """

    api_url: str
    verify: bool
    ssl_certificate: str | None
    ssl_private_key: str | None

    @staticmethod
    def get_env_value(key: str, default: str) -> str:
        return os.environ.get(key, str(default))

    @staticmethod
    def get_value(key: str, default: str) -> str:
        """
        Get the config value from:
        1. genguardx._configs (first preference)
        2. Environment Variable
        """
        try:
            # _configs is a file that can be embeeded by clients in a wheel or conda pkg that they may want
            # to distirbute to their users which has some builtin configs
            from genguardx import _configs
        except ImportError:
            _configs = None

        if _configs is not None and hasattr(_configs, key):
            # Convert to string, as env variables will always be string
            return str(getattr(_configs, key))

        return SessionConfig.get_env_value(key, default)

    @property
    def api_url(self) -> str:
        # Earlier, we used to need the /corr-api URL as we used to use corridor-api. Now, we just need the corridor
        # instance URL. So, add /corr-api to the URL if it's not already there.
        url = self.get_value("CORRIDOR_API_URL", "http://localhost:5002/corr-api")
        if url.endswith("/corr-api"):
            return url
        return url.rstrip("/") + "/corr-api"

    @api_url.setter
    def api_url(self, val: str) -> None:
        os.environ["CORRIDOR_API_URL"] = val

    @property
    def verify(self) -> bool:
        return self.get_value("CORRIDOR_API_VERIFY_SSL", "TRUE").upper() in ("TRUE", "YES", "1")

    @verify.setter
    def verify(self, val: bool) -> None:
        os.environ["CORRIDOR_API_VERIFY_SSL"] = "1" if val else "0"

    @property
    def ssl_certificate(self) -> str | None:
        certificate = self.get_value("CORRIDOR_API_SSL_CERTIFICATE", "")
        if certificate.upper() in ("", "NONE"):
            return None
        return certificate

    @ssl_certificate.setter
    def ssl_certificate(self, val: str | None) -> None:
        if val in ("", None):
            os.environ.pop("CORRIDOR_API_SSL_CERTIFICATE", None)
        else:
            os.environ["CORRIDOR_API_SSL_CERTIFICATE"] = val

    @property
    def ssl_private_key(self) -> str:
        pkey = self.get_value("CORRIDOR_API_SSL_PRIVATE_KEY", "")
        if pkey.upper() in ("", "NONE"):
            return None
        return pkey

    @ssl_private_key.setter
    def ssl_private_key(self, val: str | None) -> None:
        if val in ("", None):
            os.environ.pop("CORRIDOR_API_SSL_PRIVATE_KEY", None)
        else:
            os.environ["CORRIDOR_API_SSL_PRIVATE_KEY"] = val


class ApiAuth(AuthBase):
    def __init__(self, *args, **kwargs) -> None:
        self.user_api_key = None
        self.workspace = None
        super().__init__(*args, **kwargs)

    def init_user(self, user_api_key: str, workspace: str = "corridor") -> None:
        self.user_api_key = user_api_key
        self.workspace = workspace

    def __call__(self, req: requests.PreparedRequest) -> requests.PreparedRequest:
        if self.user_api_key is None:
            # Prints that the session is not initialised
            whoami()
        req.headers["x-api-key"] = self.user_api_key
        if self.workspace is not None:
            req.headers["x-workspace-name"] = self.workspace
        return req


class ApiSession(requests.Session):
    def set_config(self, config: SessionConfig) -> None:
        self._config = config

        # One way SSL to handle https://
        self.verify = self._config.verify
        if self.verify is False:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Client-side SSL for security (2-way SSL)
        if self._config.ssl_private_key is None:
            self.cert = self._config.ssl_certificate
        else:
            self.cert = (self._config.ssl_certificate, self._config.ssl_private_key)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_config(SessionConfig())

        # Set custom user agent - Good to have as it shows up in access logs
        self.headers["user-agent"] = f"genguardx/{importlib_metadata.version('genguardx')}"
        self.auth = ApiAuth()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        url = ujoin(self._config.api_url, url)

        if "timeout" not in kwargs:
            timeout = SessionConfig.get_value("CORRIDOR_API_TIMEOUT", "300")
            try:
                kwargs["timeout"] = int(timeout)
            except (TypeError, ValueError):
                kwargs["timeout"] = 300

        return super().request(method, url, **kwargs)


class NetworkSession:
    def __init__(self) -> None:
        self.session = ApiSession()

    def response(
        self,
        url: str,
        *,
        out: str = "json",
        params: dict | None = None,
        json: dict | None = None,
        data: dict | None = None,
        files: dict | None = None,
    ) -> str | bytes | dict:
        """
        :param url:    The URL to call
        :param out:    Get the response of the API as:
                       - json: JSON data parsed as a dictionary
                       - bin: Binary data as bytes
                       - text: Text format as a string
        :param params: The query params to use when making the API call
        :param json:   The JSON payload to use when making the API call
        :param data:   The multipart form data to be sent
        :param files:   The files to be sent
        """
        if json is not None:
            assert files is None, "`files` and `json` cannot be provided together"
            assert data is None, "`data` and `json` cannot be provided together"
        if files is not None or data is not None:
            assert json is None, "`json` cannot be provided along with `files` or `data`"

            if data is not None and files is None:  # Get files from the data

                def _extract_files(data: dict | list | tuple, path: str = "") -> tuple[dict, dict]:
                    newjson, newfiles = data, {}
                    if isinstance(data, (list, tuple)):
                        newjson = []
                        for iitem, item in enumerate(data):
                            subpath = f"{path}[{iitem}]"
                            if isinstance(item, bytes):
                                newfiles[subpath] = item
                            else:
                                innerjson, innerfiles = _extract_files(item, subpath)
                                newfiles = {**newfiles, **innerfiles}
                                newjson.append(innerjson)
                    elif isinstance(data, dict):
                        newjson = {}
                        for key, val in data.items():
                            subpath = f"{path}.{key}" if path else key
                            if isinstance(val, bytes):
                                newfiles[subpath] = val
                            else:
                                innerjson, innerfiles = _extract_files(val, subpath)
                                newjson[key] = innerjson
                                newfiles = {**newfiles, **innerfiles}
                    return newjson, newfiles

                json_with_files, files = _extract_files(data)
                data = {"json": json_module.dumps(json_with_files)}

        resp = self.session.request(
            "POST" if json is not None or data is not None or files is not None else "GET",
            url=url,
            params=params,
            json=json,
            data=data,
            allow_redirects=False,
            files=files,
        )

        if out == "json":
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError as err:
                raise AssertionError(f"Failed to parse JSON from response: {resp.text}") from err
        if out == "text":
            return resp.text
        if out == "bin":
            return resp.content
        raise NotImplementedError(f"Unknown out={out}")


api = NetworkSession()
