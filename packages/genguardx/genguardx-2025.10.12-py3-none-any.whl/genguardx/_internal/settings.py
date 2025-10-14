from __future__ import annotations

import enum
import typing as t

import dateutil.parser

from genguardx._internal.mixins.auditable import Auditable
from genguardx._internal.mixins.searchable import Searchable
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects, URLS


if t.TYPE_CHECKING:
    import datetime


class FieldType(enum.Enum):
    # Allows users to enter any combination of letters and numbers.
    SHORT_TEXT = "ShortText"
    # Allows users to enter Text value.
    LONG_TEXT = "LongText"
    # Allows users to select a value from a list you define.
    SINGLE_SELECT = "SingleSelect"
    # Allows users to select multiple values from a list you define.
    MULTI_SELECT = "MultiSelect"
    # Allows users to select a single File
    SINGLE_FILE = "SingleFile"
    # Allows users to select multiple Files
    MULTIPLE_FILES = "MultipleFiles"
    # Allows users to select DateTime Value
    DATE_TIME = "DateTime"
    # Allows users to select Number Value
    NUMBER = "Number"


class CustomField(ApiBase, Auditable, Searchable):
    """
    Represents a Custom Field that is registered.

    :param name:                 The name of the Custom Field to fetch.
    :param alias:                The alias of the Custom Field to fetch.
    :param id:                   The ID of the Custom Field to fetch.

    The following properties of the Custom Field can be accessed:
    - name: string
       The name of the Custom Field registered.
    - description: string
       The description registered for the Custom Field.
    - id: integer
       The ID that is unique to every Custom Field.
    - is_mandatory: bool
       Whether it is mandatory or not to provide an attachment for this Custom Field during object registration
    - created_by: string
       The username of the user that created the Custom Field.
    - created_date: datetime
       The date that this Custom Field was created.
    - last_modified_by: string
       The username of the Custom Field that last modified the item.
    - last_modified_date: datetime
       The date when the Custom Field was last modified.
    - object_types: list[string]
       The list of object types for which this Custom Field will be shown e.g. DataElement, Feature etc.
    """

    _object_type = Objects.FIELD.value
    _LIST_URL = URLS.FIELD_PATH.value
    _exposed_properties = {
        "id",
        "name",
        "alias",
        "description",
        "is_mandatory",
        "field_type",
        "placeholder_text",
        "help_text",
        "sort_order",
        "is_searchable_field",
        "is_access_control_field",
    }
    _available_filter_names = {"name", "alias", "contains", "object_type"}

    def __init__(self, name: str | None = None, alias: str | None = None, id: int | None = None) -> None:
        filters: dict[str, t.Any] = {}
        if id is not None:
            filters["ids"] = id
        if name is not None:
            filters["name"] = name
        if alias is not None:
            filters["alias"] = alias
        self._data = self._get_data(one=True, **filters)

    @property
    def object_types(self) -> list[str]:
        return [field_obj_type["objectType"] for field_obj_type in self._data["objectTypes"]]

    @property
    def default_value(self) -> float | str | list[str] | None:
        if (
            self.field_type in (FieldType.NUMBER.value, FieldType.SHORT_TEXT.value, FieldType.SINGLE_SELECT.value)
            and len(self._data["defaultShortTextValues"]) > 0
        ):
            value = self._data["defaultShortTextValues"][0]["defaultValue"]
            return float(value) if self.field_type == FieldType.NUMBER.value else value

        if self.field_type == FieldType.LONG_TEXT.value and self._data["defaultLongTextValue"] is not None:
            return self._data["defaultLongTextValue"]["defaultValue"]

        if self.field_type == FieldType.MULTI_SELECT.value and len(self._data["defaultShortTextValues"]) > 0:
            return [default["defaultValue"] for default in self._data["defaultShortTextValues"]]

        return None

    @property
    def options(self) -> list[str] | None:
        if self.field_type in (FieldType.SINGLE_SELECT.value, FieldType.MULTI_SELECT.value):
            return [option["optionValue"] for option in self._data["optionShortTextValues"]]
        return None

    def __str__(self) -> str:
        return f'<{type(self).__name__} name="{self.name}">'


