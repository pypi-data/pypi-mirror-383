# GHAI CLI

A Python command-line interface application built with Click.

## Installation

### Quick Start with Dev Container (Recommended)

The easiest way to get started is using the included development container:

1. **Prerequisites:**
   - [Visual Studio Code](https://code.visualstudio.com/)
   - [Docker](https://www.docker.com/get-started)
   - [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Setup:**
   ```bash
   git clone <repository-url>
   cd ghai
   code .
   ```

3. **Open in container:**
   - Click "Reopen in Container" when prompted, or
   - Use Command Palette: "Dev Containers: Reopen in Container"

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GitHub token
   ```

See [.devcontainer/README.md](.devcontainer/README.md) for detailed devcontainer documentation.

### Development Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ghai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

### Production Installation

```bash
pip install ghai-cli
```

## Usage

After installation, you can use the CLI tool:

```bash
# Basic usage
ghai --help

# Example commands
ghai hello
ghai hello --name "World"
ghai goodbye --name "Alice"
```

### GitHub API Integration

The CLI includes a GitHub GraphQL API client that can be used internally by commands. To use GitHub API functionality, you need a GitHub Personal Access Token:

1. Go to https://github.com/settings/tokens
2. Generate a new token with appropriate scopes (repo, user, read:org)
3. Create a `.env` file in your project root:
   ```bash
   cp .env.example .env
   ```
4. Add your token to the `.env` file:
   ```
   GITHUB_TOKEN=your_actual_token_here
   ```

The GitHub API client (`ghai.github_api.GitHubGraphQLClient`) is available for use in your custom commands.

#### Example Usage in Commands

```python
# Example: Using GitHub API in a command
from ghai.github_api import GitHubGraphQLClient

@click.command()
@click.option('--github-user', help='GitHub username')
def my_command(github_user):
    if github_user:
        try:
            client = GitHubGraphQLClient()
            user_info = client.get_user_info(github_user)
            click.echo(f"User: {user_info['name']} (@{user_info['login']})")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
```

Try the enhanced hello command:
```bash
# Greet a GitHub user by their real name
ghai hello --github-user octocat
```

## Development

### Running Tests

No tests are currently configured for this project.

### Code Formatting

```bash
black src/ tests/
```

### Type Checking

```bash
mypy src/
```

### Linting

```bash
flake8 src/
```

## Project Structure

```
ghai/
├── src/
│   └── ghai/
│       ├── __init__.py
│       ├── cli.py          # Main CLI entry point
│       ├── github_api.py   # GitHub GraphQL API client
│       └── commands/       # Command modules
│           ├── __init__.py
│           ├── hello.py
│           └── goodbye.py
├── pyproject.toml
└── README.md
```

## License

MIT License
