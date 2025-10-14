from __future__ import annotations

import datetime
import typing as t

import pytest

from genguardx._internal.util import lang_utils
from genguardx._internal.util.constants import DataType


if t.TYPE_CHECKING:
    import pytest_mock


class TestLangUtils:
    @pytest.mark.parametrize("literal_type", ("Numerical", DataType.NUMERICAL))
    def test_make_literal_numerical(self, *, literal_type: str | DataType) -> None:
        assert lang_utils.make_literal(101, literal_type) == "101.0"

    @pytest.mark.parametrize("literal_type", ("DateTime", DataType.DATETIME))
    def test_make_literal_datetime(self, *, literal_type: str | DataType) -> None:
        val = datetime.datetime(year=2024, month=1, day=1)
        litval = lang_utils.make_literal(val, literal_type)

        assert litval == f'datetime.datetime.strptime("2024-01-01 00:00:00", "{lang_utils.DATE_TIME_FORMAT}")'

    def test_make_literal_invalid_literal_type(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch.object(DataType, "__new__", return_value="invalid")
        with pytest.raises(NotImplementedError, match='Unsure how to handle literal of type "invalid"'):
            lang_utils.make_literal(101, "invalid")

    @pytest.mark.parametrize("cast_type", ("Numerical", DataType.NUMERICAL))
    def test_cast_value_numerical(self, *, cast_type: str | DataType) -> None:
        assert lang_utils.cast_value(101, cast_type) == pytest.approx(101.0)

    @pytest.mark.parametrize(
        "cast_type, in_val, out_val",
        (
            ("Array[Array[Numerical]]", [[101, 102]], [[101.0, 102.0]]),
            ("Array[Array[String]]", [[101, 102], [103]], [["101", "102"], ["103"]]),
            ("Array[Array[Boolean]]", [[1, 1], [0, 1, 0]], [[True, True], [False, True, False]]),
            (
                "Array[Array[DateTime]]",
                [["2024-01-01 00:00:00"], ["2024-01-02 00:00:00", "2024-01-03 00:00:00"]],
                [
                    [datetime.datetime(2024, 1, 1, 0, 0)],
                    [datetime.datetime(2024, 1, 2, 0, 0), datetime.datetime(2024, 1, 3, 0, 0)],
                ],
            ),
            (
                "Array[Map[String, String]]",
                [{"a": 1, "b": 2, "c": 3}, {"a": 2, "b": 3, "c": 1}, {"a": 3, "b": 1, "c": 2}],
                [{"a": "1", "b": "2", "c": "3"}, {"a": "2", "b": "3", "c": "1"}, {"a": "3", "b": "1", "c": "2"}],
            ),
            (
                "Array[Struct[k: String,l: Numerical]]",
                [{"k": 1, "l": 1}, {"k": 2, "l": 2}, {"k": 3, "l": 3}],
                [{"k": "1", "l": 1.0}, {"k": "2", "l": 2.0}, {"k": "3", "l": 3.0}],
            ),
        ),
    )
    def test_cast_value_array(self, *, cast_type: str | DataType, in_val: t.Any, out_val: list) -> None:  # noqa: ANN401
        assert lang_utils.cast_value(in_val, cast_type) == out_val

    @pytest.mark.parametrize(
        "cast_type, in_val, out_val",
        (
            ("Map[Numerical, String]", {101: 1, 102: 2, 103: 3}, {101: "1", 102: "2", 103: "3"}),
            (
                "Map[String, Array[Boolean]]",
                {101: [1, 0, 1], 102: [0, 0, 1]},
                {"101": [True, False, True], "102": [False, False, True]},
            ),
            (
                "Map[String, Map[Boolean, Array[DateTime]]]",
                {"101": {True: ["2024-01-01 00:00:00"], False: ["2024-01-01 00:00:00"]}},
                {"101": {True: [datetime.datetime(2024, 1, 1, 0, 0)], False: [datetime.datetime(2024, 1, 1, 0, 0)]}},
            ),
            (
                "Map[String, Struct[k1:Boolean]]",
                {101: {"k1": True}, 102: {"k1": False}},
                {"101": {"k1": True}, "102": {"k1": False}},
            ),
        ),
    )
    def test_cast_value_map(self, *, cast_type: str | DataType, in_val: t.Any, out_val: list) -> None:  # noqa: ANN401
        assert lang_utils.cast_value(in_val, cast_type) == out_val

    @pytest.mark.parametrize(
        "cast_type, in_val, out_val",
        (
            ("Struct[k1:Numerical, k2:String]", {"k1": 1, "k2": 2}, {"k1": 1, "k2": "2"}),
            (
                "Struct[k1:String, k2:Array[Numerical]]",
                {"k1": [1, 0, 1], "k2": [100, 101, 102]},
                {"k1": "[1, 0, 1]", "k2": [100.0, 101.0, 102.0]},
            ),
            (
                "Struct[k:Map[Boolean, String]]",
                {"k": {1: "a", 0: "b"}},
                {"k": {True: "a", False: "b"}},
            ),
            (
                "Struct[k:Struct[k1:Boolean, k2:String],l:Struct[l1:Boolean, l2:String]]",
                {"k": {"k1": True, "k2": "0"}, "l": {"l1": False, "l2": "1"}},
                {"k": {"k1": True, "k2": "0"}, "l": {"l1": False, "l2": "1"}},
            ),
        ),
    )
    def test_cast_value_struct(self, *, cast_type: str | DataType, in_val: t.Any, out_val: list) -> None:  # noqa: ANN401
        assert lang_utils.cast_value(in_val, cast_type) == out_val

    def test_cast_value_invalid(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch.object(DataType, "__new__", return_value="invalid")
        with pytest.raises(NotImplementedError, match='Unsure how to handle casting to "invalid"'):
            lang_utils.cast_value(101, "invalid")
