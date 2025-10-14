from __future__ import annotations

import re
import typing as t

import pytest
import requests
import urllib3
from requests.models import Response

from genguardx._internal.util.networking import ApiSession, NetworkSession, SessionConfig


if t.TYPE_CHECKING:
    import pytest_mock
    import responses


class TestSessionConfig:
    def test_get_value_from_corridor_configs(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch.dict(
            "sys.modules",
            {
                "corridor._configs": mocker.MagicMock(CORRIDOR_API_URL="http://invalid"),
            },
        )
        assert SessionConfig.get_value("CORRIDOR_API_URL", "") == "http://invalid"

    def test_session_config_with_ssl_cert(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch.dict(
            "sys.modules",
            {
                "corridor._configs": mocker.MagicMock(CORRIDOR_API_SSL_CERTIFICATE="path/to/ssl/cert"),
            },
        )
        config = SessionConfig()
        assert config.ssl_certificate == "path/to/ssl/cert"

    def test_session_config_with_ssl_key(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch.dict(
            "sys.modules",
            {
                "corridor._configs": mocker.MagicMock(CORRIDOR_API_SSL_PRIVATE_KEY="path/to/ssl/key"),
            },
        )
        config = SessionConfig()
        assert config.ssl_private_key == "path/to/ssl/key"


class TestApiSession:
    def test_warnings_disabled_on_ssl_no_verify(self, mocker: pytest_mock.MockerFixture) -> None:
        disable_warnings = mocker.patch("urllib3.disable_warnings")

        api = ApiSession()
        api.set_config(mocker.MagicMock(verify=False))

        disable_warnings.assert_called_once_with(urllib3.exceptions.InsecureRequestWarning)

    @pytest.mark.parametrize("ssl_configs", [("/path/to/cert", None), ("/path/to/cert", "/path/to/key")])
    def test_ssl_settings(self, mocker: pytest_mock.MockerFixture, *, ssl_configs: t.Iterable[str | None]) -> None:
        cert, key = ssl_configs

        api = ApiSession()
        api.set_config(mocker.MagicMock(verify=True, ssl_certificate=cert, ssl_private_key=key))

        if key is None:
            assert api.cert == cert
        else:
            assert api.cert == (cert, key)

    def test_request_explicit_timeout(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch.dict("os.environ", {"CORRIDOR_API_URL": "http://invalid"})
        session_request = mocker.patch("requests.Session.request")

        api = ApiSession()
        api.request("GET", "/meta.json", timeout=999)
        session_request.assert_called_once_with("GET", "http://invalid/meta.json", timeout=999)

    def test_request_invalid_timeout_config(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch.dict("os.environ", {"CORRIDOR_API_URL": "http://invalid", "CORRIDOR_API_TIMEOUT": "invalid-int"})
        session_request = mocker.patch("requests.Session.request")

        api = ApiSession()
        api.request("GET", "/meta.json")
        session_request.assert_called_once_with("GET", "http://invalid/meta.json", timeout=300)


class TestNetworkSession:
    def test_api_response_server_error(
        self,
        mocker: pytest_mock.MockerFixture,
        responses: responses.RequestsMock,
    ) -> None:
        mocker.patch.dict("os.environ", {"CORRIDOR_API_URL": "http://invalid"})
        responses.add(responses.GET, "http://invalid/meta.json", status=503)

        api = NetworkSession()

        with pytest.raises(
            requests.HTTPError,
            match=r"Server Error: For GET at http://invalid/meta.json\nGot Status Code = 503",
        ):
            api.response("meta.json")

    def test_api_response_invalid_json(
        self,
        mocker: pytest_mock.MockerFixture,
        responses: responses.RequestsMock,
    ) -> None:
        mocker.patch.dict("os.environ", {"CORRIDOR_API_URL": "http://invalid"})
        responses.add(responses.GET, "http://invalid/info", status=200, body=b"aaa")

        api = NetworkSession()

        with pytest.raises(requests.exceptions.JSONDecodeError):
            api.response("info")

    def test_api_response_invalid_output_format(
        self,
        mocker: pytest_mock.MockerFixture,
        responses: responses.RequestsMock,
    ) -> None:
        mocker.patch.dict("os.environ", {"CORRIDOR_API_URL": "http://invalid"})
        responses.add(responses.GET, "http://invalid/meta.json", status=200)

        api = NetworkSession()

        with pytest.raises(NotImplementedError, match="Unknown out"):
            api.response("meta.json", out="bytes")

    def test_get_error_message_unable_to_retrieve_text(self, mocker: pytest_mock.MockerFixture) -> None:
        resp = Response()
        resp.status_code = requests.codes.i_am_a_teapot
        resp.request = mocker.Mock(method="GET")
        resp.url = "http://invalid/teapot"
        # Expected bytes, we are trying to reproduce a decoding issue so that response.text cannot be retrieved
        resp._content = 101

        err_msg = NetworkSession._get_response_error_message(resp)
        assert re.search(r".*Got response:\s*$", err_msg)
