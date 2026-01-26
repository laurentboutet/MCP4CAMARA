# CAMARA FastMCP Server

**Complete MCP server for all 10 CAMARA stable APIs with dual-version support (SPRING25/FALL25)**

## Features

✅ **15+ MCP Tools** - All CAMARA stable APIs  
✅ **Dual Version** - SPRING25 + FALL25 automatic switching  
✅ **Claude Desktop** - Native MCP integration  
✅ **Server Mode** - Remote deployment ready  
✅ **Production Ready** - Error handling, logging, Docker/K8s support  

## Quick Start

### 1. Install
```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

### 2. Configure
```bash
# Edit .env
CAMARA_BASE_URL=https://api.example-operator.com
CAMARA_API_KEY=your-bearer-token-here
CAMARA_VERSION=spring25  # or fall25
```

### 3. Run

**Claude Desktop Mode (Recommended):**
See [CLAUDE_SETUP.md](CLAUDE_SETUP.md)

**Server Mode (Remote):**
```bash
python camara_final_complete.py --server --host 0.0.0.0 --port 8000
```

**Local Testing:**
```bash
python camara_final_complete.py
```

## Supported APIs

| API Family | Tools | SPRING25 | FALL25 |
|------------|-------|----------|--------|
| **Device Reachability** | 4 tools | v1.0 | v1.1 |
| **Device Roaming** | 2 tools | v1.0 | v1.1 |
| **Location** | 3 tools | v2.0 | v3.0 |
| **Number Verification** | 1 tool | v2.0 | v2.1 |
| **OTP SMS** | 1 tool | v1.1 | v1.1.1 |
| **QoS/QoD** | 2 tools | v1.0 | v1.1 |
| **SIM Swap** | 2 tools | v2.0 | v2.1 |
| **Simple Edge** | 1 tool | v1.0 | v2.0 |

See [API_REFERENCE.md](API_REFERENCE.md) for complete documentation.

## Architecture

```
Browser/Claude → FastMCP Server → CAMARA Operators
                     ↓
              15 async tools
              26 API endpoints
              Bearer token auth
```

See [COMPARAISON.md](COMPARAISON.md) for MCP vs REST comparison.

## Environment Variables

```bash
CAMARA_BASE_URL      # Operator API endpoint (required)
CAMARA_API_KEY       # Bearer token (required)
CAMARA_VERSION       # spring25 | fall25 (required)
CAMARA_TIMEOUT       # HTTP timeout in seconds (default: 30)
```

## Deployment

### Docker
```bash
docker build -t camara-mcp .
docker run -p 8000:8000 --env-file .env camara-mcp
```

### Kubernetes
```bash
kubectl apply -f k8s/camara-deployment.yaml
```

See deployment guides in `docs/`.

## Usage Examples

### Claude Desktop
```
"Check if +33612345678 is reachable"
"Create geofencing for +33612345678 around Paris"
"Verify number +33612345678"
```

### Python SDK
```python
from mcp import Client
client = Client("http://localhost:8000")
result = client.call_tool("device_reachability_status", 
                         {"phone_number": "+33612345678"})
```

## Troubleshooting

### Claude Desktop Issues
See [CLAUDE_SETUP.md](CLAUDE_SETUP.md#troubleshooting)

### Server Issues
```bash
# Test configuration
python camara_final_complete.py --test

# Enable debug logging
export MCP_LOG_LEVEL=debug
```

## Contributing

Based on official CAMARA GitHub repositories:
- DeviceReachabilityStatus (r1.2/r3.2)
- DeviceLocation (r2.2/r3.2)
- NumberVerification (r2.4/r3.2)
- SimSwap (r2.2/r3.3)
- And 6 more...

## License

MIT License - See LICENSE file

## Support

- **CAMARA Project:** https://github.com/camaraproject
- **FastMCP:** https://github.com/jlowin/fastmcp
- **Issues:** GitHub Issues

---

**Production-ready CAMARA MCP server for enterprise telco AI applications**
