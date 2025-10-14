"""
MCP Browser Tools Server CLI

Command-line interface for starting the MCP Browser Tools server.
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# uvicorn will be imported only when needed for HTTP transport

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
    prog="navmcp",
        description="MCP Browser Tools Server - Browser automation tools for MCP clients"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start the MCP server")
    start_parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="sse",
        help="Transport protocol to use (default: sse)"
    )
    start_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1, ignored for stdio transport)"
    )
    start_parser.add_argument(
        "--port",
        type=int,
        default=3333,
        help="Port to bind to (default: 3333, ignored for stdio transport)"
    )
    start_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    start_parser.add_argument(
        "--log-level",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        default="info",
        help="Log level (default: info)"
    )
    headless_group = start_parser.add_mutually_exclusive_group()
    headless_group.add_argument(
        "--headless",
        dest="headless",
        action="store_true",
        default=None,
        help="Run browser in headless mode (default: true)"
    )
    headless_group.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        default=None,
        help="Run browser with GUI (not headless)"
    )
    
    return parser


def start_server(transport: str, host: str, port: int, reload: bool = False, log_level: str = "info", headless: bool | None = None) -> None:
    """Start the MCP server using the specified transport."""
    print(f"Starting MCP Browser Tools Server...")
    print(f"Transport: {transport}")
    if transport != "stdio":
        print(f"Host: {host}")
        print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Log level: {log_level}")
    print(f"Headless: {headless}")
    print()

    # Set environment variables for the app to read
    os.environ["MCP_TRANSPORT"] = transport
    if headless is not None:
        os.environ["BROWSER_HEADLESS"] = str(headless).lower()

    try:
        if transport == "stdio":
            # For stdio transport, run the FastMCP server directly
            from navmcp.app import run_stdio_server
            run_stdio_server()
        else:
            # For HTTP/SSE transport, use uvicorn
            try:
                import uvicorn
            except ImportError:
                print("Error: uvicorn is required for HTTP/SSE transport. Please run: pip install -r requirements.txt")
                sys.exit(1)
            
            # Set environment variables for port and host
            os.environ["MCP_HOST"] = host
            os.environ["MCP_PORT"] = str(port)
            
            uvicorn.run(
                "navmcp.app:app",
                host=host,
                port=port,
                reload=reload,
                log_level=log_level,
                access_log=True
            )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "start":
        start_server(
            transport=args.transport,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            headless=args.headless
        )
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
