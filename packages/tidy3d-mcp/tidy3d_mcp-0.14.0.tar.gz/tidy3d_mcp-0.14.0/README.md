# Tidy3D MCP

A local Model Context Protocol (MCP) server that lets clients drive the
Flexcompute Tidy3D viewer and consume viewer artifacts without needing a browser session.

## Capabilities

- Authenticates against the remote FlexAgent MCP endpoint using your Tidy3D API key.
- Proxies viewer automation commands such as launching the viewer, rotating the camera,
  toggling structure visibility, running simulation health checks, and capturing screenshots.
- Returns viewer captures as MCP images so downstream tools can consume them immediately.

## Requirements

- Python 3.10 or newer
- [`uv`](https://github.com/astral-sh/uv) for dependency management
- Network access to the target FlexAgent MCP deployment (defaults to the hosted
  `https://flexagent.dev-simulation.cloud/` endpoint)

## Installation

```bash
uv sync
```

This resolves the project environment and installs the `tidy3d-mcp` console entry point.

## Usage

Start the server from the project root and supply your API key (see
[Tidy3D installation docs](https://docs.flexcompute.com/projects/tidy3d/en/latest/install.html) for
instructions to obtain it):

```bash
uv run tidy3d-mcp -- --api-key YOUR_TIDY3D_API_KEY
```

The server listens on stdio for MCP requests and forwards them to the remote FlexAgent server using
the provided API key for authentication.

### Enabling Viewer Automation

Viewer-facing tools are opt-in. Launch the proxy with `--enable-viewer` to activate them. Pair the
flag with `--host vscode` (default) or `--host cursor`, depending on which desktop is available to
handle the deeplink. When the flag is present the server:

1. Chooses a free localhost port.
2. Opens a `vscode://Flexcompute.tidy3d/bridge?...` or
   `cursor://Flexcompute.tidy3d/bridge?...` URI so the desktop extension can own the bridge on
   that port and expose the HTTP endpoint.
3. Waits (15s max) for the extension to acknowledge the port by standing up the `/viewer/*` bridge.

If the deeplink cannot be handled or the bridge never binds, viewer tools are skipped and the proxy
continues as a simple API gateway.

### Integrating with MCP Hosts

- **VS Code / Cursor**: Select the "Tidy3D MCP" binary (`uv run tidy3d-mcp`) when
  configuring an stdio MCP provider.
- **Custom hosts**: Launch the command above and connect using the Model Context Protocol over the
  process stdio pipes.

## Configuration

Environment variables control the server at startup:

| Variable | Purpose | Default |
| --- | --- | --- |
| `REMOTE_MCP_URL` | Target MCP endpoint to proxy. | `https://flexagent.dev-simulation.cloud/` |

Pass `--api-key` whenever you launch the server. Viewer tooling is available only when
`--enable-viewer` is provided **and** the Tidy3D extension accepts the bridge deeplink.
Hosts that wrap the binary must forward both arguments when spawning the process.

## Tools Exposed to Clients

| Tool | Availability | Description |
| --- | --- | --- |
| `validate_simulation` | Requires `--enable-viewer` | Launches or re-checks a simulation, returning the `viewer_id`, diagnostic status, warnings, and the evaluated code slice. |
| `rotate_viewer` | Requires `--enable-viewer` | Rotates the active viewer toward the requested direction (e.g. `TOP`, `BOTTOM`). |
| `show_structures` | Requires `--enable-viewer` | Applies a boolean visibility array to the current viewer structures. |
| `capture` | Requires `--enable-viewer` | Captures the current frame of the viewer. |

## Development Tips

- Run `uv run ruff check` to lint the project and `uv run ruff format` to apply formatting.
- The server relies on `fastmcp.as_proxy`; consult the upstream FastMCP documentation for advanced
  configuration such as custom authentication flows or additional transports.
- When debugging viewer interactions, inspect the returned `data_url` to confirm that capture
  payloads reach the client.

## Troubleshooting

- **API key rejected**: Confirm the key is current by visiting the Tidy3D account page and copying a
  fresh key. Keys can be regenerated through the web interface if needed.
- **Viewer fails to start**: Verify the simulation file exists, the MCP host provides the correct
  working directory, and the remote FlexAgent endpoint is reachable.
