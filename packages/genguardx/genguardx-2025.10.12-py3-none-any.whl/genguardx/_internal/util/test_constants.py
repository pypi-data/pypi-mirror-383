from __future__ import annotations

from enum import Enum, auto, unique

import pytest

from genguardx._internal.util.constants import Operator, StrEnum


class TestStrEnum:
    def test_too_many_arguments(self) -> None:
        with pytest.raises(TypeError, match="too many arguments for str"):

            class Invalid(StrEnum):
                x = "a", "b", "c", "d"

    def test_first_arg_not_string(self) -> None:
        with pytest.raises(TypeError, match="is not a string"):

            class Invalid(StrEnum):
                x = 0

    def test_second_arg_not_string(self) -> None:
        with pytest.raises(TypeError, match="encoding must be a string"):

            class Invalid(StrEnum):
                x = "corridor", 0

    def test_third_arg_not_string(self) -> None:
        with pytest.raises(TypeError, match="errors must be a string"):

            class Invalid(StrEnum):
                x = "corridor", "utf-8", 123

    def test_automatic_values(self) -> None:
        class Ordinal(StrEnum):
            NORTH = auto()
            SOUTH = auto()
            EAST = auto()
            WEST = auto()

        assert [o.value for o in Ordinal] == ["north", "south", "east", "west"]

    def test_enum_str_override(self) -> None:
        class MyStrEnum(Enum):
            def __str__(self) -> str:
                return "MyStr"

        class Test1Enum(int, MyStrEnum):
            One = 1
            Two = 2

        assert str(Test1Enum.One) == "MyStr"

        class Test2Enum(MyStrEnum):
            One = 1
            Two = 2

        assert str(Test2Enum.One) == "MyStr"

    def test_strenum_from_scratch(self) -> None:
        class Greek(str, Enum):
            pi = "Pi"
            tau = "Tau"

        assert Greek.pi < Greek.tau

    def test_strenum_inherited_methods(self) -> None:
        class Greek(StrEnum):
            pi = "Pi"
            tau = "Tau"

        assert Greek.pi < Greek.tau
        assert Greek.pi.upper() == "PI"

    def test_multiple_inherited_mixin(self) -> None:
        @unique
        class Decision1(StrEnum):
            REVERT = "REVERT"
            REVERT_ALL = "REVERT_ALL"
            RETRY = "RETRY"

        class MyEnum(StrEnum):
            pass

        @unique
        class Decision2(MyEnum):
            REVERT = "REVERT"
            REVERT_ALL = "REVERT_ALL"
            RETRY = "RETRY"

    def test_strenum(self) -> None:
        class GoodStrEnum(StrEnum):
            one = "1"
            two = "2"
            three = b"3", "ascii"
            four = b"4", "latin1", "strict"

        assert GoodStrEnum.one == "1"
        assert str(GoodStrEnum.one) == "1"
        assert GoodStrEnum.one == str(GoodStrEnum.one)
        assert GoodStrEnum.one == f"{GoodStrEnum.one}"


class TestOperator:
    def test_get_unsupported_operator(self) -> None:
        with pytest.raises(ValueError, match="Unsupported Operator found"):
            Operator.get("less_than")
