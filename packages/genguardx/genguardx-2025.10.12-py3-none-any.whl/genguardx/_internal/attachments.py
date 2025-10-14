from __future__ import annotations

from genguardx._internal.mixins.auditable import Auditable
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import URLS
from genguardx._internal.util.networking import api


class Attachment(ApiBase, Auditable):
    """
    Represents an Attachment that is registered.
    :param id:      The ID of the attachment to fetch.
    The following properties of the Attachment can be accessed:
    - id: integer
        The ID that is unique to every Attachment.
    - location: str
        The location of this Attachment.
    """

    _LIST_URL = URLS.ATTACHMENTS_PATH.value

    def __init__(self, id: int) -> None:
        self.data = api.response(f"/api/v1/attachments/{id}", out="bin")
