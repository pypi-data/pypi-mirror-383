"""Progress update command for GHAI CLI."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import click

from ghai.github_api import GitHubGraphQLClient
from ghai.llm_api import LLMClient


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


@dataclass
class IssueComment:
    comment_id: str
    body: str
    createdAt: datetime
    url: str


@dataclass
class IssueData:
    issue_id: str
    title: str
    is_initiative: bool
    stateChange: IssueStateChange
    body: str
    url: str
    comments: list[IssueComment]


@click.command()
@click.option(
    "--issue-url",
    "-u",
    required=True,
    help="GitHub issue URL (e.g., https://github.com/owner/repo/issues/123)",
)
@click.option(
    "--days",
    "-d",
    default=7,
    help="Number of days to look back for comments (default: 7)",
)
@click.pass_context
def progress_update(ctx: click.Context, issue_url: str, days: int) -> None:
    """Get progress update from GitHub issue and its sub-issues"""

    github_client = GitHubGraphQLClient()

    owner, repo, issue_number = github_client.parse_github_issue_url(issue_url)
    initiative_details = github_client.get_sub_issue_data(
        owner, repo, issue_number)

    issue_data_list = parse_initiative_details(initiative_details, days)

    # markdown_output = format_context_as_markdown(issue_data_list, days)
    markdown_output = format_context(issue_data_list)

    with open("context.md", "w") as f:
        f.write(markdown_output)

    prompt_path = Path("prompts/initiative_prompt.md")
    if not prompt_path.exists():
        raise FileNotFoundError("Prompt file not found: initiative_prompt.md")

    prompt_content = prompt_path.read_text().strip()

    llmClient = LLMClient()

    response = llmClient.generate_response(
        prompt_content, context_files=["context.md"])

    with open("response.md", "w") as f:
        f.write(response)


def parse_initiative_details(
    initiative_details: dict[str, Any], days: int = 7
) -> list[IssueData]:
    since_datetime = datetime.now() - timedelta(days=days)

    issue_data_list: list[IssueData] = []

    # Get relevant initiative comments
    initiative_comments: list[IssueComment] = []
    for comment in initiative_details["comments"]["nodes"]:
        comment_date = datetime.fromisoformat(
            comment["createdAt"].replace("Z", "+00:00")
        )
        if comment_date >= since_datetime.replace(tzinfo=comment_date.tzinfo):
            initiative_comments.append(
                IssueComment(
                    comment_id=comment["id"],
                    body=comment["body"],
                    createdAt=comment["createdAt"],
                    url=comment["url"],
                )
            )

    issue_data_list.append(
        IssueData(
            issue_id=initiative_details["id"],
            title=initiative_details["title"],
            is_initiative=True,
            stateChange=IssueStateChange.NONE,
            body=initiative_details["body"],
            url=initiative_details["url"],
            comments=initiative_comments,
        )
    )

    # Get relevant sub-issues comments (if any)
    # Note: subIssues field was removed from GraphQL query since it's not standard GitHub API
    # For now, we'll only process the main issue until sub-issue tracking is implemented differently
    sub_issues_data = initiative_details.get("subIssues", {}).get("nodes", [])
    for sub_issue in sub_issues_data:
        sub_issue_comments: list[IssueComment] = []
        for comment in sub_issue["comments"]["nodes"]:
            comment_date = datetime.fromisoformat(
                comment["createdAt"].replace("Z", "+00:00")
            )
            if comment_date >= since_datetime.replace(tzinfo=comment_date.tzinfo):
                sub_issue_comments.append(
                    IssueComment(
                        comment_id=comment["id"],
                        body=comment["body"],
                        createdAt=comment["createdAt"],
                        url=comment["url"],
                    )
                )

        state_change = IssueStateChange.NONE
        for timeline_item in sub_issue["timelineItems"]["nodes"]:
            timeline_item_date = datetime.fromisoformat(
                timeline_item["createdAt"].replace("Z", "+00:00")
            )
            if timeline_item_date >= since_datetime.replace(
                tzinfo=timeline_item_date.tzinfo
            ):
                state_change = IssueStateChange.from_github_reason(
                    timeline_item["stateReason"]
                )

        issue_data_list.append(
            IssueData(
                issue_id=sub_issue["id"],
                title=sub_issue["title"],
                is_initiative=False,
                stateChange=state_change,
                body=sub_issue["body"],
                url=sub_issue["url"],
                comments=sub_issue_comments,
            )
        )
    return issue_data_list


def format_context(issue_data_list: list[IssueData]) -> str:
    """Format the context for the progress update (legacy table format)."""

    context: list[str] = []
    initiative = issue_data_list[0]
    sub_issues = [issue for issue in issue_data_list[1:]
                  if not issue.is_initiative]
    context.append("# Initiative Details: ")
    context.append(f"**Title:** {initiative.title}")
    context.append(f"**URL:** {initiative.url}")
    context.append(f"**State Change:** {initiative.stateChange.value}")
    context.append("### Recent Initiative Comments: ")
    for comment in issue_data_list[0].comments:
        context.append(f"##### Date: {comment.createdAt}")
        context.append("```")
        context.append(f"{comment.body}")
        context.append("```")
        context.append("")

    context.append("# 📋 Sub-Issues Progress")
    for issue in sub_issues:
        if len(issue.comments) == 0 and issue.stateChange == IssueStateChange.NONE:
            continue
        context.append(f"## {issue.title}")
        context.append(f"**URL:** {issue.url}")
        context.append(f"**State Change:** {issue.stateChange.value}")
        context.append("### Recent Comments: ")
        for comment in issue.comments:
            context.append(f"##### Date: {comment.createdAt}")
            context.append("```")
            context.append(f"{comment.body}")
            context.append("```")
            context.append("")

    return "\n".join(context)
