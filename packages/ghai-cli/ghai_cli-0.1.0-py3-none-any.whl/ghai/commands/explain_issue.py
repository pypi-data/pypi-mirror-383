

from pathlib import Path

import click

from ghai.github_api import GitHubGraphQLClient
from ghai.llm_api import LLMClient


@click.command()
@click.option(
    "--issue-url",
    "-u",
    required=True,
    help="GitHub issue URL (e.g., https://github.com/owner/repo/issues/123)",
)
@click.pass_context
def explain_issue(ctx: click.Context, issue_url: str) -> None:
    """Get progress update from GitHub issue and its sub-issues"""

    github_client = GitHubGraphQLClient()

    owner, repo, issue_number = github_client.parse_github_issue_url(issue_url)
    issue = github_client.get_issue_details(owner, repo, issue_number)

    formatted_issue = issue.format_issue_details() if issue else None

    if formatted_issue:
        with open("context.md", "w") as f:
            f.write(formatted_issue)

        llm_client = LLMClient()

        prompt_path = Path("prompts/explain_issue_prompt.md")

        if not prompt_path.exists():
            raise FileNotFoundError(
                "Prompt file not found: explain_issue_prompt.md")
        prompt_content = prompt_path.read_text().strip()
        response = llm_client.generate_response(
            prompt_content,
            context_files=["context.md"]
        )
        print(response)
    else:
        print(f"Issue {issue_number} not found.")
