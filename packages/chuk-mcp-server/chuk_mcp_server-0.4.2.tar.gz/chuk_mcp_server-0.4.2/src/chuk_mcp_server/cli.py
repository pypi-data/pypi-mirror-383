#!/usr/bin/env python3
"""
CLI entry point for ChukMCPServer.

Provides command-line interface for running the server in different modes.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

from .core import ChukMCPServer


def setup_logging(debug: bool = False, stderr: bool = True) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    stream = sys.stderr if stderr else sys.stdout

    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=stream)


def create_example_server() -> ChukMCPServer:
    """Create a simple example server with basic tools."""
    server = ChukMCPServer(
        name=os.environ.get("MCP_SERVER_NAME", "chuk-mcp-server"),
        version=os.environ.get("MCP_SERVER_VERSION", "0.2.3"),
        description="High-performance MCP server with stdio and HTTP support",
    )

    # Add example tools if no tools are registered
    if not server.get_tools():

        @server.tool("echo")  # type: ignore[misc]
        def echo(message: str) -> str:
            """Echo back the provided message."""
            return f"Echo: {message}"

        @server.tool("add")  # type: ignore[misc]
        def add(a: float, b: float) -> float:
            """Add two numbers together."""
            return a + b

        @server.tool("get_env")  # type: ignore[misc]
        def get_env(key: str) -> str | None:
            """Get an environment variable value."""
            return os.environ.get(key)

    # Add example resource if no resources are registered
    if not server.get_resources():

        @server.resource("server://info")  # type: ignore[misc]
        def server_info() -> dict[str, Any]:
            """Get server information."""
            return {
                "name": server.server_info.name,
                "version": server.server_info.version,
                "transport": "stdio" if os.environ.get("MCP_STDIO") else "http",
                "pid": os.getpid(),
            }

    return server


def scaffold_project(project_name: str, directory: str | None = None) -> None:
    """Scaffold a new MCP server project."""
    # Determine project directory
    project_dir = Path(directory) if directory else Path.cwd() / project_name

    # Check if directory already exists
    if project_dir.exists():
        print(f"❌ Error: Directory '{project_dir}' already exists")
        sys.exit(1)

    # Create project directory
    project_dir.mkdir(parents=True)
    print(f"✅ Created project directory: {project_dir}")

    # Create server.py
    server_content = f'''"""
{project_name} - MCP Server

