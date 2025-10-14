from __future__ import annotations

import dataclasses
import functools
import typing as t

import dateutil.parser

from genguardx._internal.mixins.auditable import Auditable
from genguardx._internal.mixins.searchable import Searchable
from genguardx._internal.util import utils
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects, URLS
from genguardx._internal.util.networking import api


if t.TYPE_CHECKING:
    import datetime

    from genguardx._internal.mixins.simulatable import Simulatable


class Responsibility(Auditable, ApiBase):
    """
    Represents an Responsibility that is registered.

    :param data:                 The data contains the information for Responsibility
    :param approval_workflow:   The ApprovalWorkflow that the Responsibility registered under, optional

    The following properties of the Responsibility can be accessed:
     - name: string
        The name of the Responsibility as registered.
     - reviewers: string or list
        - `Anyone` or the list of reviewer names if responsibility type is UserBased
        - Name of the tool if the responsibility is ToolBased
        - None otherwise
     - approval_workflow: ApprovalWorkflow object
        The ApprovalWorkflow that the Responsibility registered under
     - responsibility_type: string
        The type of the responsibility, can be 'UserBased' or 'ToolBased'
     - is_veto: bool
        Flag to check if the responsibility is veto or not
    """

    _exposed_properties = {"id", "name", "responsibility_type", "is_veto", "is_editable_by_reviewer"}

    def __init__(self, data: dict, approval_workflow: ApprovalWorkflow | int | None = None) -> None:
        self._approval_workflow = approval_workflow
        self._data = data

    # FIXME: add User/Role management
    @property
    def reviewers(self) -> str | list[str] | None:
        return self._data["users"] or "Anyone"

    @property
    def approval_workflow(self) -> ApprovalWorkflow:
        if not hasattr(self, "_approval_workflow"):
            self._approval_workflow = None

        if not isinstance(self._approval_workflow, ApprovalWorkflow):
            if self._approval_workflow is None:
                self._approval_workflow = self._data["workflowId"]
            if isinstance(self._approval_workflow, int):
                self._approval_workflow = ApprovalWorkflow(id=self._approval_workflow)
            else:
                raise NotImplementedError(
                    f"Found unknown type for `approval_workflow`: {type(self._approval_workflow)}"
                    ", expecting int or ApprovalWorkflow object"
                )
        return self._approval_workflow

    def __str__(self) -> str:
        return f'<{type(self).__name__} name="{self.name}">'


class ApprovalWorkflow(Auditable, ApiBase, Searchable):
    """
    Represents an ApprovalWorkflow that is registered.

    :param id:      The ID of the ApprovalWorkflow to fetch.

    Example:
        >>> model_approval_workflow = ApprovalWorkflow(id=1)
        >>> model_approval_workflow.name
        'Model Approval Workflow'

    The following properties of the ApprovalWorkflow can be accessed:
     - name: string
        The name of the ApprovalWorkflow as registered.
     - description: string
        The description registered for the ApprovalWorkflow.
     - object_types: list of string
        The list of object types that the ApprovalWorkflow can manage.
     - responsibilities: list of Responsibility objects
        The list of Responsibilities registered under the ApprovalWorkflow.

    The following functions of the ApprovalWorkflow can be accessed:
     - all(): list
        Returns a list of filtered ApprovalWorkflow objects
        Valid filters: contains, object_type
    """

    _LIST_URL = URLS.APPROVAL_WORKFLOW_PATH.value
    _exposed_properties = {"id", "name", "description"}
    # FIXME: no name filter in the api
    _available_filter_names = {"contains", "object_type"}

    def __init__(self, id: int) -> None:
        self._data = self._get_data(one=True, ids=id)

    @utils.classproperty
    def _possible_filter_values__object_type(cls) -> set[str]:
        return {
            Objects.display_name(i)
            for i in (
                Objects.FEATURE,
                Objects.MODEL,
                Objects.GLOBAL_FUNCTION,
                Objects.REPORT,
            )
        }

    @property
    def object_types(self) -> list[str]:
        return [obj_type["objectType"] for obj_type in self._data["objectTypes"]]

    @property
    def responsibilities(self) -> list[Responsibility]:
        return [Responsibility(resp, self) for resp in self._data["responsibilities"]]

    def __str__(self) -> str:
        return f'<{type(self).__name__} name="{self.name}">'


