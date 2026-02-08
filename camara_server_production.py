#!/usr/bin/env python3
"""
CAMARA MCP Server - PRODUCTION REMOTE SERVER
==============================================
Implements MCP Streamable HTTP protocol (2025-03-26 standard)
Compatible with LibreChat and all modern MCP clients

FOR: Docker, K8s, LibreChat (remote clients)
NOT FOR: Claude Desktop local (use camara_final_complete-old-v1.0.py)
"""

import os
import sys
import json
import uuid
import logging
from typing import Optional, Dict, List

# Encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import httpx
from dotenv import load_dotenv

# FastAPI for HTTP server (Streamable HTTP protocol)
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# CAMARA API CONFIGURATION
# =============================================================================

CAMARA_BASE_URL = os.getenv("CAMARA_BASE_URL", "")
CAMARA_API_KEY = os.getenv("CAMARA_API_KEY", "")
CAMARA_VERSION = os.getenv("CAMARA_VERSION", "spring25").lower()  # spring25 | fall25
TIMEOUT = int(os.getenv("CAMARA_TIMEOUT", "30"))

client = httpx.AsyncClient(timeout=TIMEOUT)

# =============================================================================
# ALL 23 API ENDPOINTS - spring25 and fall25
# =============================================================================

API_ENDPOINTS = {
    # 1. DeviceReachabilityStatus + subscriptions
    "device_reachability_retrieve": {
        "spring25": "/device-reachability-status/v1/retrieve",
        "fall25": "/device-reachability-status/v1/retrieve"
    },
    "device_reachability_subs_create": {
        "spring25": "/device-reachability-status-subscriptions/v0.7/subscriptions",
        "fall25": "/device-reachability-status-subscriptions/v1/subscriptions"
    },
    # 2. DeviceRoamingStatus + subscriptions
    "device_roaming_retrieve": {
        "spring25": "/device-roaming-status/v1/retrieve",
        "fall25": "/device-roaming-status/v1/retrieve"
    },
    "device_roaming_subs_create": {
        "spring25": "/device-roaming-status-subscriptions/v0.7/subscriptions",
        "fall25": "/device-roaming-status-subscriptions/v1/subscriptions"
    },
    # 3. DeviceLocation - 3 APIs
    "location_verification": {
        "spring25": "/location-verification/v0/verify",
        "fall25": "/location-verification/v3/verify"
    },
    "location_retrieval": {
        "spring25": "/location-retrieval/v0/retrieve",
        "fall25": "/location-retrieval/v0.5/retrieve"
    },
    "geofencing_subs_create": {
        "spring25": "/geofencing-subscriptions/v0.3/subscriptions",
        "fall25": "/geofencing-subscriptions/v0.5/subscriptions"
    },
    # 4. NumberVerification
    "number_verification_verify": {
        "spring25": "/number-verification/v2/verify",
        "fall25": "/number-verification/v2/verify"
    },
    "number_verification_phone": {
        "spring25": "/number-verification/v2/device-phone-number",
        "fall25": "/number-verification/v2/device-phone-number"
    },
    # 5. OTPValidation
    "otp_send": {
        "spring25": "/one-time-password-sms/v1/send-code",
        "fall25": "/one-time-password-sms/v1/send-code"
    },
    "otp_validate": {
        "spring25": "/one-time-password-sms/v1/validate-code",
        "fall25": "/one-time-password-sms/v1/validate-code"
    },
    # 6. QualityOnDemand
    "qos_profiles_list": {
        "spring25": "/qos-profiles/v0.11/qos-profiles",
        "fall25": "/qos-profiles/v1/qos-profiles"
    },
    "qos_profiles_detail": {
        "spring25": "/qos-profiles/v0.11/qos-profiles/{name}",
        "fall25": "/qos-profiles/v1/qos-profiles/{name}"
    },
    "qod_sessions_create": {
        "spring25": "/quality-on-demand/v0.11/sessions",
        "fall25": "/quality-on-demand/v1/sessions"
    },
    "qod_sessions_get": {
        "spring25": "/quality-on-demand/v0.11/sessions/{id}",
        "fall25": "/quality-on-demand/v1/sessions/{id}"
    },
    "qod_sessions_delete": {
        "spring25": "/quality-on-demand/v0.11/sessions/{id}",
        "fall25": "/quality-on-demand/v1/sessions/{id}"
    },
    "qod_sessions_extend": {
        "spring25": "/quality-on-demand/v0.11/sessions/{id}/extend",
        "fall25": "/quality-on-demand/v1/sessions/{id}/extend"
    },
    # 7. SimSwap + subscriptions
    "sim_swap_check": {
        "spring25": "/sim-swap/v2/check",
        "fall25": "/sim-swap/v2/check"
    },
    "sim_swap_date": {
        "spring25": "/sim-swap/v2/retrieve-date",
        "fall25": "/sim-swap/v2/retrieve-date"
    },
    "sim_swap_subs_create": {
        "spring25": "/sim-swap-subscriptions/v0.2/subscriptions",
        "fall25": "/sim-swap-subscriptions/v1/subscriptions"
    },
    # 8. SimpleEdgeDiscovery
    "simple_edge_discovery": {
        "spring25": "/simple-edge-discovery/v1/edge-resources",
        "fall25": "/simple-edge-discovery/v2/edge-resources"
    },
    # 9. DeviceSwap
    "device_swap_check": {
        "spring25": "/device-swap/v0.2/check",
        "fall25": "/device-swap/v1/check"
    },
    "device_swap_date": {
        "spring25": "/device-swap/v0.2/retrieve-date",
        "fall25": "/device-swap/v1/retrieve-date"
    },
}

