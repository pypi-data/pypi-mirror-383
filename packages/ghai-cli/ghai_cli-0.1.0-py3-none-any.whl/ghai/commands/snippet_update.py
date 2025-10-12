"""Snippet update command for GHAI CLI."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import click

from ghai.github_api import GitHubGraphQLClient, IssueComment, ProjectIssue
from ghai.llm_api import LLMClient


@click.command()
@click.option('--project-url', '-u',
              required=True,
              help='GitHub project URL (e.g., https://github.com/orgs/<org_name>/projects/<project_id>)'
              )
@click.option('--days', '-d', default=7, help='Number of days to look back (default: 7)')
@click.option('--workstream', '-w', default='SFI', help='Workstream to filter by (default: SFI)')
@click.pass_context
def snippet_update(ctx: click.Context, project_url: str, days: int, workstream: str) -> None:
    """Get snippet update from a GitHub project workstream"""

    github_client = GitHubGraphQLClient()

    owner, project_number = github_client.parse_github_project_url(project_url)

    print("Getting project details...")
    project_issues = github_client.get_project_issues(owner, project_number)

    print("Filtering project issues...")
    filtered_issues = filter_project_issues(
        project_issues, days, workstream=workstream)

    print("Generating context file...")
    generate_context_file(filtered_issues, "github_context.md")

    prompt_path = Path("prompts/snippet_prompt.md")
    if not prompt_path.exists():
        raise FileNotFoundError("Prompt file not found: snippet_prompt.md")

    prompt_content = prompt_path.read_text().strip()

    llm_client = LLMClient()

    print("Generating LLM response...")
    llm_response = llm_client.generate_response(
        prompt_content, context_files=["github_context.md"])

    with open("test_response.md", "w") as f:
        f.write(llm_response)


def filter_project_issues(issues: List[ProjectIssue], days: int = 14, workstream: str = "SFI") -> List[ProjectIssue]:
    """Filter ProjectIssues to only include comments from the last N days.

    Args:
        issues: List of ProjectIssue objects
        days: Number of days to look back (default: 14)

    Returns:
        List of ProjectIssue objects with only recent comments
    """
    cutoff_date = datetime.now() - timedelta(days=days)

    filtered_issues: list[ProjectIssue] = []
    for issue in issues:
        # Filter by workstream if specified
        if workstream and issue.get_field_value("Workstream") != workstream:
            continue

        # Filter comments to only include recent ones
        recent_comments: list[IssueComment] = []
        for comment in issue.comments:
            # Handle both datetime objects and ISO strings
            if isinstance(comment.createdAt, str):
                comment_date = datetime.fromisoformat(
                    comment.createdAt.replace('Z', '+00:00'))  # pyright: ignore[reportArgumentType]
            else:
                comment_date = comment.createdAt

            # Make cutoff_date timezone-aware if comment_date is timezone-aware
            if comment_date.tzinfo is not None and cutoff_date.tzinfo is None:
                from datetime import timezone
                cutoff_date = cutoff_date.replace(tzinfo=timezone.utc)
            elif comment_date.tzinfo is None and cutoff_date.tzinfo is not None:
                cutoff_date = cutoff_date.replace(tzinfo=None)

            if comment_date > cutoff_date:
                recent_comments.append(comment)

        # Create a new ProjectIssue with filtered comments
        filtered_issue = ProjectIssue(
            issue_id=issue.issue_id,
            title=issue.title,
            project=issue.project,
            fields=issue.fields,
            url=issue.url,
            comments=recent_comments
        )
        filtered_issues.append(filtered_issue)

    return filtered_issues


def generate_context_file(issues: List[ProjectIssue], output_path: str = "context.md") -> None:
    """Generate a context markdown file from ProjectIssues with recent comments.

    Args:
        issues: List of ProjectIssue objects (should be pre-filtered for recent comments)
        output_path: Path where to save the context file
    """
    content: list[str] = []

    for issue in issues:
        if not issue.comments:  # Skip issues with no recent comments
            continue

        content.append(f"# Issue: {issue.title}")
        content.append(f"**URL:** {issue.url}")
        content.append(f"**ID:** {issue.issue_id}")
        content.append(f"**Project:** {issue.project}")

        # Add fields if they exist
        if issue.fields:
            content.append("\n## Fields:")
            for field in issue.fields:
                content.append(f"- **{field.name}:** {field.value}")

        # Add recent comments
        if issue.comments:
            content.append("\n## Recent Comments (Last 14 Days):")
            for comment in sorted(issue.comments, key=lambda c: c.createdAt, reverse=True):
                # Format datetime for display
                if isinstance(comment.createdAt, str):
                    date_str = comment.createdAt
                else:
                    date_str = comment.createdAt.isoformat()

                content.append(f"\n### Comment - {date_str}")
                content.append(f"**URL:** {comment.url}")
                content.append("```")
                content.append(comment.body)
                content.append("```")

        content.append("\n---\n")

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
