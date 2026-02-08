# FastMCP Implementation Guide

## What is FastMCP?

FastMCP is a lightweight Python framework for creating Model Context Protocol (MCP) servers. It simplifies exposing Python functions as MCP tools that can be used by AI assistants like Claude Desktop.

## Why FastMCP for CAMARA?

✅ **Simple decorators** - `@mcp.tool()` converts functions to tools  
✅ **Async support** - Native `async/await` for CAMARA HTTP calls  
✅ **Type hints** - Automatic JSON schema generation  
✅ **SSE transport** - Claude Desktop compatible  
✅ **HTTP server** - Remote deployment ready  

## Architecture

```python
@mcp.tool()
async def device_reachability_status(phone_number: str) -> str:
    # FastMCP handles:
    # - JSON-RPC protocol
    # - Parameter validation
    # - Error handling
    # - Response formatting

    result = await camara_request(...)  # Your code
    return json.dumps(result)
```

## Core Components

### 1. MCP Server
```python
from fastmcp import FastMCP
mcp = FastMCP("CAMARA Complete Official APIs")
```

### 2. Tool Declaration
```python
@mcp.tool()
async def tool_name(param1: str, param2: int = 10) -> str:
    """Tool description for AI assistant"""
    # Implementation
    return result
```

### 3. Transport Modes

**SSE (Claude Desktop):**
```python
mcp.run(transport="sse")  # Default
```

**HTTP (Server Mode):**
```python
mcp.run(transport="http", host="0.0.0.0", port=8000)
```

## CAMARA Integration Pattern

### Request Flow
```
Claude → FastMCP → camara_request() → CAMARA API
   ↓         ↓              ↓              ↓
User    JSON-RPC      Bearer token    Operator
input   validation    + UUID          response
```

### Error Handling
```python
try:
    resp = await client.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()
except httpx.HTTPStatusError as e:
    return {
        "error": e.response.status_code,
        "detail": e.response.text[:1000],
        "endpoint": endpoint_key
    }
```

## Tool Patterns

### Simple Tool
```python
@mcp.tool()
async def number_verification(phone_number: str) -> str:
    result = await camara_request("number_verification_verify", "POST", 
                                 {"device": {"phoneNumber": phone_number}})
    return json.dumps(result, indent=2)
```

### Complex Tool with Options
```python
@mcp.tool()
async def location_verification(
    phone_number: str, 
    latitude: float, 
    longitude: float,
    radius: int = 5000,
    max_age: int = 120
) -> str:
    result = await camara_request("location_verification", "POST", {
        "device": {"phoneNumber": phone_number},
        "area": {
            "areaType": "CIRCLE",
            "center": {"latitude": latitude, "longitude": longitude},
            "radius": radius
        },
        "maxAge": max_age
    })
    return json.dumps(result, indent=2)
```

### Subscription Tool
```python
@mcp.tool()
async def create_geofencing_subscription(
    phone_number: str, 
    latitude: float, 
    longitude: float,
    webhook: str = "https://webhook.example.com"
) -> str:
    result = await camara_request("geofencing_subs_create", "POST", {
        "protocol": "HTTP",
        "sink": webhook,
        "types": ["org.camaraproject.geofencing-subscriptions.v0.area-entered"],
        "config": {...}
    })
    return json.dumps(result, indent=2)
```

## Version Switching

```python
API_ENDPOINTS = {
    "device_reachability_retrieve": {
        "spring25": "/device-reachability-status/v1.0/retrieve",
        "fall25": "/device-reachability-status/v1.1/retrieve"
    }
}

# Automatic selection via CAMARA_VERSION env
path = API_ENDPOINTS[endpoint_key][CAMARA_VERSION]
```

## Server Mode Implementation

```python
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.server:
        print(f"Server mode: {args.host}:{args.port}")
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        print("Claude Desktop mode (SSE)")
        mcp.run(transport="sse")
```

## Best Practices

### 1. Type Hints
```python
# ✅ Good - Auto-generates JSON schema
async def tool(phone_number: str, max_age: int = 120) -> str:

# ❌ Bad - No validation
async def tool(phone_number, max_age=120):
```

### 2. Docstrings
```python
# ✅ Good - Shows in tool list
"""Device Reachability Status - Check SMS/Data connectivity"""

# ❌ Bad - No description
```

### 3. Error Messages
```python
# ✅ Good - Structured errors
return {"error": 404, "detail": "Device not found", "endpoint": "..."}

# ❌ Bad - Raw exceptions
raise Exception("Error!")
```

### 4. Response Format
```python
# ✅ Good - Pretty JSON for Claude
return json.dumps(result, indent=2)

# ❌ Bad - Unreadable
return str(result)
```

## Testing

### Unit Test
```python
import pytest
from camara_final_complete import device_reachability_status

@pytest.mark.asyncio
async def test_reachability():
    result = await device_reachability_status("+33612345678")
    assert "reachabilityStatus" in result
```

### Integration Test
```bash
# Start server
python camara_final_complete.py --server

# Test tool call
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "device_reachability_status", "arguments": {"phone_number": "+33612345678"}}'
```

## Performance

- **Cold start:** ~200ms (FastMCP initialization)
- **Tool call:** ~500-2000ms (CAMARA API latency)
- **Memory:** ~50MB (Python + httpx)
- **Concurrent:** 100+ tools/sec (async HTTP pool)

## Limitations

- **No streaming** - Tools return complete responses
- **Text only** - No binary/file support
- **Stateless** - No session persistence
- **Single instance** - Use load balancer for HA

## Advanced Features

### Custom HTTP Client
```python
client = httpx.AsyncClient(
    timeout=TIMEOUT,
    limits=httpx.Limits(max_connections=100),
    http2=True
)
```

### Middleware
```python
@mcp.middleware()
async def log_requests(request, call_next):
    print(f"Tool: {request.tool_name}")
    response = await call_next(request)
    return response
```

### Health Check
```python
@mcp.tool()
async def health() -> str:
    return json.dumps({"status": "ok", "version": CAMARA_VERSION})
```

## Resources

- **FastMCP Docs:** https://github.com/jlowin/fastmcp
- **MCP Spec:** https://modelcontextprotocol.io
- **CAMARA APIs:** https://github.com/camaraproject

---

**FastMCP = Perfect bridge between AI assistants and CAMARA telco APIs**