logger.info(f"🚀 CAMARA Server - {CAMARA_VERSION.upper()} ({len(API_ENDPOINTS)} endpoints)")

# =============================================================================
# CAMARA API REQUEST HANDLER
# =============================================================================

async def camara_request(endpoint_key: str, method: str = "POST", 
                        data: Optional[Dict] = None,
                        params: Optional[Dict] = None, 
                        path_params: Optional[Dict] = None) -> Dict:
    """CAMARA API request handler with detailed logging"""
    try:
        path_template = API_ENDPOINTS[endpoint_key][CAMARA_VERSION]
        path = path_template.format(**path_params) if path_params else path_template
        
        headers = {
            "Authorization": f"Bearer {CAMARA_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json,application/problem+json",
            "x-correlator": str(uuid.uuid4())
        }
        
        url = f"{CAMARA_BASE_URL.rstrip('/')}{path}"
        
        # LOG REQUEST
        logger.info(f"   🔹 CAMARA API Call:")
        logger.info(f"      Method: {method}")
        logger.info(f"      URL: {url}")
        logger.info(f"      Endpoint: {endpoint_key}")
        if data:
            logger.info(f"      Request Body: {json.dumps(data)[:200]}")
        
        # MAKE REQUEST
        if method.upper() == "GET":
            resp = await client.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            resp = await client.post(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            resp = await client.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        # LOG RESPONSE
        logger.info(f"   🔹 CAMARA Response:")
        logger.info(f"      Status: {resp.status_code}")
        logger.info(f"      Content-Length: {len(resp.content)}")
        logger.info(f"      Content-Type: {resp.headers.get('content-type')}")
        logger.info(f"      Body preview: {resp.text[:500]}")
        
        resp.raise_for_status()
        
 # PARSE RESPONSE BASED ON STATUS CODE
        if resp.status_code == 204:
            # 204 No Content - operation succeeded, no data returned
            logger.info(f"   ✅ 204 No Content - Operation successful")
            return {
                "status": "success",
                "message": "Operation completed successfully (no content returned)",
                "endpoint": endpoint_key,
                "http_status": 204
            }
        
        elif resp.status_code == 200:
            if resp.content:
                try:
                    parsed = resp.json()
                    logger.info(f"   ✅ 200 OK - JSON data returned")
                    return parsed
                except json.JSONDecodeError as e:
                    logger.error(f"   ❌ 200 OK but invalid JSON: {e}")
                    return {
                        "error": "invalid_json",
                        "detail": resp.text[:1000],
                        "endpoint": endpoint_key
                    }
            else:
                # 200 with empty body - unusual but treat as success
                logger.warning(f"   ⚠️  200 OK but empty body")
                return {
                    "status": "success",
                    "message": "Operation returned 200 OK with no content",
                    "endpoint": endpoint_key,
                    "http_status": 200
                }
        
        else:
            # Other 2xx codes
            return {
                "status": "success",
                "message": f"Operation returned {resp.status_code}",
                "endpoint": endpoint_key,
                "http_status": resp.status_code
            }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP {e.response.status_code}: {e.response.text[:500]}")
        
        # Try to parse error response
        try:
            error_detail = e.response.json()
        except:
            error_detail = e.response.text[:1000]
        
        return {
            "error": e.response.status_code,
            "detail": error_detail,
            "endpoint": endpoint_key,
            "url": str(e.request.url)
        }
    
    except Exception as e:
        logger.error(f"❌ Exception: {type(e).__name__}: {e}")
        return {
            "error": "network",
            "detail": str(e),
            "endpoint": endpoint_key
        }


# =============================================================================
# MCP TOOL DEFINITIONS - 18 Tools
# =============================================================================

MCP_TOOLS = [
    {
        "name": "device_reachability_status",
        "description": "Check if device is reachable via SMS/Data connectivity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string", "description": "Phone number in E.164 format (+33612345678)"}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "create_reachability_subscription",
        "description": "Create subscription for device reachability status changes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "webhook_url": {"type": "string", "description": "Webhook URL for notifications"},
                "max_events": {"type": "integer", "default": 10}
            },
            "required": ["phone_number", "webhook_url"]
        }
    },
    {
        "name": "device_roaming_status",
        "description": "Check if device is currently roaming",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "create_roaming_subscription",
        "description": "Create subscription for roaming status changes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "webhook_url": {"type": "string"}
            },
            "required": ["phone_number", "webhook_url"]
        }
    },
    {
        "name": "location_verification",
        "description": "Verify if device is within a geographic area (geofencing)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "radius": {"type": "integer", "default": 5000, "description": "Radius in meters"}
            },
            "required": ["phone_number", "latitude", "longitude"]
        }
    },
    {
        "name": "location_retrieval",
        "description": "Get device current coordinates",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "create_geofencing_subscription",
        "description": "Create subscription for geofencing area entry/exit",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "radius": {"type": "integer", "default": 2000},
                "webhook": {"type": "string"}
            },
            "required": ["phone_number", "latitude", "longitude", "webhook"]
        }
    },
    {
        "name": "number_verification",
        "description": "Verify if phone number matches the device",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "send_otp",
        "description": "Send One-Time Password via SMS",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "message": {"type": "string", "default": "{{code}} is your code"}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "validate_otp",
        "description": "Validate OTP code",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "auth_code": {"type": "string"}
            },
            "required": ["phone_number", "auth_code"]
        }
    },
    {
        "name": "list_qos_profiles",
        "description": "List available Quality of Service profiles",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_name": {"type": "string", "description": "Optional filter"}
            }
        }
    },
    {
        "name": "get_qos_profile",
        "description": "Get QoS profile details",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_name": {"type": "string"}
            },
            "required": ["profile_name"]
        }
    },
    {
        "name": "create_qos_session",
        "description": "Create Quality on Demand session",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "app_server_ip": {"type": "string"},
                "qos_profile": {"type": "string"},
                "duration": {"type": "integer", "default": 3600}
            },
            "required": ["phone_number", "app_server_ip", "qos_profile"]
        }
    },
    {
        "name": "get_qos_session",
        "description": "Get QoS session details",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"}
            },
            "required": ["session_id"]
        }
    },
    {
        "name": "delete_qos_session",
        "description": "Delete QoS session",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"}
            },
            "required": ["session_id"]
        }
    },
    {
        "name": "sim_swap_check",
        "description": "Check if SIM was swapped recently (fraud detection)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "max_age": {"type": "integer", "description": "Hours"}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "sim_swap_retrieve_date",
        "description": "Get last SIM swap date",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "device_swap_check",
        "description": "Check if device was swapped recently",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "max_age": {"type": "integer"}
            },
            "required": ["phone_number"]
        }
    }
]

