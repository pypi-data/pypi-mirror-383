from __future__ import annotations

import dataclasses
import typing as t
import warnings

from genguardx._internal.util import utils
from genguardx._internal.util.constants import WorkflowStatus
from genguardx._internal.util.networking import api


@dataclasses.dataclass(frozen=True)
class ShareRecord:
    id: int
    access_type: str
    shared_with: str


class Shareable:
    """
    Represents a class to access share details associated with an object.
    """

    @property
    def share_details(self) -> list[ShareRecord]:
        """
        Access share details of an object

        :returns:                       List of details related to share
        :raises NotImplementedError:    When unsupported object type is used for sharing

        Returns list of named tuples containing access_type, user associated with share.

        Each share record is a namedTuple with fields:
        - access_type: type of access like `Read` or `Write`.
        - user:        the user to which the entity is being shared.
        """
        warnings.warn(
            "`share_details` is deprecated and will be removed in the next version. It gives `user` access details. "
            "Please use `.user_accesses` instead to get `user` access details and "
            "`.role_accesses` to get `user_role` access details.",
            DeprecationWarning,
            stacklevel=1,
        )

        return self.user_accesses

    def grant_share(self, user: str, access_type: t.Literal["Read", "Write"]) -> None:
        """
        Share an object with a user based on access_type.
        A success message is printed when the access is granted to the user successfully.

        :param user:                 The name of the user to share the object with
        :param access_type:          The type of access (Write or Read) granted to the user
        :return: None
        :raises RequestApiException: When user without Write access to the object calls this function
        """
        warnings.warn(
            "`grant_share` is deprecated and will be removed in the next version. It is used to grant access to "
            "`user`. Please use `.grant_share_for_user` instead to grant access to `user` and "
            "`.grant_share_for_role` to grant access to `user_role`.",
            DeprecationWarning,
            stacklevel=1,
        )

        return self.grant_share_for_user(user, access_type)

    def revoke_share(self, user: str) -> None:
        """
        Revoke the access of a user to the object.
        A success message is printed when the user's access is revoked successfully.

        :param user:                 The name of the user to share the object with
        :return:                     None
        :raises RequestApiException: When user without Write access to the object calls this function
        """
        warnings.warn(
            "Please use `.revoke_share_for_user` instead to revoke `user` access and "
            "`.revoke_share_for_role` to revoke `user_role` access.",
            DeprecationWarning,
            stacklevel=1,
        )

        return self.revoke_share_for_user(user)

    def _entity_status_check(self, msg: str) -> None:
        if self.current_status in (WorkflowStatus.APPROVED.value, WorkflowStatus.REJECTED.value):
            raise AssertionError(msg)

    def _get_share_accessess(self, details_for: str) -> list[ShareRecord]:
        """
        Helper function to access the share details for user/user_role of an object.

        :param details_for:             The type of entity to get the access details for. Possible values:
                                            - "user" to get the access details for a user
                                            - "user_role" to get the access details for a user role

        :returns:                       List of details related to share
        :raises NotImplementedError:    When unsupported object type is used for sharing

        Returns list of named tuples containing access_type, user/user_role associated with share.

        Each share record is a dataclass with fields:
        - access_type:   type of access like `Read` or `Write`.
        - shared_with:   the user/user_role to which the object is being shared.
        """
        status_check_msg = (
            f'Share details are not available as the {self._object_type} is in "{self.current_status}" status.'
        )
        self._entity_status_check(status_check_msg)

        share_details_for = "user" if details_for == "user" else "userRole"

        all_shares = api.response(
            utils.ujoin(self._LIST_URL, f"{self.id}/shares"), params={"entityId": self._data["id"]}
        )["result"]

        return [
            ShareRecord(
                id=share_record["id"],
                access_type=share_record["accessType"],
                shared_with=share_record[share_details_for]["name"],
            )
            for share_record in all_shares
            if share_record[share_details_for] is not None
        ]

    def _grant_share_for(
        self,
        access_type: t.Literal["Read", "Write"],
        share_with: t.Literal["user", "user_role"],
        share_with_value: str,
    ) -> None:
        """
        Helper function to grant access to a user/user role.
        A success message is printed when the access is granted to the user/user_role successfully.

        :param access_type:      The type of access (Write or Read) granted to the user
        :param share_with:       The type of entity to share the access with. Possible values:
                                    - "user" to share the access with a user
                                    - "user_role" to share the access with a user role
        :param share_with_value: The actual value with who the object has to be shared with. It should be:
                                    - the name of the user if `share_with=user`
                                    - the name of the user role if `share_with=user_role`
        :return: None
        :raises RequestApiException: When user/user_role without Write access to the object calls this function.
        """
        status_check_msg = f'Cannot share {self._object_type} in "{self.current_status}" status.'
        self._entity_status_check(status_check_msg)

        payload = {
            "entityId": self._data["id"],
            "entityType": self._object_type,
            "accessType": access_type,
        }
        if share_with == "user":
            payload["userId"] = share_with_value
            existing_shares = self.user_accesses
        else:  # "user_role"
            payload["userRoleId"] = share_with_value
            existing_shares = self.role_accesses

        existing_share = next(iter(share for share in existing_shares if share.shared_with == share_with_value), None)

        if existing_share is not None:
            payload["id"] = existing_share.id

        api.response(utils.ujoin(self._LIST_URL, f"{self.id}/shares"), json=payload)
        print(f'Shared {self._object_type} with {share_with} "{share_with_value}" with "{access_type}" access.')

    def _revoke_share_for(self, revoke_for: t.Literal["user", "user_role"], revoke_for_value: str) -> None:
        """
        Helper function to revoke access for a user/user role.
        A success message is printed when the user's or user_role's access is revoked successfully.

        :param revoke_for:       The type of entity to revoke the access for. Possible values:
                                    - "user" to revoke the access for a user
                                    - "user_role" to revoke the access for a user role
        :param revoke_for_value: The actual value for who the access has to be revoked. It should be:
                                    - the name of the user if `revoke_for=user`
                                    - the name of the user role if `revoke_for=user_role`
        :return: None
        :raises RequestApiException: When user/user_role without Write access to the object calls this function.
        """

        status_check_msg = f'Cannot revoke the access as the {self._object_type} is in "{self.current_status}" status.'
        self._entity_status_check(status_check_msg)

        existing_shares = self.user_accesses if revoke_for == "user" else self.role_accesses

        existing_share = next(iter(share for share in existing_shares if share.shared_with == revoke_for_value), None)
        if existing_share is None:
            raise AssertionError(f'There are no accesses to be revoked for {revoke_for} "{revoke_for_value}"')

        api.session.delete(utils.ujoin(self._LIST_URL, f"shares/{existing_share.id}"))
        print(f"Revoked access for {existing_share.shared_with}")

    @property
    def user_accesses(self) -> list[ShareRecord]:
        """
        Access user related share details of an object

        :returns:                       List of user details related to share
        :raises NotImplementedError:    When unsupported object type is used for sharing

        Returns list of dataclasses containing access_type, created_by, entity, user associated with share.

        Each share record is a namedTuple with fields:
        - access_type: type of access like `Read` or `Write`.
        - shared_with: the user to which the entity is being shared.
        """
        return self._get_share_accessess(details_for="user")

    def grant_share_for_user(self, user: str, access_type: t.Literal["Read", "Write"]) -> None:
        """
        Share an object with a user based on access_type.
        A success message is printed when the access is granted to the user successfully.

        :param user: The name of the user to share the object with
        :param access_type: The type of access (Write or Read) granted to the user
        :return: None
        :raises RequestApiException: When user without Write access to the object calls this function
        """
        self._grant_share_for(access_type=access_type, share_with="user", share_with_value=user)

    def revoke_share_for_user(self, user: str) -> None:
        """
        Revoke the access of a user to the object.
        A success message is printed when the user's access is revoked successfully.

        :param user: The name of the user to share the object with
        :return: None
        :raises RequestApiException: When user without Write access to the object calls this function
        """
        self._revoke_share_for(revoke_for="user", revoke_for_value=user)

    @property
    def role_accesses(self) -> list[ShareRecord]:
        """
        Access user role related share details of an object
        :returns:                       List of user role details related to share
        :raises NotImplementedError:    When unsupported object type is used for sharing
        Returns list of named tuples containing access_type, created_by, entity, user_role associated with share.
        Each share record is a namedTuple with fields:
        - access_type: type of access like `Read` or `Write`.
        - shared_with: the user_role to which the entity is being shared.
        """
        return self._get_share_accessess(details_for="user_role")

    def grant_share_for_role(self, user_role: str, access_type: t.Literal["Read", "Write"]) -> None:
        """
        Share an object with a user role based on access_type.
        A success message is printed when the access is granted to the user role successfully.
        :param user_role:   The name of the user_role to share the object with
        :param access_type: The type of access (Write or Read) granted to the user role
        :return: None
        :raises RequestApiException: When user without Write access to the object calls this function
        """
        self._grant_share_for(access_type=access_type, share_with="user_role", share_with_value=user_role)

    def revoke_share_for_role(self, user_role: str) -> None:
        """
        Revoke the access of a user role to the object.
        A success message is printed when the access of a user role is revoked successfully.
        :param user: The name of the user_role to share the object with
        :return: None
        :raises RequestApiException: When user without Write access to the object calls this function
        """
        self._revoke_share_for(revoke_for="user_role", revoke_for_value=user_role)
