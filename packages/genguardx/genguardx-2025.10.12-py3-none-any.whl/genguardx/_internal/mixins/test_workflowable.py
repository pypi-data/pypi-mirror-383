from __future__ import annotations

import typing as t
from datetime import datetime

import pytest

from genguardx._internal.mixins.workflowable import ApprovalHistory, Responsibility, Workflowable
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import URLS
from genguardx_test.helpers import api_url


if t.TYPE_CHECKING:
    import responses


if t.TYPE_CHECKING:
    import responses


class TestResponsibility:
    def test_reviewers_with_invalid_responsibility_type(self) -> None:
        responsibility = Responsibility._from_data(data={"responsibilityType": "invalid"})
        assert responsibility.reviewers is None

    def test_attribute_approval_workflow(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.APPROVAL_WORKFLOW_PATH.value),
            json={"result": [{"id": 101, "name": "Compliance"}]},
        )
        responsibility = Responsibility._from_data(data={"workflowId": 101})
        assert responsibility.approval_workflow.name == "Compliance"

    def test_attribute_approval_workflow_invalid(self) -> None:
        with pytest.raises(NotImplementedError, match="Found unknown type for `approval_workflow`"):
            Responsibility._from_data(approval_workflow="not_an_integer").approval_workflow  # noqa: B018 --Call property to trigger the exception we are trying to test


class TestApprovalHistory:
    def test_attribute_responsibility_with_workflow_id(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.APPROVAL_WORKFLOW_PATH.value),
            json={
                "result": [
                    {
                        "id": 101,
                        "name": "Compliance",
                        "responsibilities": [{"id": 1, "name": "resp_1"}, {"id": 2, "name": "resp_2"}],
                    }
                ]
            },
        )
        history = ApprovalHistory(data={"responsibilityId": 2}, approval_workflow=101)
        assert history.responsibility.name == "resp_2"

    def test_attribute_responsibility_with_invalid_workflow_id(self) -> None:
        with pytest.raises(NotImplementedError, match="Found unknown type for `approval_workflow`"):
            ApprovalHistory(data={"responsibilityId": 2}, approval_workflow="invalid").responsibility  # noqa: B018 --Call property to trigger the exception we are trying to test

    def test_attribute_created_date(self) -> None:
        history = ApprovalHistory._from_data(data={"createdDate": "2024-08-20T12:20:37.000000"})
        created_date = history.created_date
        assert created_date == datetime(year=2024, month=8, day=20, hour=12, minute=20, second=37)

    def test_str_cast(self) -> None:
        history = ApprovalHistory._from_data(data={"newStatus": "Pending Approval"})

        assert str(history) == '<ApprovalHistory status="Pending Approval">'


class TestWorkflowable:
    def test_attribute_approval_workflow_not_present(self) -> None:
        class TestObject(ApiBase, Workflowable):
            pass

        obj = TestObject._from_data(data={"workflowId": None})
        assert obj.approval_workflow is None
        assert obj.approval_statuses is None
