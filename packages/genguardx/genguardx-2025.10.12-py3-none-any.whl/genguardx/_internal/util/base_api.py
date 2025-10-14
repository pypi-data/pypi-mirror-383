from __future__ import annotations

import html
import typing as t

from genguardx._internal.util import utils
from genguardx._internal.util.networking import api
from genguardx.exceptions import NotFound


class ApiBase:
    """
    Base for any Api resource that is being referred to.
    """

    _LIST_URL: str | None = None
    _exposed_properties: set[str] = set()
    _default_filters: dict[str, t.Any] = {}

    def __init__(self) -> None:
        self._data = {}

    @classmethod
    def _from_data(cls, **private_attrs) -> ApiBase:
        """
        Alternative constructor: initialize object with existing attributes/data instead of making api call
        """
        # get object of class `cls` without calling init()
        # Ref: https://stackoverflow.com/questions/6383914/is-there-a-way-to-instantiate-a-class-without-calling-init
        obj = cls.__new__(cls)

        for attr_name, attr_value in private_attrs.items():
            setattr(obj, f"_{attr_name}", attr_value)
        return obj

    @classmethod
    def _get_data(cls, *, one: bool = False, **kwargs) -> dict | list[dict]:
        """
        Fetch the resource related to this class. Can return a single item or a list of items of this resource.

        :param one:      Whether to return only 1 item or multiple items in a list.
                         If the data fetched has 0 records or >1 record, raise appropriate errors.
        :param **kwargs: Filters to use when querying the resource.
        """
        kwargs.update(cls._default_filters)
        retval = api.response(cls._LIST_URL, params=kwargs)["result"]
        if one:
            if len(retval) > 1:
                filters_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
                print(f"WARN: {len(retval)} {cls.__name__}(s) with {filters_str} were found. Choosing first.")
            try:
                return retval[0]
            except IndexError:
                filters_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
                raise NotFound(
                    f"No {cls.__name__} found with {filters_str}. "
                    f"Ensure the {cls.__name__} exists and you have access to it.",
                    filters=kwargs,
                    name=cls,
                )
        return retval

    def __getattr__(self, key: str) -> t.Any:  # noqa: ANN401 -- return type can vary based on the attribute
        # Override the __getattr__ to dynamically fetch the properties in the underlying `self._data` that
        # are mentioned in the exposed properties.
        if key in self._exposed_properties:
            return self._data[utils.camelcase(key)]
        raise AttributeError(f"{type(self).__name__} object has no attribute {key}")

    def __setattr__(self, key: str, value: t.Any) -> None:  # noqa: ANN401 -- type(value) can vary
        # Override the __setattr__, so that user doesn't have the illusion of being able to set attributes
        # in self._exposed_properties
        if key in self._exposed_properties:
            raise AttributeError("can't set attribute")
        super().__setattr__(key, value)

    def __dir__(self) -> t.Iterable[str]:
        # We override the __dir__ to make it simpler for users to introspect things.
        #  - _exposed_properties and __getattr__() - expose some values from the underlying data. Make them visible.
        dir_exposed = super().__dir__()
        return dir_exposed + list(self._exposed_properties)

    def __repr__(self) -> str:
        return str(self)

    def _repr_html_(self) -> str:
        # Ref: https://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display
        return "<pre>" + html.escape(str(self)) + "</pre>"

    def __eq__(self, other: object) -> bool:
        return (type(self) is type(other)) and (self.id == other.id)

    # ref: https://docs.python.org/3/glossary.html#term-hashable
    def __hash__(self) -> int:
        return hash(type(self).__name__) ^ hash(self.id)
