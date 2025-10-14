from __future__ import annotations

import typing as t

from genguardx._internal.util import utils
from genguardx._internal.util.constants import Objects, URLS, WorkflowStatus
from genguardx._internal.util.networking import api


T = t.TypeVar("T", bound="Searchable")


class Searchable:
    """
    Represents a class that has searching capabilities
    """

    _available_filter_names: set[str] = set()
    FILTER_API_PARAMETER_MAPPING = {
        "status": "statuses",
        "permissible_purpose": "permissibleTags",
        "type": "types",
        "group": "group",
        "contains": "keyword",
        "object_type": "objectTypes",
    }

    _str_filters = {"name", "alias", "contains", "type"}

    @utils.classproperty
    def _possible_filter_values__status(cls) -> set[str]:
        return {i.value for i in WorkflowStatus}

    @utils.classproperty
    def _possible_filter_values__permissible_purpose(cls) -> set[str]:
        # FIXME: Can we reduce the API calls ?
        return {item["name"] for item in api.response(URLS.PERMISSIBLE_PURPOSE_PATH.value)["result"]}

    @utils.classproperty
    def _possible_filter_values__group(cls) -> set[str]:
        return {
            item["name"]
            for item in api.response(URLS.GROUP_PATH.value, params={"object_type": cls._object_type})["result"]
        }

    @utils.classproperty
    def _possible_filter_values__object_type(cls) -> set[str]:
        return {Objects.display_name(obj) for obj in Objects}

    @utils.classproperty
    def _display_name_mapping__object_type(cls) -> dict[str, str]:
        return {v: k.value for k, v in Objects.name_mapping().items()}

    @classmethod
    def all(cls: T, **filters) -> list[T]:
        # FIXME: generate dynamic docstring
        """
        Search the platforms using filters

        :param filters: key-value pair of the searching criterion
                        if no searching criterion applied, all() returns all the objects registered for the class
        :return:        A list of objects that fit the searching criterion

        Examples(Using DataElement as example, it applies the same for all other searchable Entities):
        Returns all the DataElement registered on the platform
        >>> DataElement.all()

        Returns all the Draft DataElement registered on the platform
        >>> DataElement.all(status='Draft')

        Returns all the Numerical and String DataElements registered on the platform
        >>> DataElement.all(type=['Numerical', 'String'])

        Returns all the DataElements registered on the platform that contains the word `annual`
        in the name, alias, description etc
        >>> DataElement.all(contains='annual')

        Note: if unsure of what are the available filter values, you can input a arbitrary value,
        the error message will provide information on the valid values to search for
        Example: Search for `status='garbage'`
        >>> DataElement.all(status='garbage')
        AssertionError: Found invalid filter value(s): {'garbage'} for filter: status.
        Expecting filter value to be in {'Draft', 'Rejected', 'Approved', 'Pending Approval', 'Shadow', 'Active'}
        """

        invalid_filters = filters.keys() - cls._available_filter_names
        if invalid_filters:
            raise TypeError(
                f"`{cls.__name__}.all()` got unexpected filter(s): {', '.join(invalid_filters)}. "
                f"Expected filters to be in: {cls._available_filter_names}"
            )
        api_filters = {}
        for filter_, value in filters.items():
            if filter_ in cls._str_filters:
                assert isinstance(value, str), (
                    f"Found invalid filter value type: {type(value).__name__} for filter: {filter_}. "
                    f"Expecting filter value to be string type"
                )
            else:
                possible_values = getattr(cls, f"_possible_filter_values__{filter_}", None)
                assert possible_values is not None, f"No possible values found for filter: {filter_}"

                if not isinstance(value, list):
                    value = [value]
                invalid_filter_values = set(value) - possible_values
                assert not invalid_filter_values, (
                    f"Found invalid filter value(s): {', '.join(invalid_filter_values)} for filter: {filter_}. "
                    f"Expecting filter value to be in {possible_values}"
                )

                # filter values provided by user are the values displayed in UI, which might differ with
                # our internal value. mapping display_name to internal name if any
                display_name_to_internal = getattr(cls, f"_display_name_mapping__{filter_}", {})
                value = [display_name_to_internal.get(val, val) for val in value]

            api_filters.update({cls.FILTER_API_PARAMETER_MAPPING.get(filter_, filter_): value})

        # FIXME: Use Versionable mixin to identify the ones need singleVersionOnly filter
        if cls.__name__ != "DataTable":
            api_filters["singleVersionOnly"] = True

        return [cls._from_data(data=item) for item in cls._get_data(**api_filters)]
