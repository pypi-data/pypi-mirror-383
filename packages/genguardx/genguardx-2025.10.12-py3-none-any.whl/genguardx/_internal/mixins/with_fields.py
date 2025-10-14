from __future__ import annotations


# class FieldValues:
#     def __init__(self, parent: ApiBase) -> None:
#         self.parent = parent

#     @functools.cached_property
#     def _custom_fields(self) -> dict[str, t.Any]:
#         # NOTE: Any custom_field in the UI of an object should be available in corridor-python package also
#         # Hence assigning 'None' to all custom field which is configured for the object type but not assigned a
#         # value. Thus we can avoid getting 'AttributeError' for these custom fields which is a undesirable UX.
#         all_custom_fields = {
#             field.alias for field in CustomField.all(object_type=Objects.display_name(type(self.parent)._object_type))
#         }
#         custom_fields_with_value = set()
#         retval = {}

#         # Setting values for all existing custom field
#         for field in self.parent._data["entityFields"]:
#             alias = field["field"]["alias"]
#             field_type = field["field"]["fieldType"]

#             prop_value = None
#             if field_type == FieldType.SINGLE_FILE.value:
#                 attachment_name = field["attachment"]["name"]
#                 bytes_io = io.BytesIO(
#                     api.response(utils.ujoin(URLS.ATTACHMENTS_PATH.value, field["attachment"]["id"]), out="bin")
#                 )
#                 prop_value = AttachmentFile(attachment_name, bytes_io)
#             # FIXME: Use field_value to simplify the logic?
#             elif field_type in (
#                 FieldType.SHORT_TEXT.value,
#                 FieldType.SINGLE_SELECT.value,
#                 FieldType.NUMBER.value,
#             ):
#                 if len(field["shortTextValues"]) > 1:
#                     raise AssertionError("Expected length of values to be 1 or less")
#                 if len(field["shortTextValues"]) == 1:
#                     if field_type == FieldType.NUMBER.value:
#                         prop_value = float(field["shortTextValues"][0]["value"])
#                     else:
#                         prop_value = field["shortTextValues"][0]["value"]
#                 else:
#                     prop_value = None
#             elif field_type == FieldType.LONG_TEXT.value:
#                 prop_value = field["longTextValue"]["value"]
#             elif field_type == FieldType.MULTI_SELECT.value:
#                 prop_value = [val["value"] for val in field["shortTextValues"]]
#             else:
#                 # field_type is FieldType.DATE_TIME
#                 prop_value = field["datetimeValue"]["value"]

#             retval[alias] = prop_value
#             custom_fields_with_value.add(alias)

#         # Setting all the unassigned custom_field as None
#         retval.update(dict.fromkeys(all_custom_fields - custom_fields_with_value))
#         return retval

#     @functools.cached_property
#     def __doc__(cls) -> str:
#         fields_docstring = ""
#         try:
#             configured_fields = CustomField.all(object_type=Objects.display_name(cls._object_type))
#             fields_docstring += textwrap.dedent(
#                 """
#                 Admin configured fields are:
#                 """
#             )
#             for field in configured_fields:
#                 fields_docstring += textwrap.indent(
#                     textwrap.dedent(
#                         f"""
#                         - {field.alias}: dataclasses.dataclass | float | str
#                             {field.description}
#                         """
#                     ),
#                     " " * 4,
#                 )
#             fields_docstring += textwrap.dedent(
#                 """
#                 Each field is an attribute of the object, with value as,
#                     - for file attachments, a dataclass having attributes
#                         - name: filename
#                         - content: io.BytesIO object
#                     - a floating point value for field type "Number"
#                     - a string in all other cases
#                 """
#             )
#         except Exception:
#             # FIXME: The docstring is appended here but maybe it should be replaced
#             #        otherwise we might have a half written docstring for fields
#             fields_docstring += textwrap.dedent(
#                 """
#                 Admin configured fields might also be available.
#                 """
#             )
#         return fields_docstring

#     def __getattr__(self, field_alias: str) -> int | float | str | datetime.datetime:
#         return self._custom_fields[field_alias]


class WithFields:
    """
    Represents a class to access the Fields and their Attachments which are tagged to an object.
    """

    def _set_custom_fields(self) -> None:
        pass
        # self.fields = FieldValues(self)