class User(ApiBase, Auditable, Searchable):
    """
    Represents a User that is registered.

    :param username:             The username of the User to fetch.
    :param id:                   The ID of the User to fetch.

    The following properties of the User can be accessed:
    - username: string
       The username of the User as registered.
    - id: integer
       The ID that is unique to every User.
    - created_by: string
       The username of the user that created the `User` object on the platform.
    - created_date: datetime
       The date that this User was created.
    - last_modified_by: string
       The username of the user that last modified the `User` object on the platform.
    - last_modified_date: datetime
       The date when the User was last modified.
    - last_login_date: datetime
       The date when the User had logged in last time.
    - first_name: string
       The first name of the User as registered.
    - last_name: string
       The last name of the User as registered.
    - department: string
       The department of the User as registered.
    - email: string
       The email of the User as registered.
    - is_active : bool
       The boolean indicating if the User is activated on the platform or not.
    - user_roles: list[dict]
       The list of dictionaries, where each dictionary has information about the role assigned
       to the user in a workspace.
    """

    _object_type = Objects.USER.value
    _LIST_URL = URLS.USER_PATH.value
    _exposed_properties = {"id", "email", "first_name", "last_name", "is_active", "department"}
    _available_filter_names = {"username", "contains"}
    _str_filters = {"username", "alias", "contains"}
    FILTER_API_PARAMETER_MAPPING = {"contains": "keyword", "username": "name"}

    def __init__(self, username: str | None = None, id: int | None = None) -> None:
        filters: dict[str, t.Any] = {}
        if id is not None:
            filters["ids"] = id
        if username is not None:
            filters["name"] = username
        self._data = self._get_data(one=True, **filters)

    @property
    def user_roles(self) -> list[dict[str, str]]:
        return self._data["rolesWithWorkspace"]

    @property
    def username(self) -> str:
        return self._data["name"]

    @property
    def last_login_date(self) -> datetime.datetime | None:
        last_login_date_data = self._data["lastLoginDate"]
        if last_login_date_data is not None:
            return dateutil.parser.parse(last_login_date_data)
        return None

    def __str__(self) -> str:
        return f'<{type(self).__name__} username="{self.username}">'


class PlatformSetting(ApiBase, Auditable):
    """
    Represents a Platform Setting object

    The following properties of the Platform Setting can be accessed:

    - id: integer
       The ID of the Platform Setting
    - created_by: string
       The username of the user that created the `Platform Setting` object on the platform.
    - created_date: datetime
       The date that this Platform Setting was created.
    - last_modified_by: string
       The username of the user that last modified the `Platform Setting` object on the platform.
    - last_modified_date: datetime
       The date when the Platform Setting was last modified.
    - max_file_size: integer
        The max file size that can be uploaded on the platform.
    - allowed_file_extensions: list[str]
        The file extensions that are allowed on the platform for note and log attachments.
    - allowed_python_imports: list[str]
        The python libraries and packages that are allowed in the definition of an object.
    """

    _object_type = Objects.PLATFORM_SETTING.value
    _LIST_URL = URLS.PLATFORM_SETTING_PATH.value
    _exposed_properties = {"id"}

    def __init__(self) -> None:
        self._data = self._get_data()

    @property
    def max_file_size(self) -> int:
        return self._data["maxContentLength"]

    @property
    def max_job_records(self) -> int:
        return self._data["maxJobRecords"]

    @property
    def allowed_file_extensions(self) -> list[str] | None:
        allowed_file_extensions = self._data["allowedFileExtensions"]
        if isinstance(allowed_file_extensions, str):
            return [ext.strip() for ext in allowed_file_extensions.split(",") if ext.strip() != ""]
        return None

    @property
    def allowed_python_imports(self) -> list[str] | None:
        allowed_python_imports = self._data["allowedPythonImports"]
        if isinstance(allowed_python_imports, str):
            return [imp.strip() for imp in allowed_python_imports.split(",") if imp.strip() != ""]
        return None

    def __str__(self) -> str:
        return f"<{type(self).__name__}>"