class ApprovalHistory(ApiBase):
    """
    Represents an approval history for the item.

    :param data:      The approval history details
    """

    _exposed_properties = {"comment", "action", "created_by"}

    def __init__(self, data: dict, approval_workflow: ApprovalWorkflow | int) -> None:
        self._data = data
        self._approval_workflow = approval_workflow

    @property
    def status(self) -> str:
        return self._data["newStatus"]

    @property
    def reviewers(self) -> list[str]:
        return self._data["reviewerNames"]

    @property
    def responsibility(self) -> Responsibility | None:
        if self._data["responsibilityId"] is None:
            return None

        assert self._approval_workflow, "Need approval_workflow to get responsibility"

        if isinstance(self._approval_workflow, int):
            self._approval_workflow = ApprovalWorkflow(id=self._approval_workflow)
        elif isinstance(self._approval_workflow, ApprovalWorkflow):
            pass
        else:
            raise NotImplementedError(
                f"Found unknown type for `approval_workflow`: {type(self._approval_workflow)}"
                ", expecting int or ApprovalWorkflow object"
            )
        return next(
            iter(r for r in self._approval_workflow.responsibilities if r.id == self._data["responsibilityId"]),
            None,
        )  # pragma: no cover -- coverage is reported incorrectly for generators. Ref: https://github.com/nedbat/coveragepy/issues/475

    @property
    def created_date(self) -> datetime.datetime:
        return dateutil.parser.parse(self._data["createdDate"])

    def __repr__(self) -> str:
        return f'<{type(self).__name__} status="{self.status}">'


@dataclasses.dataclass(frozen=True)
class ApprovalStatus:
    id: int
    type: str
    responsibility: Responsibility
    object: t.Any
    reviewers: list[str]
    status: str
    status_date: datetime.datetime
    simulations: list[Simulatable.Job]
    comment: str
    is_old: bool
    group_approval_id: int
    inputs: list[t.Any]


class Workflowable:
    """
    Represents an item that has approval histories.

    The following properties of the Workflowable can be accessed:
     - approval_workflow: ApprovalWorkflow
        The ApprovalWorkflow associated with the Workflowable object.
     - approval_statuses: list of ApprovalStatus tuples
        The approval statuses for the Workflowable object.
        ApprovalStatus contains id of the review, responsibility, object under review, reviewer, status,
        the simulation used for the review process, the comment and the info whether the review is old or not.
     - approval_histories: list of ApprovalHistory objects
        The approval histories for the Workflowable object.
    """

    @functools.cached_property
    def approval_workflow(self) -> ApprovalWorkflow | None:
        if self._data["workflowId"] is not None:
            return ApprovalWorkflow(id=self._data["workflowId"])
        return None

    @property
    def approval_statuses(self) -> list[ApprovalStatus] | None:
        if not self.approval_workflow:
            return None

        statuses = api.response(utils.ujoin(self._LIST_URL, f"{self.id}/review"))["result"]
        responsibilities = self.approval_workflow.responsibilities
        approval_statuses = []
        for status in statuses:
            responsibility = next(
                iter(resp for resp in responsibilities if resp.id == status["responsibilityId"]), None
            )  # pragma: no cover -- coverage is reported incorrectly for generators. Ref: https://github.com/nedbat/coveragepy/issues/475

            simulations = []
            for assoc in status.get("approvalSimAssocs") or []:
                sim_cls = Objects.class_mapping()[Objects(assoc["objectType"])]
                simulations.append(sim_cls.Job(id=assoc["simulationId"]))
            inputs = [Objects.class_mapping()[Objects(inp["objectType"])](id=inp["id"]) for inp in status["inputs"]]

            approval_statuses += [
                ApprovalStatus(
                    status["id"],
                    status["type"],
                    responsibility,
                    self,
                    status["reviewerNames"],
                    status["status"],
                    dateutil.parser.parse(status["statusDate"]) if status["statusDate"] is not None else None,
                    simulations,
                    status["comment"],
                    status["isOld"],
                    status["groupApprovalId"],
                    inputs,
                )
            ]
        return approval_statuses

    @functools.cached_property
    def approval_histories(self) -> list[ApprovalHistory]:
        histories = api.response(utils.ujoin(self._LIST_URL, f"{self.id}/audit"))["result"]
        workflow = self.approval_workflow
        return [ApprovalHistory(hist, workflow) for hist in histories]
