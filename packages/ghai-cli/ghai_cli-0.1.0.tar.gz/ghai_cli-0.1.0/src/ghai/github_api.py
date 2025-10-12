"""GitHub GraphQL API client for GHAI CLI."""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import requests

from ghai.types.github_api_types import Issue


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


class IssueStateChange(Enum):
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    NONE = "None"

    @classmethod
    def from_github_reason(cls, reason: str) -> "IssueStateChange":
        mapping = {
            "COMPLETED": cls.COMPLETED,
            "CLOSED": cls.CLOSED,
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
class IssueData:
    issue_id: str
    title: str
    is_initiative: bool
    fields: List[FieldValue]
    state: IssueState
    stateChange: IssueStateChange
    body: str
    url: str
    comments: List[IssueComment]
    timeLineItems: List[TimeLineItem]

    def get_field_value(self, field_name: str) -> Optional[str]:
        for field in self.fields:
            if field.name == field_name:
                return field.value
        return None

    @classmethod
    def from_github_issue(cls, data: Dict[str, Any]) -> "IssueData":
        comments = [
            IssueComment(
                comment_id=comment["id"],
                body=comment["body"],
                createdAt=comment["createdAt"],
                url=comment["url"],
            )
            for comment in data.get("comments", {}).get("nodes", [])
        ]

        timeLineItems = [
            TimeLineItem(
                createdAt=item["createdAt"],
                stateReason=StateReason.from_github_reason(
                    item.get("stateReason")),
            )
            for item in data.get("timelineItems", {}).get("nodes", [])
        ]

        return cls(
            issue_id=data["id"],
            title=data["title"],
            is_initiative=(
                data.get("state") == "OPEN"
                and data.get("title", "").startswith("[Initiative]")
            ),
            fields=[
                FieldValue(name=field["name"], value=field["value"])
                for field in data.get("fields", [])
            ],
            state=IssueState.from_github_reason(data.get("state", "")),
            stateChange=IssueStateChange.from_github_reason(
                data.get("stateChange", "")),
            body=data["body"],
            url=data["url"],
            comments=comments,
            timeLineItems=timeLineItems,
        )


@dataclass
class ProjectIssue:
    issue_id: str
    title: str
    project: int
    fields: List[FieldValue]
    url: str
    comments: List[IssueComment]

    def get_field_value(self, field_name: str) -> Optional[str]:
        for field in self.fields:
            if field.name == field_name:
                return field.value
        return None

    @classmethod
    def from_github_project_issue(
        cls, project_number: int, data: Dict[str, Any]
    ) -> "ProjectIssue | None":
        if data.get("content") is None:
            return None

        return cls(
            issue_id=data.get("content", {}).get("id"),
            title=data.get("content", {}).get("title"),
            project=project_number,
            fields=[
                FieldValue(name=field["field"]["name"], value=field["name"])
                for field in data.get("fieldValues", {}).get("nodes", [])
                if field.get("field") and field.get("name")
            ],
            comments=[
                IssueComment(
                    comment_id=comment["id"],
                    body=comment["body"],
                    createdAt=comment["createdAt"],
                    url=comment["url"],
                )
                for comment in data.get("content", {})
                .get("comments", {})
                .get("nodes", [])
            ],
            url=data.get("content", {}).get("url"),
        )


class GitHubGraphQLClient:
    """A client for interacting with GitHub's GraphQL API."""

    def __init__(self) -> None:
        """Initialize the GitHub GraphQL client.

        Args:
            token: GitHub personal access token. Will try to get from keys.json.
        """
        self.base_url = "https://api.github.com/graphql"

        # Try multiple sources for the token
        self.token = self._get_token()

        if not self.token:
            raise ValueError(
                "GitHub token is required. You can set it by:\n"
                "- Using: ghai keys set GITHUB_TOKEN\n"
            )

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _get_token(self) -> Optional[str]:
        """Get GitHub token from keys.json"""
        home_dir = Path.home()
        keys_path = home_dir / ".ghai" / "keys.json"

        if keys_path.exists():
            keys_data: dict[str, str] = json.loads(keys_path.read_text())
            token = keys_data.get("GITHUB_TOKEN")
            if token:
                return token

        click.ClickException(
            "key 'GITHUB_TOKEN' not found. Please set it using 'ghai keys set GITHUB_TOKEN'"
        )
        return None

    def query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query against GitHub API.

        Args:
            query: The GraphQL query string
            variables: Optional variables for the query

        Returns:
            The response data from GitHub API

        Raises:
            requests.RequestException: If the HTTP request fails
            ValueError: If the GraphQL query has errors
        """
        payload: dict[str, Any] = {
            "query": query, "variables": variables or {}}

        try:
            response = requests.post(
                self.base_url, headers=self.headers, json=payload, timeout=30
            )
            response.raise_for_status()

            data: dict[str, Any] = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                error_messages = [
                    error.get("message", "Unknown error") for error in data["errors"]
                ]
                raise ValueError(
                    f"GraphQL errors: {'; '.join(error_messages)}")

            return data

        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to query GitHub API: {e}")

    def paginated_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        cursor_path: List[str] = [],
    ) -> List[Dict[str, Any]]:
        """
        Execute a paginated GraphQL query against GitHub API and return all results.

        Args:
            query: The GraphQL query string (must accept $after variable for pagination)
            variables: Optional dict of query variables
            cursor_path: Path (list of keys) to the paginated field in the response
                        e.g. ["organization", "projectV2", "items"]

        Returns:
            A list of all nodes across all pages.
        """
        all_nodes: list[dict[str, Any]] = []
        variables = variables or {}
        variables["after"] = None  # start without a cursor

        while True:
            data = self.query(query, variables)

            # Traverse into nested structure until we reach the paginated object
            page = data["data"]
            for key in cursor_path:
                page = page[key]

            # Collect nodes
            all_nodes.extend(page["nodes"])

            # Check if more pages exist
            page_info = page["pageInfo"]
            if not page_info["hasNextPage"]:
                break

            # Set cursor for next request
            variables["after"] = page_info["endCursor"]

        return all_nodes

    def parse_github_issue_url(self, url: str) -> tuple[str, str, int]:
        """Parse a GitHub issue URL to extract owner, repo, and issue number.

        Args:
            url: GitHub issue URL (e.g., "https://github.com/owner/repo/issues/123")

        Returns:
            Tuple of (owner, repo, issue_number)

        Raises:
            ValueError: If URL format is invalid
        """

        # Match GitHub issue URL pattern
        pattern = r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)"
        match = re.match(pattern, url)

        if not match:
            raise ValueError("Invalid GitHub issue URL format: {url}")

        owner, repo, issue_number = match.groups()
        return owner, repo, int(issue_number)

    def parse_github_project_url(self, url: str) -> tuple[str, int]:
        """Parse a GitHub project URL to extract owner, repo, and project number.

        Args:
            url: GitHub project URL (e.g., "https://github.com/orgs/owner/projects/20761")
        """
        pattern = r"https://github\.com/orgs/([^/]+)/projects/(\d+)"
        match = re.match(pattern, url)

        if not match:
            raise ValueError("Invalid GitHub project URL format: {url}")

        owner, project_number = match.groups()
        return owner, int(project_number)

    def get_sub_issue_data(
        self, owner: str, name: str, issue_number: int
    ) -> Dict[str, Any]:
        """Get detailed information about a GitHub issue including sub-issues.

        Args:
            owner: Repository owner
            name: Repository name
            issue_number: Issue number

        Returns:
            Issue information including linked issues
        """
        query = """
          query($owner: String!, $name: String!, $issueNumber: Int!) {
              repository(owner: $owner, name: $name) {
                  issue(number: $issueNumber) {
                      id
                      number
                      title
                      state
                      body
                      url
                      comments(last: 50, orderBy: {field: UPDATED_AT, direction: ASC}) {
                          nodes {
                              id
                              body
                              createdAt
                              url
                          }
                          totalCount
                      }
                      subIssues(first: 50) {
                          nodes {
                              id
                              number
                              title
                              state
                              body
                              url
                              comments(last: 50, orderBy: {field: UPDATED_AT, direction: ASC}) {
                                  nodes {
                                      id
                                      body
                                      createdAt
                                      url
                                  }
                                  totalCount
                              }
                              timelineItems(last: 50, itemTypes: [CLOSED_EVENT]) {
                                  nodes {
                                      ... on ClosedEvent {
                                          createdAt
                                          stateReason  # Can be COMPLETED, NOT_PLANNED, etc.
                                      }
                                  }
                              }
                          }
                      }
                  }
              }
          }
        """

        variables: dict[str, Any] = {"owner": owner,
                                     "name": name, "issueNumber": issue_number}

        response: dict[str, Any] = self.query(query, variables)
        issue_response: dict[str, Any] = response.get(
            "data", {}).get("repository", {}).get("issue", {})
        return issue_response

    def get_issue_data(self, issue_ids: List[str]) -> List[IssueData]:
        """Get detailed information about multiple GitHub issues by their IDs.

        Args:
            issue_ids: List of GitHub issue IDs (Limit 100)

        Returns
          A list of IssueData objects
        """

        query = """
            query($issueIds: [ID!]!) {
                nodes(ids: $issueIds) {
                    ... on Issue {
                        id
                        number
                        title
                        state
                        body
                        url
                        comments(last: 50, orderBy: {field: UPDATED_AT, direction: ASC}) {
                            nodes {
                                id
                                body
                                createdAt
                                url
                            }
                            totalCount
                        }
                        timelineItems(last: 50, itemTypes: [CLOSED_EVENT]) {
                            nodes {
                                ... on ClosedEvent {
                                    createdAt
                                    stateReason  # Can be COMPLETED, NOT_PLANNED, etc.
                                }
                            }
                        }
                    }
                }
            }
        """

        variables = {"issueIds": issue_ids}
        response = self.query(query, variables)

        issues: list[IssueData] = []
        for issue in response["data"]["nodes"]:
            issues.append(IssueData.from_github_issue(issue))

        return issues

    def get_project_issues(self, owner: str, project_number: int) -> List[ProjectIssue]:
        """Get detailed information about a GitHub project including its issues.

        Args:
            owner: Organization or user who owns the repository
            project_number: Project number

        Returns:
            Project information including its issues
        """

        query = """
          query($owner: String!, $projectNumber: Int!, $after: String) {
            organization(login: $owner) {
              projectV2(number: $projectNumber) {
                title
                items(first: 100, after: $after) {
                  nodes {
                    content {
                      ... on Issue {
                        id
                        number
                        title
                        url
                        state
                        comments(last: 50, orderBy: {field: UPDATED_AT, direction: ASC}) {
                            nodes {
                                id
                                body
                                createdAt
                                url
                            }
                            totalCount
                        }
                      }
                    }
                    fieldValues(first: 25) {
                      nodes {
                        ... on ProjectV2ItemFieldSingleSelectValue {
                          name
                          field {
                            ... on ProjectV2SingleSelectField {
                              name
                            }
                          }
                        }
                      }
                    }
                  }
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                }
              }
            }
          }
        """

        variables: dict[str, Any] = {
            "owner": owner, "projectNumber": project_number}
        cursor_path = ["organization", "projectV2", "items"]
        response = self.paginated_query(query, variables, cursor_path)

        project_issues: list[ProjectIssue] = []
        for node in response:
            project_issue = ProjectIssue.from_github_project_issue(
                project_number, node)
            if project_issue is not None:
                project_issues.append(project_issue)

        return project_issues

    # def get_project_issues_nested(self, owner: str, project_number: int) -> List[ProjectIssue]:
    #     """Get detailed information about a GitHub project including its issues.

    #     Args:
    #         owner: Organization or user who owns the repository
    #         project_number: Project number

    #     Returns:
    #         Project information including its issues
    #     """

    #     query = """
    #       query($owner: String!, $projectNumber: Int!, $after: String) {
    #         organization(login: $owner) {
    #           projectV2(number: $projectNumber) {
    #             title
    #             items(first: 100, after: $after) {
    #               nodes {
    #                 content {
    #                   ... on Issue {
    #                     id
    #                     number
    #                     title
    #                     url
    #                     state
    #                     subIssues(first: 100) {
    #                         nodes {
    #                             id
    #                         }
    #                     }
    #                   }
    #                 }
    #                 fieldValues(first: 25) {
    #                   nodes {
    #                     ... on ProjectV2ItemFieldSingleSelectValue {
    #                       name
    #                       field {
    #                         ... on ProjectV2SingleSelectField {
    #                           name
    #                         }
    #                       }
    #                     }
    #                   }
    #                 }
    #               }
    #               pageInfo {
    #                 hasNextPage
    #                 endCursor
    #               }
    #             }
    #           }
    #         }
    #       }
    #     """

    #     variables = {"owner": owner, "projectNumber": project_number}
    #     cursor_path = ["organization", "projectV2", "items"]
    #     response = self.paginated_query(query, variables, cursor_path)

    #     # Step 1: Build flat lookup of id -> ProjectIssue
    #     issues: Dict[str, ProjectIssue] = {}
    #     for node in response:
    #         issue_id = node["content"]["id"]
    #         issue = ProjectIssue(
    #             issue_id=issue_id,
    #             title=node["content"]["title"],
    #             project=project_number,
    #             fields=[
    #                 FieldValue(
    #                     name=field["field"]["name"],
    #                     value=field["name"]
    #                 )
    #                 for field in node["fieldValues"]["nodes"]
    #                 if "name" in field and "field" in field
    #             ],
    #             sub_issues=[],
    #             url=node["content"]["url"]
    #         )
    #         issues[issue_id] = issue

    #     # Step 2: Wire up parent → sub_issues using trackedIssues/subIssues
    #     child_ids = set()
    #     for node in response:
    #         parent_id = node["content"]["id"]
    #         for sub in node["content"]["subIssues"]["nodes"]:
    #             sub_id = sub["id"]
    #             if sub_id in issues.keys():
    #                 issues[parent_id].sub_issues.append(issues[sub_id])
    #                 child_ids.add(sub_id)

    #     root_issues = []
    #     for (id, issue) in issues.items():
    #         if id not in child_ids:
    #             root_issues.append(issue)

    #     roots = [issue for iid, issue in issues.items() if iid not in child_ids]
    #     return roots

    def get_issue_details(self, owner: str, name: str, issue_number: int) -> Issue | None:
        """Get detailed information about a GitHub issue.

        """

        query = """
          query($owner: String!, $name: String!, $issueNumber: Int!) {
              repository(owner: $owner, name: $name) {
                  issue(number: $issueNumber) {
                      id
                      title
                      state
                      body
                      url
                      comments(last: 50, orderBy: {field: UPDATED_AT, direction: ASC}) {
                          nodes {
                              id
                              body
                              createdAt
                              url
                          }
                          totalCount
                      }
                      labels(first: 10) {
                          nodes {
                              name
                              description
                          }
                      }
                      timelineItems(last: 50, itemTypes: [CLOSED_EVENT]) {
                          nodes {
                              ... on ClosedEvent {
                                  createdAt
                                  stateReason  # Can be COMPLETED, NOT_PLANNED, etc.
                              }
                          }
                      }
                      projectItems(first: 5) {
                          nodes {
                              project {
                                  title
                                  number
                              }
                              fieldValues(first: 15) {
                                  nodes {
                                      ... on ProjectV2ItemFieldSingleSelectValue {
                                        field {
                                          ... on ProjectV2FieldCommon {
                                            name
                                          }
                                        }
                                        name
                                      }
                                      ... on ProjectV2ItemFieldDateValue {
                                          field {
                                            ... on ProjectV2FieldCommon {
                                              name
                                            }
                                          }
                                        date
                                      }
                                  }
                              }
                          }
                      }
                      subIssues(first: 100) {
                          nodes {
                              id
                          }
                      }
                  }
              }
          }
        """

        variables: dict[str, Any] = {"owner": owner,
                                     "name": name, "issueNumber": issue_number}

        response: dict[str, Any] = self.query(query, variables)
        issue = Issue.from_graphql_response(response.get(
            "data", {}).get("repository", {}).get("issue", {}))
        return issue


if __name__ == "__main__":
    github_client = GitHubGraphQLClient()

    issue = github_client.get_issue_details(
        "github", "codespaces", 17587)
