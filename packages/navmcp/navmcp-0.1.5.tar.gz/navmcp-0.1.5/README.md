# navmcp --- A purely Python-based browser automation tool using MCP

---

## Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [License](#license)

A Model Context Protocol (MCP) server that provides browser automation tools over SSE (Server-Sent Events). Built with FastMCP and Selenium, this server enables MCP-capable clients to interact with web pages, extract content, perform automated browser tasks, and access academic search engines.

## Features

- **SSE Transport**: MCP server over SSE (Server-Sent Events) via FastMCP
- **Browser Automation**: Selenium-powered Chrome automation with headless support
- **Comprehensive Toolset** (15 tools):

  - `fetch_url`: Navigate to a URL using a real browser and retrieve the final page content, title, and metadata (handles redirects, bot protection, errors).
  - `find_elements`: Parse the current or specified web page and extract detailed information about elements using CSS selectors or XPath (text, attributes, HTML, visibility).
  - `click_element`: Find and click a page element (button, link, form, etc.), optionally waiting for post-click changes; returns updated page state and metadata.
  - `run_js_interaction`: Execute custom JavaScript in the browser context, with argument support and JSON-serializable results; ideal for advanced DOM interactions.
  - `download_pdfs`: Download PDF files from web pages using multiple strategies (auto-detect, custom selector, or JavaScript-triggered); returns file info and metadata.
  - `web_search`: Perform general web searches using Google or Bing; returns structured results (title, URL, snippet) and metadata.
  - `paper_search`: Search academic literature across Google Scholar, PubMed, IEEE, arXiv, medRxiv, and bioRxiv; returns structured results and metadata.
  - `convert_to_markdown`: Convert HTML content, web pages, or PDFs to Markdown format using MarkItDown; supports URLs and raw HTML.
  - `convert_file_to_markdown`: Convert a local HTML or PDF file to Markdown and write to output; supports extracting specific HTML elements by ID.
  - `save_file`: Save raw content to a file at the specified path (supports large files, returns metadata).
  - `fetch_and_save_url`: Fetch content from a URL (using browser automation) and save it directly to a file.
  - `start_browser`: Start the Selenium browser session (if not already running).
  - `stop_browser`: Stop the Selenium browser session (not the server).
  - `restart_browser`: Restart the Selenium browser session (not the server).
  - `shutdown_server`: Gracefully shut down the MCP server process (safe for automation workflows).
- **Academic Focus**: Specialized search capabilities for research papers and scholarly content
- **Security**: URL validation, domain allowlists, and private IP blocking
- **Robust Error Handling**: Comprehensive error handling and retry logic
- **Smart Driver Management**: Selenium Manager with webdriver-manager fallback

## Quick Start

### Installation

1. **Install from PyPI:**
```powershell
pip install navmcp
```

2. **Configure environment (optional):**
```powershell
copy .env.example .env
# Edit .env with your preferences
```

3. **Start the server:**
```powershell
python -m navmcp start
```

#### Headless/GUI Mode

To run the browser in headless mode (default):
```powershell
python -m navmcp start --headless
```

To run the browser with GUI (not headless):
```powershell
python -m navmcp start --no-headless
```

> **Note:** Headless mode is now only controlled by command parameters (`--headless` or `--no-headless`). The `BROWSER_HEADLESS` environment variable is no longer used.

4. **Verify it's running:**
```powershell
# Health check
curl http://127.0.0.1:3333/health

# SSE endpoint check 
curl http://127.0.0.1:3333/sse
```

### Alternative Start Methods
```powershell
# Using fastmcp SSE directly (if your fastmcp version supports it)
py -m fastmcp sse navmcp.app:app --host 127.0.0.1 --port 3333

# Using the __main__ module
python -m navmcp
```

## Client Configuration

### MCP Client Configuration

For Cline, Continue, VS Code Copilot Chat, and CodeGeeX, refer to the [`mcp.json`](./configs/mcp.json) file in this repository for the recommended MCP server configuration.  
- **VS Code Copilot Chat**: Copy or adapt the configuration from [`mcp.json`](./mcp.json) to your workspace/.vscode/.

- **Cline / Continue**: Use the configuration in [`cline_mcp_settings.json`](./configs/cline_mcp_settings.json) for your `cline_mcp_settings.json`. Or configure MCP server through the cline interface.
- 
- **CodeGeeX**: Use the details from [`mcp.json`](./mcp.json) for your MCP server setup (location varies by version).

