# WorkspaceFlow - Python Backend

Pluggable workspace/project management for Python web applications with team-based access control and data isolation.

## Features

- ✅ **Workspace/Project Management** - Create and manage projects within organizations
- ✅ **Team-Based Access Control** - Assign teams to workspaces for granular access
- ✅ **Data Isolation** - Automatic workspace-scoped data filtering with `WorkspaceScopedMixin`
- ✅ **AuthFlow Integration** - Seamless integration with authflow for authentication
- ✅ **FastAPI Ready** - One-line setup with FastAPI applications
- ✅ **Type Safe** - Full type hints with SQLAlchemy 2.0 and Pydantic v2

## Installation

```bash
pip install workspaceflow
```

## Quick Start

```python
from fastapi import FastAPI
from authflow import setup_auth
from workspaceflow import setup_workspaces

app = FastAPI()

# 1. Setup authentication
authflow = setup_auth(app, preset="multi_tenant")

# 2. Setup workspace management
setup_workspaces(app, authflow=authflow)
```

## Documentation

See [examples/fastapi_basic](examples/fastapi_basic/) for a complete working example.

## License

MIT
