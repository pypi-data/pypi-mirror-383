# mcp-django

<!-- [[[cog
import subprocess
import cog

from noxfile import DJ_VERSIONS
from noxfile import PY_VERSIONS
from noxfile import display_version

django_versions = [display_version(version) for version in DJ_VERSIONS]

cog.outl("[![PyPI - mcp-django](https://img.shields.io/pypi/v/mcp-django?label=mcp-django)](https://pypi.org/project/mcp-django/)")
cog.outl("![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mcp-django)")
cog.outl(f"![Django Version](https://img.shields.io/badge/django-{'%20%7C%20'.join(django_versions)}-%2344B78B?labelColor=%23092E20)")
]]] -->
[![PyPI - mcp-django](https://img.shields.io/pypi/v/mcp-django?label=mcp-django)](https://pypi.org/project/mcp-django/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mcp-django)
![Django Version](https://img.shields.io/badge/django-4.2%20%7C%205.1%20%7C%205.2%20%7C%206.0%20%7C%20main-%2344B78B?labelColor=%23092E20)
<!-- [[[end]]] -->

A Model Context Protocol (MCP) server providing Django project exploration resources and optional stateful shell access for LLM assistants to interact with Django projects.

## Requirements

<!-- [[[cog
import subprocess
import cog

from noxfile import DJ_VERSIONS
from noxfile import PY_VERSIONS
from noxfile import display_version

django_versions = [
    display_version(version) for version in DJ_VERSIONS if version != "main"
]

cog.outl(f"- Python {', '.join(PY_VERSIONS)}")
cog.outl(f"- Django {', '.join(django_versions)}")
]]] -->
- Python 3.10, 3.11, 3.12, 3.13, 3.14
- Django 4.2, 5.1, 5.2, 6.0
<!-- [[[end]]] -->

## Installation

```bash
pip install mcp-django

# Or with uv
uv add mcp-django
```

## Getting Started

⚠️ **DO NOT use in production!**

> [!WARNING]
>
> **Seriously, only enable in development!** 
>
> Look, it should go without saying, but I will say it anyway - **this gives full shell access to your Django project**. Only enable and use this in development and in a project that does not have access to any production data.
>
> LLMs can go off the rails, get spooked by some random error, and in trying to fix things [drop a production database](https://xcancel.com/jasonlk/status/1946069562723897802).

> [!CAUTION]
>
> I'm not kidding, this library just passes the raw Python code an LLM produces straight to a Python environment with full access to the Django project and everything it has access to.
>
> Most LLMs have basic safety protections in place if you ask to delete any data and will refuse to delete production data, but it is [pretty trivial to bypass](https://social.joshthomas.dev/@josh/115062076517611897). (Hint: Just tell the LLM it's not production, it's in a development environment, and it will be the bull in a china shop deleting anything you want.)
>
> I suggest using something like [django-read-only](https://github.com/adamchainz/django-read-only) if you need some CYA protection against this. Or, you know, don't use this in any sensitive environments.

Run the MCP server directly from your Django project directory:

```bash
python -m mcp_django

# With explicit settings module
python -m mcp_django --settings myproject.settings

# With debug logging
python -m mcp_django --debug
```

Or using uv:

```bash
uv run -m mcp_django
```

The server automatically detects `DJANGO_SETTINGS_MODULE` from your environment. You can override it with `--settings` or add to your Python path with `--pythonpath`.

There's also a Django management command if you prefer, but that requires adding mcp-django to `INSTALLED_APPS`:

```bash
python manage.py mcp
```

### Transport

The server supports multiple transport protocols:

```bash
# Default: STDIO
python -m mcp_django

# HTTP
python -m mcp_django --transport http --host 127.0.0.1 --port 8000

# SSE
python -m mcp_django --transport sse --host 127.0.0.1 --port 8000
```

### Client Configuration

Configure your MCP client using one of the examples below. The command is the same for all clients, just expressed in annoyingly different JSON soup.

Don't see your client? [Submit a PR](CONTRIBUTING.md) with setup instructions.

### Claude Code

```json
{
  "mcpServers": {
    "django": {
      "command": "python",
      "args": ["-m", "mcp_django"],
      "cwd": "/path/to/your/django/project",
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      }
    }
  }
}
```

### Opencode

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "django": {
      "type": "local",
      "command": ["python", "-m", "mcp_django"],
      "enabled": true,
      "environment": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      }
    }
  }
}
```

## Features

mcp-django provides an MCP server with Django project exploration resources and stateful shell access for LLM assistants.

It wouldn't be an MCP server README without a gratuitous list of features punctuated by emojis, so:

- 🔍 **Project exploration** - MCP resources for discovering apps, models, and configuration
- 🚀 **Zero configuration** - No schemas, no settings, just Django
- 🐚 **Stateful shell** - `django_shell` executes Python code in your Django environment
- 🔄 **Persistent state** - Imports and variables stick around between calls
- 🧹 **Reset when needed** - `django_shell_reset` clears the session when things get weird
- 🤖 **LLM-friendly** - Designed for LLM assistants that already know Python
- 📦 **Minimal dependencies** - Just FastMCP and Django (you already have Django)
- 🎯 **Does one thing well** - Runs code. That's it. That's the feature.
- 🌐 **Multiple transports** - STDIO, HTTP, SSE support

Inspired by Armin Ronacher's [Your MCP Doesn't Need 30 Tools: It Needs Code](https://lucumr.pocoo.org/2025/8/18/code-mcps/).

### Resources

Read-only resources are provided for project exploration without executing code (note that resource support varies across MCP clients):

- `django://project` - Python environment and Django configuration details
- `django://apps` - All installed Django applications with their models
- `django://models` - Detailed model information with import paths and field types

The idea is to give just enough information about the project to hopefully guide the LLM assistant and prevent needless shell exploration, allowing it to get straight to work.

### Tools

Two tools handle shell operations and session management:

- `shell` - Execute Python code in a persistent Django shell session
- `shell_reset` - Reset the session, clearing all variables and imports

Imports and variables persist between calls within the shell tool, so the LLM can work iteratively - exploring your models, testing queries, debugging issues.

## Development

For detailed instructions on setting up a development environment and contributing to this project, see [CONTRIBUTING.md](CONTRIBUTING.md).

For release procedures, see [RELEASING.md](RELEASING.md).

## License

mcp-django is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