# =============================================================================
# TOOL EXECUTION HANDLER
# =============================================================================

async def execute_tool(name: str, arguments: dict) -> dict:
    """Execute CAMARA tool - all 18 tools"""
    logger.info(f"📞 Tool: {name}")
    
    try:
        # 1. Device Reachability
        if name == "device_reachability_status":
            result = await camara_request("device_reachability_retrieve", "POST", {
                "device": {"phoneNumber": arguments["phone_number"]}
            })
        
        elif name == "create_reachability_subscription":
            result = await camara_request("device_reachability_subs_create", "POST", {
                "sink": arguments["webhook_url"],
                "protocol": "HTTP",
                "types": ["org.camaraproject.device-reachability-status-subscriptions.v0.reachability-data"],
                "config": {
                    "subscriptionDetail": {"device": {"phoneNumber": arguments["phone_number"]}},
                    "subscriptionMaxEvents": arguments.get("max_events", 10),
                    "initialEvent": True
                }
            })
        
        # 2. Device Roaming
        elif name == "device_roaming_status":
            result = await camara_request("device_roaming_retrieve", "POST", {
                "device": {"phoneNumber": arguments["phone_number"]}
            })
        
        elif name == "create_roaming_subscription":
            result = await camara_request("device_roaming_subs_create", "POST", {
                "sink": arguments["webhook_url"],
                "protocol": "HTTP",
                "types": ["org.camaraproject.device-roaming-status-subscriptions.v0.roaming-status"],
                "config": {
                    "subscriptionDetail": {"device": {"phoneNumber": arguments["phone_number"]}},
                    "subscriptionMaxEvents": 10
                }
            })
        
        # 3. Location
        elif name == "location_verification":
            result = await camara_request("location_verification", "POST", {
                "device": {"phoneNumber": arguments["phone_number"]},
                "area": {
                    "areaType": "CIRCLE",
                    "center": {"latitude": arguments["latitude"], "longitude": arguments["longitude"]},
                    "radius": arguments.get("radius", 5000)
                },
                "maxAge": 120
            })
        
        elif name == "location_retrieval":
            result = await camara_request("location_retrieval", "POST", {
                "device": {"phoneNumber": arguments["phone_number"]},
                "maxAge": 0
            })
        
        elif name == "create_geofencing_subscription":
            result = await camara_request("geofencing_subs_create", "POST", {
                "protocol": "HTTP",
                "sink": arguments["webhook"],
                "types": ["org.camaraproject.geofencing-subscriptions.v0.area-entered"],
                "config": {
                    "subscriptionDetail": {
                        "device": {"phoneNumber": arguments["phone_number"]},
                        "area": {
                            "areaType": "CIRCLE",
                            "center": {"latitude": arguments["latitude"], "longitude": arguments["longitude"]},
                            "radius": arguments.get("radius", 2000)
                        }
                    },
                    "initialEvent": True,
                    "subscriptionMaxEvents": 10
                }
            })
        
        # 4. Number Verification
        elif name == "number_verification":
            result = await camara_request("number_verification_verify", "POST", {
                "device": {"phoneNumber": arguments["phone_number"]}
            })
        
        # 5. OTP
        elif name == "send_otp":
            result = await camara_request("otp_send", "POST", {
                "phoneNumber": arguments["phone_number"],
                "message": arguments.get("message", "{{code}} is your code")
            })
        
        elif name == "validate_otp":
            result = await camara_request("otp_validate", "POST", {
                "phoneNumber": arguments["phone_number"],
                "authCode": arguments["auth_code"]
            })
        
        # 6. QoS
        elif name == "list_qos_profiles":
            params = {"name": arguments["profile_name"]} if arguments.get("profile_name") else None
            result = await camara_request("qos_profiles_list", "GET", params=params)
        
        elif name == "get_qos_profile":
            result = await camara_request("qos_profiles_detail", "GET", 
                                        path_params={"name": arguments["profile_name"]})
        
        elif name == "create_qos_session":
            result = await camara_request("qod_sessions_create", "POST", {
                "device": {"phoneNumber": arguments["phone_number"]},
                "applicationServer": {"ipv4Address": arguments["app_server_ip"]},
                "qosProfile": arguments["qos_profile"],
                "duration": arguments.get("duration", 3600)
            })
        
        elif name == "get_qos_session":
            result = await camara_request("qod_sessions_get", "GET", 
                                        path_params={"id": arguments["session_id"]})
        
        elif name == "delete_qos_session":
            result = await camara_request("qod_sessions_delete", "DELETE", 
                                        path_params={"id": arguments["session_id"]})
        
        # 7. SIM Swap
        elif name == "sim_swap_check":
            data = {"phoneNumber": arguments["phone_number"]}
            if arguments.get("max_age"): data["maxAge"] = arguments["max_age"]
            result = await camara_request("sim_swap_check", "POST", data)
        
        elif name == "sim_swap_retrieve_date":
            result = await camara_request("sim_swap_date", "POST", {
                "phoneNumber": arguments["phone_number"]
            })
        
        # 8. Device Swap
        elif name == "device_swap_check":
            data = {"phoneNumber": arguments["phone_number"]}
            if arguments.get("max_age"): data["maxAge"] = arguments["max_age"]
            result = await camara_request("device_swap_check", "POST", data)
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return result
    
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return {"error": str(e)}

