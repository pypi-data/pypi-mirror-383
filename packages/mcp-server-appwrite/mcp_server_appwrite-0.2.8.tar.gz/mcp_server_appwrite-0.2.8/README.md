# Appwrite MCP server

mcp-name: io.github.appwrite/mcp-for-api

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/install-mcp?name=appwrite&config=eyJjb21tYW5kIjoidXZ4IG1jcC1zZXJ2ZXItYXBwd3JpdGUgLS11c2VycyIsImVudiI6eyJBUFBXUklURV9BUElfS0VZIjoiPHlvdXItYXBpLWtleT4iLCJBUFBXUklURV9QUk9KRUNUX0lEIjoiPHlvdXItcHJvamVjdC1pZD4iLCJBUFBXUklURV9FTkRQT0lOVCI6Imh0dHBzOi8vPFJFR0lPTj4uY2xvdWQuYXBwd3JpdGUuaW8vdjEifX0%3D)

## Overview

A Model Context Protocol server for interacting with Appwrite's API. This server provides tools to manage databases, users, functions, teams, and more within your Appwrite project.

## Quick Links
- [Configuration](#configuration)
- [Installation](#installation)
- IDE Integration:
  - [Claude Desktop](#usage-with-claude-desktop)
  - [Cursor](#usage-with-cursor)
  - [Windsurf Editor](#usage-with-windsurf-editor)
  - [VS Code](#usage-with-vs-code)
- [Local Development](#local-development)
- [Debugging](#debugging)

## Configuration

> Before launching the MCP server, you must setup an [Appwrite project](https://cloud.appwrite.io/) and create an API key with the necessary scopes enabled.

Create a `.env` file in your working directory and add the following:

```env
APPWRITE_PROJECT_ID=your-project-id
APPWRITE_API_KEY=your-api-key
APPWRITE_ENDPOINT=https://<REGION>.cloud.appwrite.io/v1
```

Then, open your terminal and run the following command

### Linux and MacOS

```sh
source .env
```

### Windows

#### Command Prompt

```cmd
for /f "tokens=1,2 delims==" %A in (.env) do set %A=%B
```

#### PowerShell

```powershell
Get-Content .\.env | ForEach-Object {
  if ($_ -match '^(.*?)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
  }
}
```

## Installation

### Using uv (recommended)
When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-appwrite*.

```bash
uvx mcp-server-appwrite [args]
```

### Using pip

```bash
pip install mcp-server-appwrite
```
Then run the server using 

```bash
python -m mcp_server_appwrite [args]
```

### Command-line arguments

Both the `uv` and `pip` setup processes require certain arguments to enable MCP tools for various Appwrite APIs.

> When an MCP tool is enabled, the tool's definition is passed to the LLM, using up tokens from the model's available context window. As a result, the effective context window is reduced.  
>  
> The default Appwrite MCP server ships with only the Databases tools (our most commonly used API) enabled to stay within these limits. Additional tools can be enabled by using the flags below.

| Argument | Description |
| --- | --- |
| `--tables-db` | Enables the TablesDB API |
| `--users` | Enables the Users API |
| `--teams` | Enables the Teams API |
| `--storage` | Enables the Storage API |
| `--functions` | Enables the Functions API |
| `--messaging` | Enables the Messaging API |
| `--locale` | Enables the Locale API |
| `--avatars` | Enables the Avatars API |
| `--sites` | Enables the Sites API |
| `--all` | Enables all Appwrite APIs |
| `--databases` | Enables the Legacy Databases API |

## Usage with Claude Desktop

In the Claude Desktop app, open the app's **Settings** page (press `CTRL + ,` on Windows or `CMD + ,` on MacOS) and head to the **Developer** tab. Clicking on the **Edit Config** button will take you to the `claude_desktop_config.json` file, where you must add the following:

```json
{
  "mcpServers": {
    "appwrite": {
      "command": "uvx",
      "args": [
        "mcp-server-appwrite"
      ],
      "env": {
        "APPWRITE_PROJECT_ID": "<YOUR_PROJECT_ID>",
        "APPWRITE_API_KEY": "<YOUR_API_KEY>",
        "APPWRITE_ENDPOINT": "https://<REGION>.cloud.appwrite.io/v1" // Optional
      }
    }
  }
}

```

> Note: In case you see a `uvx ENOENT` error, ensure that you either add `uvx` to the `PATH` environment variable on your system or use the full path to your `uvx` installation in the config file.

Upon successful configuration, you should be able to see the server in the list of available servers in Claude Desktop.

![Claude Desktop Config](images/claude-desktop-integration.png)

## Usage with [Cursor](https://www.cursor.com/)

Head to Cursor `Settings > MCP` and click on **Add new MCP server**. Choose the type as `Command` and add the command below to the **Command** field.

- **MacOS**

```bash
env APPWRITE_API_KEY=your-api-key env APPWRITE_PROJECT_ID=your-project-id uvx mcp-server-appwrite
```

- **Windows**

```cmd
cmd /c SET APPWRITE_PROJECT_ID=your-project-id && SET APPWRITE_API_KEY=your-api-key && uvx mcp-server-appwrite
```

![Cursor Settings](./images/cursor-integration.png)

## Usage with [Windsurf Editor](https://codeium.com/windsurf)

Head to Windsurf `Settings > Cascade > Model Context Protocol (MCP) Servers` and click on **View raw config**. Update the `mcp_config.json` file to include the following:

```json
{
  "mcpServers": {
    "appwrite": {
      "command": "uvx",
      "args": [
        "mcp-server-appwrite"
      ],
      "env": {
        "APPWRITE_PROJECT_ID": "<YOUR_PROJECT_ID>",
        "APPWRITE_API_KEY": "<YOUR_API_KEY>",
        "APPWRITE_ENDPOINT": "https://<REGION>.cloud.appwrite.io/v1" // Optional
      }
    }
  }
}
```

![Windsurf Settings](./images/windsurf-integration.png)

## Usage with [VS Code](https://code.visualstudio.com/)

### Configuration

1. **Update the MCP configuration file**: Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`) and run `MCP: Open User Configuration`. It should open the `mcp.json` file in your user settings.

2. **Add the Appwrite MCP server configuration**: Add the following to the `mcp.json` file:

```json
{
  "servers": {
    "appwrite": {
      "command": "uvx",
      "args": ["mcp-server-appwrite", "--users"],
      "env": {
        "APPWRITE_PROJECT_ID": "<YOUR_PROJECT_ID>",
        "APPWRITE_API_KEY": "<YOUR_API_KEY>",
        "APPWRITE_ENDPOINT": "https://<REGION>.cloud.appwrite.io/v1"
      }
    }
  }
}
```

3. **Start the MCP server**: Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`) and run `MCP: List Servers`. In the dropdown, select `appwrite` and click on the **Start Server** button.

4. **Use in Copilot Chat**: Open Copilot Chat and switch to **Agent Mode** to access the Appwrite tools.

![VS Code Settings](./images/vs-code-integration.png)

## Local Development

### Clone the repository

```bash
git clone https://github.com/appwrite/mcp.git
```

### Install `uv`

- Linux or MacOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Prepare virtual environment

First, create a virtual environment.

```bash
uv venv
```

Next, activate the virtual environment.

- Linux or MacOS

```bash
source .venv/bin/activate
```

- Windows

```powershell
.venv\Scripts\activate
```

### Run the server

```bash
uv run -v --directory ./ mcp-server-appwrite
```

## Debugging

You can use the MCP inspector to debug the server. 

```bash
npx @modelcontextprotocol/inspector \
  uv \
  --directory . \
  run mcp-server-appwrite
```

Make sure your `.env` file is properly configured before running the inspector. You can then access the inspector at `http://localhost:5173`.

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
