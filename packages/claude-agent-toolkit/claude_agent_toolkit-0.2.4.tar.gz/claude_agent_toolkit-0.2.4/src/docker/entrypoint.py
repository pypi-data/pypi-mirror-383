#!/usr/bin/env python3
# entrypoint.py - Entry point script that runs inside the Docker container

import asyncio
import json
import os
import sys
from claude_agent_sdk import query, ClaudeAgentOptions

# Model ID mappings removed - now handled in executor.py


async def main():
    """Main function that runs inside the Docker container."""
    
    # Get configuration from environment variables
    prompt = os.environ.get('AGENT_PROMPT', '')
    mcp_servers_json = os.environ.get('MCP_SERVERS', '{}')
    allowed_tools_json = os.environ.get('ALLOWED_TOOLS', '[]')
    oauth_token = os.environ.get('CLAUDE_CODE_OAUTH_TOKEN', '')
    system_prompt = os.environ.get('AGENT_SYSTEM_PROMPT')
    model = os.environ.get('ANTHROPIC_MODEL', None)
    
    if not prompt:
        print("ERROR: No prompt provided - AGENT_PROMPT environment variable is empty", file=sys.stderr, flush=True)
        return
    
    if not oauth_token:
        print("ERROR: No OAuth token provided - CLAUDE_CODE_OAUTH_TOKEN environment variable is empty", file=sys.stderr, flush=True)
        return
    
    # Parse MCP servers configuration
    try:
        mcp_servers = json.loads(mcp_servers_json)
    except json.JSONDecodeError as e:
        print(f"[entrypoint] Warning: Invalid JSON in MCP_SERVERS: {e}", file=sys.stderr, flush=True)
        mcp_servers = {}
    
    # Parse allowed tools list
    try:
        allowed_tools = json.loads(allowed_tools_json)
    except json.JSONDecodeError as e:
        print(f"[entrypoint] Warning: Invalid JSON in ALLOWED_TOOLS: {e}", file=sys.stderr, flush=True)
        allowed_tools = []
    
    # Use MCP servers configuration directly - no need to build it
    if mcp_servers:
        for server_name, config in mcp_servers.items():
            print(f"[entrypoint] Using MCP server {server_name} with config: {config}", file=sys.stderr, flush=True)

            # Test connectivity for HTTP-based servers
            if config.get("type") == "http":
                try:
                    import httpx
                    with httpx.Client(timeout=5.0) as client:
                        health_url = config["url"].replace('/mcp', '/health')
                        response = client.get(health_url)
                        print(f"[entrypoint] Health check for {server_name}: {response.status_code}", file=sys.stderr, flush=True)
                except httpx.TimeoutException:
                    print(f"[entrypoint] Health check timeout for {server_name}", file=sys.stderr, flush=True)
                except httpx.RequestError as e:
                    print(f"[entrypoint] Health check connection error for {server_name}: {e}", file=sys.stderr, flush=True)
                except Exception as e:
                    print(f"[entrypoint] Health check failed for {server_name}: {e}", file=sys.stderr, flush=True)
    
    # Setup Claude Code options with proper MCP configuration
    print(f"[entrypoint] MCP servers config: {json.dumps(mcp_servers, indent=2)}", file=sys.stderr, flush=True)
    print(f"[entrypoint] Allowed tools: {json.dumps(allowed_tools, indent=2)}", file=sys.stderr, flush=True)
    print(f"[entrypoint] Using model: {model}", file=sys.stderr, flush=True)

    options = ClaudeAgentOptions(
        allowed_tools=allowed_tools if allowed_tools else None,
        mcp_servers=mcp_servers if mcp_servers else {},
        system_prompt=system_prompt,
        model=model
    )
    
    print(f"[entrypoint] Claude Code options - allowed_tools: {options.allowed_tools}", file=sys.stderr, flush=True)
    print(f"[entrypoint] Claude Code options - mcp_servers: {len(options.mcp_servers)} servers", file=sys.stderr, flush=True)
    
    def serialize_message(message):
        """Convert a claude-code-sdk message to a serializable dict."""
        def default_serializer(obj):
            """Custom serializer for objects that aren't JSON serializable by default."""
            if hasattr(obj, '__dict__'):
                result = {"type": type(obj).__name__}
                result.update(obj.__dict__)
                return result
            return str(obj)
        
        return json.loads(json.dumps(message, default=default_serializer))
    
    try:
        print(f"[entrypoint] Starting Claude Code query with {len(mcp_servers)} MCP servers...", file=sys.stderr, flush=True)
        
        async for message in query(prompt=prompt, options=options):
            # Serialize and output each message as JSON to stdout
            message_dict = serialize_message(message)
            print(json.dumps(message_dict), flush=True)
            
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())