This ensures that all clients use the same configuration and remain up-to-date.

## Configuration

### Configuration Options

You can configure the server using either a `.env` file or by setting environment variables directly before starting the server.  
Most options can also be set as environment variables in your shell.

```bash
# Example .env file or environment variables:
MCP_PORT=3333
MCP_HOST=127.0.0.1
DOWNLOAD_DIR=.data\downloads
PAGE_LOAD_TIMEOUT_S=30
SCRIPT_TIMEOUT_S=30
MCP_ALLOWED_HOSTS=
MCP_CORS_ORIGINS=http://127.0.0.1,http://localhost
```

> **Note:** The `BROWSER_HEADLESS` environment variable is deprecated and no longer used. Use command-line parameters to control headless mode.

For advanced usage, check whether your server start command supports passing these options as command-line arguments.

### Browser Configuration

The server automatically:
- Uses Chrome with Selenium Manager (Selenium ≥4.6) for driver management
- Falls back to webdriver-manager on Windows if needed
- Configures headless mode for CI and server environments
- Sets up automatic PDF downloads without prompts
- Creates download directories as needed

### Security Features

- **URL Validation**: Blocks invalid, file://, data:, and javascript: URLs
- **Private IP Blocking**: Prevents access to local/private IP ranges by default
- **Domain Allowlists**: Optional restriction to specific hosts using `MCP_ALLOWED_HOSTS`
- **Rate Limiting**: Built-in protections against abuse

## MCP Tool Schema

All MCP tools now use explicit Annotated parameters with Pydantic Field annotations for proper schema exposure and validation.

## Troubleshooting

### Server Issues
- **Server won't start**: Check if port 3333 is available, verify your Python environment, and ensure all dependencies in `requirements.txt` are installed.
- **Browser errors**: Make sure Chrome is installed and up-to-date. Selenium Manager (Selenium ≥4.6) should auto-manage drivers, but on Windows, `webdriver-manager` is used as fallback.
- **Download issues**: Ensure `.data/downloads` directory exists and is writable. If you encounter permission errors, run your shell as an administrator.
- **Structured output errors**: If tool results are not returned as JSON, check your return type annotations and output schemas.
- **Async errors**: For asynchronous tools, ensure you are not blocking the event loop with synchronous code. Use `anyio.to_thread.run_sync` for CPU-bound tasks.

### Client Integration
- **Tools not showing**: Confirm the server is running and accessible at `http://127.0.0.1:3333/`. Use `/health` and `/sse` endpoints to verify.
- **CORS errors**: Add your client's origin to `MCP_CORS_ORIGINS` in your `.env` file or environment configuration.
- **Timeout errors**: Increase timeout values in your environment configuration if requests are slow or failing.
- **Schema validation errors**: Ensure your client sends parameters matching the tool's schema (see tool docs or `/sse` endpoint).

### Common Commands
```powershell
# Check server health
curl http://127.0.0.1:3333/health

# Check SSE endpoint (tools/list requires MCP client)
curl http://127.0.0.1:3333/sse

# Run all tests
pytest tests/
```

> For more help, see the [FastMCP documentation](https://gofastmcp.com/servers/tools) and Selenium [driver docs](https://www.selenium.dev/documentation/webdriver/getting_started/).

## Requirements

- **Python**: ≥3.10
- **Chrome**: Must be installed (or automatically managed by Selenium Manager)
- **Dependencies**: See `requirements.txt`
- **Operating System**: Windows (PowerShell commands), adaptable to other OSes

## License

This project is licensed under the terms of the MIT License. See [LICENSE](./LICENSE) for details.

## Author & Contact

- **Author:** Jianlin Shi
- **GitHub:** [jianlins](https://github.com/jianlins)
- **Project Issues:** [GitHub Issues](https://github.com/jianlins/navmcp/issues)
- **Email:** your-email@example.com

## Useful Links

- [FastMCP Documentation](https://gofastmcp.com/servers/tools)
- [Selenium WebDriver Docs](https://www.selenium.dev/documentation/webdriver/getting_started/)
- [MarkItDown Library](https://github.com/microsoft/markitdown)
- [Pydantic Docs](https://docs.pydantic.dev/)

## Developer Documentation

See [DEV_README.md](./DEV_README.md) for development, contribution, and changelog information.
