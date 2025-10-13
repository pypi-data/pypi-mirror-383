

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class IssueState(Enum):
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    NONE = "None"

    @classmethod
    def from_github_reason(cls, reason: str) -> "IssueState":
        mapping = {
            "COMPLETED": cls.COMPLETED,
            "CLOSED": cls.CLOSED,
            "OPEN": cls.OPEN,
        }
        return mapping.get(reason, cls.NONE)


class StateReason(Enum):
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    NOT_PLANNED = "NOT_PLANNED"
    DUPLICATE = "DUPLICATE"
    REOPENED = "REOPENED"
    NONE = "None"

    @classmethod
    def from_github_reason(cls, reason: str) -> "StateReason":
        mapping = {
            "COMPLETED": cls.COMPLETED,
            "CLOSED": cls.CLOSED,
            "NOT_PLANNED": cls.NOT_PLANNED,
            "DUPLICATE": cls.DUPLICATE,
            "REOPENED": cls.REOPENED,
        }
        return mapping.get(reason, cls.NONE)


@dataclass
class TimeLineItem:
    createdAt: datetime
    stateReason: StateReason


@dataclass
class IssueComment:
    comment_id: str
    body: str
    createdAt: datetime
    url: str


@dataclass
class FieldValue:
    name: str
    value: str


@dataclass
class IssueLabel:
    name: str
    description: str


@dataclass
class Issue:
    issue_id: str
    title: str
    state: IssueState
    body: str
    url: str
    fields: List[FieldValue]
    labels: List[IssueLabel]
    comments: List[IssueComment]
    timeLineItems: List[TimeLineItem]
    subIssueIds: List[str]

    def get_field_value(self, field_name: str) -> Optional[str]:
        for field in self.fields:
            if field.name == field_name:
                return field.value
        return None

    @classmethod
    def from_graphql_response(
        cls, data: Dict[str, Any]
    ) -> "Issue":

        return cls(
            issue_id=data.get("id", ""),
            title=data.get("title", ""),
            state=IssueState.from_github_reason(data.get("state", "")),
            body=data.get("body", ""),
            url=data.get("url", ""),
            fields=[
                FieldValue(name=field["field"]["name"], value=field["name"])
                for field in data.get("fieldValues", {}).get("nodes", [])
                if field.get("field") and field.get("name")
            ],
            labels=[
                IssueLabel(
                    name=label["name"],
                    description=label.get("description", "")
                )
                for label in data.get("labels", {}).get("nodes", [])
                if label.get("name")
            ],
            comments=[
                IssueComment(
                    comment_id=comment["id"],
                    body=comment["body"],
                    createdAt=datetime.fromisoformat(
                        comment["createdAt"].rstrip("Z")),
                    url=comment["url"],
                )
                for comment in data.get("comments", {}).get("nodes", [])
            ],
            timeLineItems=[
                TimeLineItem(
                    createdAt=datetime.fromisoformat(
                        item["createdAt"].rstrip("Z")),
                    stateReason=StateReason.from_github_reason(
                        item.get("stateReason", "None")
                    ),
                )
                for item in data.get("timelineItems", {}).get("nodes", [])
                if item.get("createdAt") and item.get("stateReason")
            ],
            subIssueIds=[
                sub_issue["id"]
                for sub_issue in data.get("subIssues", {}).get("nodes", [])
                if sub_issue.get("id")
            ],
        )

    def format_issue_details(self) -> str:
        details = [
            f"Issue ID: {self.issue_id}",
            f"Title: {self.title}",
            f"State: {self.state.value}",
            f"URL: {self.url}",
            f"Body:\n{self.body}\n",
            "Fields:",
        ]
        for field in self.fields:
            details.append(f"  - {field.name}: {field.value}")
        details.append("Labels:")
        for label in self.labels:
            details.append(f"  - {label.name}: {label.description}")
        details.append("Comments:")
        for comment in self.comments:
            details.append(
                f"  - [{comment.createdAt.isoformat()}] {comment.body} (URL: {comment.url})"
            )
        details.append("Timeline Items:")
        for item in self.timeLineItems:
            details.append(
                f"  - [{item.createdAt.isoformat()}] State Reason: {item.stateReason.value}"
            )
        if self.subIssueIds:
            details.append("Sub-Issue IDs:")
            for sub_id in self.subIssueIds:
                details.append(f"  - {sub_id}")
        return "\n".join(details)
