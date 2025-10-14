from __future__ import annotations

import html
import re
import typing as t

import pytest

from genguardx._internal.util.base_api import ApiBase
from genguardx.exceptions import NotFound
from genguardx_test.helpers import api_url


if t.TYPE_CHECKING:
    import responses
    from _pytest.capture import CaptureFixture


class TestBaseAPI:
    def test_get_data_one_mutliple_results(self, responses: responses.RequestsFixure, capsys: CaptureFixture) -> None:
        class Entity(ApiBase):
            _LIST_URL = "/entity"
            _exposed_properties = {"id"}

        responses.add(responses.GET, api_url("/entity"), json={"result": [{"id": 1}, {"id": 2}]})

        entity = Entity._get_data(one=True)
        assert entity["id"] == 1
        assert re.match(r"^WARN: 2 Entity\(s\) with .* were found\. Choosing first", capsys.readouterr().out)

    def test_get_data_one_no_result(self, responses: responses.RequestsFixure) -> None:
        class Entity(ApiBase):
            _LIST_URL = "/entity"
            _exposed_properties = {"id"}

        responses.add(responses.GET, api_url("/entity"), json={"result": []})

        with pytest.raises(NotFound, match="No Entity found"):
            Entity._get_data(one=True)

    def test_ipython_repr_html(self) -> None:
        class Entity(ApiBase):
            _LIST_URL = "/entity"
            _exposed_properties = {"id", "alias"}

            def __str__(self) -> str:
                return f'<{type(self).__name__} alias="{self.alias}">'

        html_str_encoded = Entity._from_data(data={"id": 1, "alias": "ent_test"})._repr_html_()
        assert html.unescape(html_str_encoded) == '<pre><Entity alias="ent_test"></pre>'
