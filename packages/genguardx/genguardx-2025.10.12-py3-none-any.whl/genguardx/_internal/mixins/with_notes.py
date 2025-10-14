from __future__ import annotations

import io

from genguardx._internal.util import utils
from genguardx._internal.util.constants import AttachmentFile, URLS
from genguardx._internal.util.networking import api


class WithNotes:
    """
    Represents a class to access the Note Attachemnts which are tagged to an object.
    """

    @property
    def attached_files(self) -> list[AttachmentFile]:
        """
        Access the note attachments tagged to the object.

        :return: A list of attachments where each attachment is a dataclass having attributes
                    - name: filename
                    - content: io.BytesIO object
        """
        return [
            AttachmentFile(
                note_attachment["name"],
                io.BytesIO(api.response(utils.ujoin(URLS.ATTACHMENTS_PATH.value, note_attachment["id"]), out="bin")),
            )
            for note_attachment in self._data["noteAttachments"]
        ]
