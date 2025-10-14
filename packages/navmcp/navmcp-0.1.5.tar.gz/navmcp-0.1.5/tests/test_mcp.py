import json
import sys
import subprocess

# Test MCP server stdio mode
def test_mcp_server():
    print("Testing MCP server stdio mode...")
    
    # Start the server process
    cmd = [sys.executable, "-m", "navmcp", "start", "--transport", "stdio"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Send initialize message
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    proc.stdin.write(json.dumps(init_msg) + "\n")
    proc.stdin.flush()
    
    # Read response
    response = proc.stdout.readline()
    print(f"Response: {response.strip()}")
    
    # Test tools/list
    tools_msg = {
        "jsonrpc": "2.0", 
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    proc.stdin.write(json.dumps(tools_msg) + "\n")
    proc.stdin.flush()
    
    # Read tools response
    tools_response = proc.stdout.readline()
    print(f"Tools response: {tools_response.strip()}")
    
    proc.terminate()
    return True

if __name__ == "__main__":
    test_mcp_server()
