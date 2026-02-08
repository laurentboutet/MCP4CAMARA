# Claude Desktop Setup Guide

## Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

### 2. Configure Environment
```bash
# Edit .env with your credentials
CAMARA_BASE_URL=https://api.example-operator.com
CAMARA_API_KEY=your-bearer-token-here
CAMARA_VERSION=spring25
```

### 3. Configure Claude Desktop

**Location:** `%APPDATA%\Claude\claude_desktop_config.json` (Windows)  
**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)

```json
{
  "mcpServers": {
    "camara": {
      "command": "py",
      "args": [
        "-3.13",
        "C:/path/to/camara_final_complete.py"
      ]
    }
  }
}
```

**⚠️ IMPORTANT:** Use **forward slashes** (`/`) in paths, even on Windows!

### 4. Restart Claude Desktop

1. **Completely close** Claude Desktop
2. **Open Task Manager** → End all Claude processes
3. **Restart** Claude Desktop
4. **Check sidebar** → "CAMARA Complete Official APIs" should appear

## Platform-Specific Commands

### Windows
```json
{
  "mcpServers": {
    "camara": {
      "command": "py",
      "args": ["-3.13", "C:/Users/YourName/camara/camara_final_complete.py"]
    }
  }
}
```

### Mac/Linux
```json
{
  "mcpServers": {
    "camara": {
      "command": "python3",
      "args": ["/Users/yourname/camara/camara_final_complete.py"]
    }
  }
}
```

## Troubleshooting

### Issue: "spawn python3 ENOENT"
**Solution:** Change `"python3"` → `"py"` on Windows

### Issue: "UnicodeEncodeError emoji"
**Solution:** Already fixed in code (line 18-20 encoding reconfigure)

### Issue: "Server transport closed"
**Solutions:**
1. Check `.env` exists with valid credentials
2. Kill any manual Python processes
3. Restart Claude Desktop completely
4. Check logs: `%APPDATA%\Claude\logs\`

### Issue: "Tools not appearing"
**Solutions:**
1. Verify config path is correct (forward slashes)
2. Test manually: `py -3.13 camara_final_complete.py`
3. Check Python version: `py -3.13 --version`

## Testing

```bash
# Manual test (should NOT crash)
py -3.13 camara_final_complete.py
# Ctrl+C to stop

# Check Claude logs
tail -f "%APPDATA%\Claude\logs\mcp.log"
```

## Using CAMARA Tools in Claude

Once configured, use natural language:
```
"Check reachability status for +33612345678"
"Create geofencing subscription around Paris for +33612345678"
"Verify if +33612345678 is in location 48.8566, 2.3522"
"Check SIM swap status"
```

## Advanced: Virtual Environment

```bash
# Windows
py -3.13 -m venv venv
venv\Scripts\activate
pip install -r requirements_fastmcp.txt

# Claude config with venv
{
  "command": "C:/path/to/venv/Scripts/python.exe",
  "args": ["C:/path/to/camara_final_complete.py"]
}
```

## Support

- **Logs:** `%APPDATA%\Claude\logs\mcp-camara.log`
- **Test manually:** `py -3.13 camara_final_complete.py`
- **CAMARA docs:** https://github.com/camaraproject