A custom MCP server built with ChukMCPServer.
"""

import sys
from chuk_mcp_server import tool, resource, run


@tool
def hello(name: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {{name}}!"


@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@tool
def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        # Only allow safe operations
        allowed = {{'+', '-', '*', '/', '(', ')', '.', ' '}} | set('0123456789')
        if not all(c in allowed for c in expression):
            return "Error: Invalid characters in expression"

        result = eval(expression)
        return f"{{expression}} = {{result}}"
    except Exception as e:
        return f"Error: {{str(e)}}"


@resource("config://info")
def server_info() -> dict:
    """Get server information."""
    return {{
        "name": "{project_name}",
        "version": "0.1.0",
        "description": "Custom MCP server"
    }}


if __name__ == "__main__":
    import sys

    # Check which transport mode to use
    if "--stdio" in sys.argv or "--transport=stdio" in sys.argv:
        # Stdio mode explicitly requested
        run(transport="stdio")
    elif "--port" in sys.argv or "--host" in sys.argv or "--http" in sys.argv or "--transport=http" in sys.argv:
        # HTTP mode explicitly requested
        run()
    else:
        # Default to stdio mode (best for Claude Desktop)
        run(transport="stdio")
'''

    server_file = project_dir / "server.py"
    server_file.write_text(server_content)
    print("✅ Created server.py")

    # Create pyproject.toml
    pyproject_content = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "MCP server built with ChukMCPServer"
requires-python = ">=3.11"
dependencies = [
    "chuk-mcp-server>=0.4.2",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.8.0",
    "ruff>=0.2.0",
]

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''

    pyproject_file = project_dir / "pyproject.toml"
    pyproject_file.write_text(pyproject_content)
    print("✅ Created pyproject.toml")

    # Create README.md
    readme_content = f'''# {project_name}

MCP server built with [ChukMCPServer](https://github.com/chrishayuk/chuk-mcp-server).

## Transport Modes

This server supports two transport modes:

- **STDIO (default)**: For Claude Desktop and MCP clients. Communication via stdin/stdout.
- **HTTP**: For web applications, APIs, and cloud deployment. RESTful endpoints with streaming support.

## Quick Start

### Option 1: Claude Desktop (STDIO mode)

#### 1. Install dependencies
```bash
# Install globally
uv pip install --system chuk-mcp-server

# Or in a virtual environment (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
uv pip install chuk-mcp-server
```

#### 2. Test the server
```bash
# Default mode is stdio - perfect for Claude Desktop
echo '{{"jsonrpc":"2.0","method":"tools/list","id":1}}' | python server.py
```

#### 3. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{{
  "mcpServers": {{
    "{project_name}": {{
      "command": "uv",
      "args": ["--directory", "{project_dir.absolute()}", "run", "server.py"]
    }}
  }}
}}
```

Restart Claude Desktop and your server will be available!

### Option 2: Web/API (HTTP mode)

Perfect for web applications and cloud deployment.

```bash
# Start HTTP server on port 8000
python server.py --http

# Or specify custom port/host
python server.py --port 8000 --host 0.0.0.0
```

Test with curl:
```bash
curl http://localhost:8000/mcp \\
  -H "Content-Type: application/json" \\
  -d '{{"jsonrpc":"2.0","method":"tools/list","id":1}}'
```

### Option 3: Docker (Production Deployment)

Docker automatically runs the server in HTTP mode, perfect for production deployments.

#### Using docker-compose (easiest)
```bash
docker-compose up
```

#### Or build manually
```bash
# Build the image
docker build -t {project_name} .

# Run the container
docker run -p 8000:8000 {project_name}
```

#### Test the deployment
```bash
curl http://localhost:8000/mcp \\
  -H "Content-Type: application/json" \\
  -d '{{"jsonrpc":"2.0","method":"tools/list","id":1}}'
```

You should see:
```json
{{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {{
    "tools": [
      {{"name": "hello", "description": "Say hello to someone."}},
      {{"name": "add_numbers", "description": "Add two numbers together."}},
      {{"name": "calculate", "description": "Safely evaluate a mathematical expression."}}
    ]
  }}
}}
```

Perfect for deploying to cloud platforms like AWS, GCP, Azure, or Kubernetes!

## Available Tools

- **hello**: Say hello to someone
- **add_numbers**: Add two numbers together
- **calculate**: Safely evaluate a mathematical expression

## Available Resources

- **config://info**: Get server information

## Development

### Run tests
```bash
uv run pytest
```

### Type checking
```bash
uv run mypy server.py
```

### Linting
```bash
uv run ruff check .
```

## Command-Line Options

The server automatically detects the best transport mode, but you can override:

```bash
# Force STDIO mode (default)
python server.py --stdio
python server.py --transport=stdio

# Force HTTP mode
python server.py --http
python server.py --port 8000
python server.py --host 0.0.0.0
python server.py --transport=http
```

## Customization

Edit `server.py` to add your own tools and resources:

```python
from chuk_mcp_server import tool, resource, run

@tool
def my_custom_tool(param: str) -> str:
    """Your custom tool description."""
    return f"Result: {{param}}"

@resource("custom://data")
def my_resource() -> dict:
    """Your custom resource."""
    return {{"data": "value"}}

if __name__ == "__main__":
    run(transport="stdio")  # or just run() for auto-detection
```

See the [ChukMCPServer documentation](https://github.com/chrishayuk/chuk-mcp-server) for more examples and advanced features.
'''

    readme_file = project_dir / "README.md"
    readme_file.write_text(readme_content)
    print("✅ Created README.md")

    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff
.ruff_cache/

# OS
.DS_Store
Thumbs.db
"""

    gitignore_file = project_dir / ".gitignore"
    gitignore_file.write_text(gitignore_content)
    print("✅ Created .gitignore")

    # Create Dockerfile
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
COPY server.py ./

# Install dependencies using uv
RUN uv pip install --system --no-cache chuk-mcp-server>=0.4.2

# Expose HTTP port
EXPOSE 8000

# Run server in HTTP mode for web/API access
CMD ["python", "server.py", "--port", "8000", "--host", "0.0.0.0"]
"""

    dockerfile_file = project_dir / "Dockerfile"
    dockerfile_file.write_text(dockerfile_content)
    print("✅ Created Dockerfile")

    # Create docker-compose.yml
    docker_compose_content = f"""version: '3.8'

