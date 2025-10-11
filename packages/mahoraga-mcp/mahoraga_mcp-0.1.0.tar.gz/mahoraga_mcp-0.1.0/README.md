# Mahoraga MCP - AI-Powered Mobile Automation

A Model Context Protocol (MCP) server for mobile automation testing with Mahoraga. Control Android devices and run automated tests directly from Claude Code or any MCP-compatible client using natural language.

## Features

- 🤖 **AI-Powered Automation**: Control your Android device using plain English
- 📱 **Device Connection**: Works with emulators and physical devices
- ⚙️ **Flexible Configuration**: Customize AI model, temperature, vision, reasoning, and more
- 🔄 **Real-Time Execution**: Live progress streaming during task execution
- 🎯 **Suite Execution**: Run multiple tasks in sequence with retry logic
- 📊 **Usage Tracking**: Monitor API costs and token usage
- 🔐 **Secure**: API key authentication via Mahoraga platform

## Installation

```bash
pip install mahoraga-mcp
```

All dependencies (including ADB tools, LLM frameworks, and image processing) are automatically installed.

## Quick Start

### 1. Get Your API Key

1. Visit [mahoraga.app](https://mahoraga.app) (or your deployment URL)
2. Sign in with Google
3. Go to Dashboard → API Keys
4. Create a new API key

### 2. Configure Claude Code

Add this to your MCP settings file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mahoraga": {
      "command": "mahoraga-mcp"
    }
  }
}
```

**Important**: Restart Claude Code after adding the configuration.

### 3. Start Automating

Open Claude Code and try:

```
"Setup Mahoraga and connect to my Android device"
"Configure with my API key: mhg_xxxx..."
"Execute task: Open Settings and enable WiFi"
```

## Available Tools

### 1. `build`
Setup and verify all dependencies.

**Example:**
```
Can you run the build tool to setup my system for Mahoraga?
```

### 2. `connect`
Connect to an Android device or emulator.

**Parameters:**
- `device_serial` (optional): Device serial number

**Example:**
```
Connect to my Android device
```

### 3. `configure`
Configure agent execution parameters.

**Parameters:**
- `mahoraga_api_key`: Your Mahoraga API key from the web portal
- `model`: LLM model (e.g., "anthropic/claude-sonnet-4", "openai/gpt-4o")
- `temperature`: 0-2 (default: 0.2)
- `max_steps`: Maximum execution steps (default: 15)
- `vision`: Enable screenshots (default: false)
- `reasoning`: Enable multi-step planning (default: false)
- `reflection`: Enable self-improvement (default: false)
- `debug`: Verbose logging (default: false)

**Example:**
```
Configure Mahoraga with my API key mhg_xxx, use Claude Sonnet 4, and enable vision
```

### 4. `execute`
Run an automation task on the device.

**Parameters:**
- `task`: Natural language task description

**Example:**
```
Execute task: Open Settings and navigate to WiFi settings
```

### 5. `runsuite`
Execute multiple tasks in sequence with retry logic.

**Parameters:**
- `suite_name`: Name of the test suite
- `tasks`: Array of tasks with retry and failure handling options

**Example:**
```
Run a test suite with these tasks: [
  {"prompt": "Open Settings", "type": "setup"},
  {"prompt": "Enable WiFi", "type": "test", "retries": 2},
  {"prompt": "Close Settings", "type": "teardown"}
]
```

### 6. `usage`
View API usage statistics and costs.

**Example:**
```
Show me my Mahoraga usage statistics
```

## Complete Workflow Example

```
User: "Setup Mahoraga on my machine"
→ Runs build tool
→ Returns: All dependencies installed ✓

User: "Connect to my Android emulator"
→ Runs connect tool
→ Returns: Connected to emulator-5554 ✓

User: "Configure to use Claude Sonnet 4 with vision and my API key is mhg_xxx..."
→ Runs configure tool
→ Returns: Configuration set ✓

User: "Execute task: Open Instagram and go to my profile"
→ Runs execute tool with live streaming
→ Returns: Task completed ✓

User: "Show me my usage statistics"
→ Runs usage tool
→ Returns: Total cost: $0.15, 10 executions ✓
```

## Requirements

- **Python 3.11+** - Required for the MCP server
- **Android Device** - Emulator or physical device with USB debugging enabled
- **Mahoraga API Key** - Get from [mahoraga.app](https://mahoraga.app)

Dependencies automatically installed:
- Android Debug Bridge (ADB) - via `adbutils`
- Mahoraga Portal APK - via `apkutils`
- LLM frameworks - via `llama-index`
- Image processing - via `pillow`

## Architecture

```
mahoraga-mcp/
├── src/
│   ├── server.py            # Main MCP server entry point
│   ├── backend_client.py    # API communication with Mahoraga platform
│   ├── llm_wrapper.py       # LLM integration layer
│   ├── state.py             # Session state management
│   ├── usage_tracker.py     # Usage and cost tracking
│   └── tools/
│       ├── build.py         # Dependency checker and installer
│       ├── connect.py       # Device connectivity
│       ├── configure.py     # Agent configuration
│       ├── execute.py       # Task execution
│       ├── runsuite.py      # Suite execution
│       └── usage.py         # Usage statistics
└── pyproject.toml
```

## Troubleshooting

**"No devices found"**
- Start Android emulator via Android Studio > AVD Manager
- Connect physical device with USB debugging enabled
- For WiFi debugging: `adb tcpip 5555 && adb connect <device-ip>:5555`

**"Portal not ready"**
- The `connect` tool automatically installs the Portal APK
- If it fails, manually enable the Mahoraga Portal accessibility service in Settings > Accessibility

**"Invalid API key"**
- Make sure you've run `configure` with a valid API key from mahoraga.app
- API keys start with `mhg_` prefix
- Check your API key hasn't been revoked in the web portal

## License

MIT