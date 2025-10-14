# Mobile-Use MCP Server

A Model Context Protocol (MCP) server that provides AI-powered mobile device screen analysis. Automatically detects connected Android (via ADB) and iOS devices (via xcrun), captures screenshots, and analyzes them using vision language models.

## Features

- **🔍 Device Discovery**: Automatically finds connected Android devices (ADB) and iOS simulators (xcrun)
- **📱 Screen Analysis**: Capture and analyze device screenshots using vision-capable LLMs
- **🤖 Natural Language Control**: Execute commands on your device using natural language via the mobile-use SDK
- **🚀 Easy Integration**: Built with FastMCP for seamless MCP protocol implementation
- **⚙️ Flexible Configuration**: Uses Minitap API with support for various vision models

## Installation

### Prerequisites

- **Python 3.12+**
- **uv** (recommended) or pip
- **For Android**: ADB installed and accessible
- **For iOS**: Xcode Command Line Tools (macOS only)
- **Minitap API Key** - Get one at [platform.minitap.ai](https://platform.minitap.ai)

### Setup

1. **Clone and navigate to the project:**

```bash
cd mobile-use-mcp
```

2. **Install dependencies:**

```bash
# Create a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```

3. **Configure for MCP usage:**

The MCP server is configured via environment variables passed from your MCP client (e.g., Windsurf). 

Required environment variable:
- `MINITAP_API_KEY`: Your Minitap API key

Optional environment variables:
- `MINITAP_API_BASE_URL`: API base URL (default: `https://platform.minitap.ai/api/v1`)
- `VISION_MODEL`: Vision model to use (default: `baidu/ernie-4.5-vl-28b-a3b`)
- `ADB_SERVER_SOCKET`: Custom ADB server socket (format: `tcp:host:port`)

## Available Resources & Tools

### Resource: `data://devices`

Lists all connected mobile devices (Android and iOS).

**Returns:** Array of device information objects with:
- `device_id`: Device serial (Android) or UDID (iOS)
- `platform`: `"android"` or `"ios"`
- `name`: Device name
- `state`: Device state (`"connected"` or `"Booted"`)

### Tool: `analyze_screen`

Captures a screenshot from a mobile device and analyzes it using a vision language model.

**Parameters:**
- `prompt` (required): Analysis prompt describing what information to extract
- `device_id` (optional): Specific device ID to target. If not provided, uses the first available device.

**Returns:** AI-generated analysis of the screenshot based on the prompt.

**Example:**
```
Prompt: "What app is currently open? List all visible UI elements."
```

The tool will:
1. Find the specified device (or first available)
2. Capture a screenshot
3. Analyze it with the vision model
4. Return the analysis

### Tool: `execute_mobile_command`

Execute natural language commands on your mobile device using the mobile-use SDK. This tool allows you to control your Android or iOS device with simple instructions.

**Parameters:**
- `goal` (required): Natural language command to execute on the device
- `output_description` (optional): Description of the expected output format (e.g., "A JSON list of objects with sender and subject keys")
- `profile` (optional): Name of the profile to use for this task. Defaults to 'default'

**Returns:** Execution result with status, output, and any extracted data.

**Examples:**
```python
# Simple command
goal: "Go to settings and tell me my current battery level"

# Data extraction with structured output
goal: "Open Gmail, find first 3 unread emails, and list their sender and subject line"
output_description: "A JSON list of objects, each with 'sender' and 'subject' keys"

# App navigation
goal: "Open Twitter and scroll to the latest tweet"
```

The tool will:
1. Find the specified device (or first available)
2. Execute the command using the mobile-use AI agent
3. Return the result or extracted data

## Usage

### Running the MCP Server

#### Local Mode (Default)

The MCP server is typically started by your MCP client (e.g., Windsurf). For manual testing:

```bash
minitap-mcp
```

#### Network Server Mode

You can run the MCP server as a network server for remote access:

```bash
# Run as network server (uses MCP_SERVER_HOST and MCP_SERVER_PORT from env)
minitap-mcp --server
```

The server will bind to the host and port specified in your environment variables:
- `MCP_SERVER_HOST` (default: `0.0.0.0`)
- `MCP_SERVER_PORT` (default: `8000`)

Configure these in your `.env` file or via environment variables to customize the binding address.

Inside Windsurf, you can configure the MCP server by adding the following to your `~/.codeium/windsurf/mcp_settings.json` file:

```json
{
  "mcpServers": {
    "minitap-mcp": {
      "serverUrl": "http://localhost:8000/mcp"
    }
  }
}
```

N.B. You may need to change the port based on what you've configured in your `.env` file.

## Development

### Quick Testing

Test device detection and screenshot capture (no API key required):

```bash
python tests/test_devices.py
```

Test the complete MCP flow with LLM analysis (requires API key):

```bash
cp .env.example .env
# Edit .env and add your MINITAP_API_KEY
python tests/test_mcp.py
```

### Code Quality

**Format code:**
```bash
ruff format .
```

**Lint:**
```bash
ruff check --fix
```

## Project Structure

```
minitap/mcp/
├── __init__.py
├── main.py                    # FastMCP server entry point
├── core/
│   ├── __init__.py
│   ├── config.py              # Pydantic settings configuration
│   ├── decorators.py          # Error handling decorators
│   ├── device.py              # Device discovery & screenshot capture
│   ├── llm.py                 # LLM client initialization
│   └── utils.py               # Utility functions (image compression, etc.)
└── tools/
    ├── __init__.py
    ├── analyze_screen.py      # Screen analysis tool
    ├── execute_mobile_command.py  # Mobile-use SDK integration tool
    └── screen_analyzer.md     # System prompt for analysis

tests/
├── test_devices.py            # Device detection tests
└── test_mcp.py                # Full MCP integration tests
```

## Creating New Tools

When adding new MCP tools, use the `@handle_tool_errors` decorator to prevent unhandled exceptions from causing infinite loops:

```python
from minitap.mcp.core.decorators import handle_tool_errors
from minitap.mcp.main import mcp

@mcp.tool(name="my_tool", description="...")
@handle_tool_errors  # Add this decorator
async def my_tool(param: str) -> str:
    # Your tool logic here
    # Any exception will be caught and returned as an error message
    return "result"
```

The decorator automatically:
- Catches all exceptions (including `DeviceNotFoundError`)
- Returns user-friendly error messages
- Prevents the MCP server from hanging or looping infinitely
- Works with both sync and async functions

## Integration with Windsurf

To use this MCP server in Windsurf, add it to your MCP settings:

**Location:** `~/.codeium/windsurf/mcp_settings.json`

**Configuration:**

```json
{
  "mcpServers": {
    "minitap-mcp": {
      "command": "uv",
      "args": ["-c", "cd /path/to/minitap-mcp && source .venv/bin/activate && uv sync && minitap-mcp"],
      "env": {
        "MINITAP_API_KEY": "your_minitap_api_key_here",
        "MINITAP_API_BASE_URL": "https://platform.minitap.ai/api/v1",
        "VISION_MODEL": "baidu/ernie-4.5-vl-28b-a3b" // optional
      }
    }
  }
}
```

**After configuration:**
1. Restart Windsurf
2. The `analyze_screen` and `execute_mobile_command` tools will be available in Cascade
3. The `data://devices` resource will list connected devices

### Available Vision Models

The Minitap API supports various vision models:
- `qwen/qwen-2.5-vl-7b-instruct` (default)
- `baidu/ernie-4.5-vl-28b-a3b`
- `openai/gpt-4o`
- And more - check the Minitap platform for the full list

## Device Requirements

### Android Devices

**Requirements:**
- ADB installed and in PATH
- USB debugging enabled on the device
- Device connected via USB or network ADB

**Verify connection:**
```bash
adb devices
```

**Custom ADB Server:**
If using a custom ADB server (e.g., Docker, WSL), set the socket:
```bash
export ADB_SERVER_SOCKET="tcp:localhost:5037"
```

N.B. You may need to reboot your IDE

### iOS Devices

**Requirements:**
- macOS with Xcode Command Line Tools
- iOS Simulator running

**Verify simulators:**
```bash
xcrun simctl list devices booted
```

**Start a simulator:**
```bash
open -a Simulator
```

## Troubleshooting

### No devices found

1. **Android:** Run `adb devices` to verify device connection
2. **iOS:** Run `xcrun simctl list devices booted` to check running simulators
3. Ensure USB debugging is enabled (Android)
4. Try restarting ADB: `adb kill-server && adb start-server`

### Screenshot capture fails

1. Ensure device screen is unlocked
2. For Android, verify screencap permission
3. For iOS, ensure simulator is fully booted

### Tool not detected in Windsurf

1. Verify the import in `main.py` includes the tools module
2. Check that `tools/__init__.py` exists
3. Restart Windsurf after configuration changes