services:
  {project_name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_TRANSPORT=http
    restart: unless-stopped
"""

    docker_compose_file = project_dir / "docker-compose.yml"
    docker_compose_file.write_text(docker_compose_content)
    print("✅ Created docker-compose.yml")

    # Print success message with next steps
    print(f"\n🎉 Project '{project_name}' created successfully!")
    print("\n📂 Next steps:")
    print(f"   cd {project_dir.name}")
    print("   uv pip install --system chuk-mcp-server")
    print("   python server.py")
    print("\n🐳 Or run with Docker:")
    print("   docker-compose up")
    print(f"\n💡 For Claude Desktop - see {project_dir.name}/README.md for config")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="chuk-mcp-server",
        description="High-performance MCP server with stdio and HTTP transport support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new MCP server project
  uvx chuk-mcp-server init my-awesome-server

  # Run in stdio mode (for MCP clients)
  uvx chuk-mcp-server stdio

  # Run in HTTP mode on default port
  uvx chuk-mcp-server http

  # Run in HTTP mode on custom port
  uvx chuk-mcp-server http --port 9000

  # Run with specific log level (suppress INFO/DEBUG logs)
  uvx chuk-mcp-server http --log-level warning

  # Run with debug logging
  uvx chuk-mcp-server http --debug
  uvx chuk-mcp-server http --log-level debug

  # Run with minimal logging (errors only)
  uvx chuk-mcp-server http --log-level error

  # Run with custom server name
  MCP_SERVER_NAME=my-server uvx chuk-mcp-server stdio

Environment Variables:
  MCP_SERVER_NAME     Server name (default: chuk-mcp-server)
  MCP_SERVER_VERSION  Server version (default: 0.2.3)
  MCP_TRANSPORT       Force transport mode (stdio|http)
  MCP_LOG_LEVEL       Logging level (debug|info|warning|error|critical)
  MCP_STDIO          Set to 1 to force stdio mode
  USE_STDIO          Alternative to MCP_STDIO
        """,
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest="mode", help="Transport mode", required=True)

    # Stdio mode
    stdio_parser = subparsers.add_parser("stdio", help="Run in stdio mode for MCP clients")
    stdio_parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # HTTP mode
    http_parser = subparsers.add_parser("http", help="Run in HTTP mode with SSE streaming")
    http_parser.add_argument("--host", default=None, help="Host to bind to (default: auto-detect)")
    http_parser.add_argument("--port", type=int, default=None, help="Port to bind to (default: auto-detect)")
    http_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    http_parser.add_argument(
        "--log-level",
        default="warning",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level (default: warning)",
    )

    # Auto mode (detect from environment)
    auto_parser = subparsers.add_parser("auto", help="Auto-detect transport mode from environment")
    auto_parser.add_argument("--host", default=None, help="Host for HTTP mode (default: auto-detect)")
    auto_parser.add_argument("--port", type=int, default=None, help="Port for HTTP mode (default: auto-detect)")
    auto_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    auto_parser.add_argument(
        "--log-level",
        default="warning",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level (default: warning)",
    )

    # Init mode (scaffold new project)
    init_parser = subparsers.add_parser("init", help="Create a new MCP server project")
    init_parser.add_argument("project_name", help="Name of the project to create")
    init_parser.add_argument(
        "--dir", dest="directory", default=None, help="Directory to create project in (default: ./<project_name>)"
    )

    args = parser.parse_args()

    # Handle init mode separately (no server needed)
    if args.mode == "init":
        scaffold_project(args.project_name, args.directory)
        return

    # Set up logging (to stderr for stdio mode)
    setup_logging(debug=args.debug, stderr=(args.mode == "stdio"))

    # Create server
    server = create_example_server()

    # Run in appropriate mode
    if args.mode == "stdio":
        # Force stdio mode
        logging.info("Starting ChukMCPServer in STDIO mode...")
        server.run(stdio=True, debug=args.debug)

    elif args.mode == "http":
        # Force HTTP mode
        logging.info("Starting ChukMCPServer in HTTP mode...")
        server.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            stdio=False,
            log_level=getattr(args, "log_level", "warning"),
        )

    else:  # auto mode
        # Let smart config detect
        logging.info("Starting ChukMCPServer in AUTO mode...")
        server.run(
            host=getattr(args, "host", None),
            port=getattr(args, "port", None),
            debug=args.debug,
            log_level=getattr(args, "log_level", "warning"),
        )


if __name__ == "__main__":
    main()