# =============================================================================
# FASTAPI - Streamable HTTP (MCP 2025-03-26)
# =============================================================================

app = FastAPI(
    title="CAMARA MCP Server",
    description="Streamable HTTP MCP Server for CAMARA APIs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "CAMARA MCP Server",
        "version": "1.0.0",
        "protocol": "MCP Streamable HTTP (2025-03-26)",
        "endpoint": "/mcp",
        "tools": len(MCP_TOOLS),
        "camara_version": CAMARA_VERSION.upper()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "api_configured": bool(CAMARA_API_KEY),
        "base_url": CAMARA_BASE_URL
    }

# MCP Streamable HTTP endpoint
@app.post("/mcp")
async def handle_mcp(request: Request):
    """MCP Streamable HTTP endpoint (2025-03-26 standard)"""
    logger.info("📨 MCP Request")
    
    try:
        body = await request.json()
    except:
        body = {}
    
    logger.info(f"   Method: {body.get('method')}")
    
    async def response_generator():
        """Generate streaming JSON-RPC response"""
        
        # Initialize
        if body.get("method") == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "CAMARA-MCP", "version": "1.0.0"}
                }
            }
            yield f"data: {json.dumps(response)}\n\n"
        
        # List tools
        elif body.get("method") == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {"tools": MCP_TOOLS}
            }
            yield f"data: {json.dumps(response)}\n\n"
        
        # Call tool
        elif body.get("method") == "tools/call":
            params = body.get("params", {})
            result = await execute_tool(params.get("name"), params.get("arguments", {}))
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            }
            yield f"data: {json.dumps(response)}\n\n"
        
        else:
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id", 0),
                "error": {"code": -32601, "message": f"Method not found: {body.get('method')}"}
            }
            yield f"data: {json.dumps(response)}\n\n"
    
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    print("=" * 70)
    print("   CAMARA MCP SERVER - Streamable HTTP (Production)")
    print("=" * 70)
    print(f"   Protocol     : MCP Streamable HTTP (2025-03-26)")
    print(f"   CAMARA Version: {CAMARA_VERSION.upper()}")
    print(f"   API Endpoints : {len(API_ENDPOINTS)}")
    print(f"   MCP Tools     : {len(MCP_TOOLS)}")
    print(f"   Listen        : {args.host}:{args.port}")
    print(f"   MCP Endpoint  : /mcp")
    print("=" * 70)
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
