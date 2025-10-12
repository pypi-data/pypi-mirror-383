"""LLM API module for GHAI CLI."""

import json
from pathlib import Path

import llm


class LLMClient:
    """A simple client for interacting with LLM models."""

    def __init__(self, model_name: str = "github/o1", api_key: str | None = None):
        """Initialize the LLM client.

        Args:
            model_name: Name of the LLM model to use (default: github/o1)
            api_key: API key for the model. If not provided, will try to get from GHAI's key storage
        """
        self.model_name = model_name
        self.model = llm.get_model(model_name)

        # If no API key provided, try to get it from GHAI keys
        if not api_key:
            api_key = self._get_github_token()

        if api_key:
            self.model.key = api_key
        else:
            raise ValueError(
                "GitHub token is required for GitHub models. You can set it by:\n"
                "- Using: ghai keys set GITHUB_TOKEN\n"
                "- Or use llm: llm keys set github"
            )

    def _get_github_token(self) -> str | None:
        """Get GitHub token from GHAI keys.json"""
        try:
            home_dir = Path.home()
            keys_path = home_dir / ".ghai" / "keys.json"

            if keys_path.exists():
                keys_data: dict[str, str] = json.loads(keys_path.read_text())
                return keys_data.get("GITHUB_TOKEN")
        except Exception:
            pass
        return None

    def generate_response(self, prompt_content: str, context_files: list[str]) -> str:
        """Generate a response using a prompt file and optional attachment files.

        Args:
            prompt_content: The prompt text to send to the model
            context_files: List of file paths to attach to the prompt

        Returns:
            The LLM response as a string

        Raises:
            FileNotFoundError: If any context file doesn't exist
        """
        fragments: list[str] = []
        for file_path in context_files:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(path) as f:
                fragments.append(f.read())

        # Use positional argument for prompt to avoid type issues
        response = self.model.prompt(  # pyright: ignore[reportUnknownMemberType]
            prompt=prompt_content, fragments=fragments)
        result = response.text()
        return str(result)


def get_available_models() -> list[str]:
    """Get list of available LLM models.

    Returns:
        List of available model IDs
    """
    models: list[str] = []
    for model in llm.get_models():
        models.append(model.model_id)
    return models


def set_api_key(model_name: str, api_key: str) -> None:
    """Set API key for a specific model using LLM's key storage.

    Args:
        model_name: Name of the model
        api_key: API key to set
    """
    model = llm.get_model(model_name)
    model.key = api_key
