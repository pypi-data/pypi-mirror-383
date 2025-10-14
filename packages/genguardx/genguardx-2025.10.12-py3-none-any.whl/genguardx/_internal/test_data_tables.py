from __future__ import annotations

import re
import typing as t

import pytest
from responses.matchers import query_param_matcher

from corridor_api import AppUser
from corridor_api.db.models.data_column_type import DataColumnType
from corridor_api_test import seed
from genguardx._internal.data_tables import DataColumn, DataTable
from genguardx._internal.util.constants import URLS
from genguardx._internal.util.utils import ujoin
from genguardx_test.helpers import api_url, get_spark


if t.TYPE_CHECKING:
    import fs.base
    import pytest_mock
    import responses

    from corridor_api.db.models import SQLAlchemy


class TestDataColumn:
    def test_data_column_init_with_alias(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(ujoin(URLS.DATA_TABLE_PATH.value, "columns")),
            json={"result": [{"id": 1, "alias": "fico_range_low"}]},
            match=[query_param_matcher({"alias": "fico_range_low"}, strict_match=False)],
        )

        column = DataColumn(alias="fico_range_low")
        assert column.alias == "fico_range_low"

    def test_data_column_with_table_alias(
        self, responses: responses.RequestsMock, mocker: pytest_mock.MockerFixture
    ) -> None:
        mocker.patch("genguardx._internal.mixins.with_fields.WithFields._set_custom_fields")
        responses.add(
            responses.GET,
            api_url(URLS.DATA_TABLE_PATH.value),
            json={"result": [{"id": 1, "alias": "app"}]},
            match=[query_param_matcher({"alias": "app"}, strict_match=False)],
        )
        responses.add(
            responses.GET,
            api_url(ujoin(URLS.DATA_TABLE_PATH.value, "columns")),
            json={"result": [{"id": 1, "alias": "fico_range_low"}]},
            match=[query_param_matcher({"alias": "fico_range_low", "dataTableId": "1"}, strict_match=False)],
        )
        column = DataColumn("app", alias="fico_range_low")
        assert column.alias == "fico_range_low"


class TestDataTable:
    def test_data_table_init_with_alias(
        self, mocker: pytest_mock.MockerFixture, responses: responses.RequestsMock
    ) -> None:
        mocker.patch("genguardx._internal.mixins.with_fields.WithFields._set_custom_fields")
        responses.add(
            responses.GET,
            api_url(URLS.DATA_TABLE_PATH.value),
            json={"result": [{"id": 1, "alias": "app"}]},
            match=[query_param_matcher({"alias": "app"}, strict_match=False)],
        )

        assert DataTable("app").alias == "app"

    def test_attribute_deprecation_tables(self, mocker: pytest_mock.MockerFixture) -> None:
        datatable_all_mocked = mocker.patch("genguardx._internal.data_tables.DataTable.all", return_value=[])

        with pytest.warns(
            DeprecationWarning,
            match=re.escape(
                "`.tables` is deprecated and will be removed in the next version. Please use `.all()` instead"
            ),
        ):
            _ = DataTable.tables
        datatable_all_mocked.assert_called_once()

    def test_to_spark(self, sa_session: SQLAlchemy, data_lake: str, fs: fs.base.FS) -> None:
        spark = get_spark()
        df = spark.createDataFrame(
            [["1", 700, 10000], ["2", 750, 20000], ["3", 800, 30000]], ["appId", "fico", "income"]
        )
        path = data_lake.format("df")
        df.write.parquet(path)
        path = path[len("file://") :]
        app_table = seed.create_data_table("app", location=path, created_by="master")
        seed.create_data_column("appId", DataColumnType.Values.STRING, app_table)
        seed.create_data_column("fico", DataColumnType.Values.INT, app_table)
        seed.create_data_column("income", DataColumnType.Values.INT, app_table)

        with AppUser("master", "corridor"):
            # This is equivalent to a SQL except
            assert DataTable(id=app_table.id).to_spark().subtract(df).rdd.isEmpty()
