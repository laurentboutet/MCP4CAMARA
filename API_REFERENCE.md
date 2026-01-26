# CAMARA MCP Tools Reference

Complete reference for all 15 MCP tools from 10 CAMARA stable APIs.

## Device Reachability Status

### device_reachability_status
Check if device is reachable via SMS/Data.

**Parameters:**
- `phone_number` (str, required) - E.164 format (e.g., +33612345678)
- `naid` (str, optional) - Network Access Identifier
- `ipv4` (str, optional) - IPv4 address
- `ipv6` (str, optional) - IPv6 address

**Returns:**
```json
{
  "reachabilityStatus": "REACHABLE",
  "smsCapable": true,
  "dataCapable": true,
  "lastSeen": "2026-01-26T14:30:00Z"
}
```

**Example:**
```
device_reachability_status("+33612345678")
```

### create_reachability_subscription
Subscribe to reachability status changes.

**Parameters:**
- `phone_number` (str, required)
- `webhook_url` (str, required) - HTTPS callback URL
- `max_events` (int, optional, default=10)
- `initial_event` (bool, optional, default=True)

**Returns:** Subscription ID

### list_reachability_subscriptions
List all active subscriptions.

**Returns:** Array of subscription objects

### delete_reachability_subscription
Delete subscription by ID.

**Parameters:**
- `subscription_id` (str, required)

---

## Device Roaming Status

### device_roaming_status
Check if device is roaming.

**Parameters:**
- `phone_number` (str, required)
- `naid` (str, optional)
- `ipv4` (str, optional)
- `ipv6` (str, optional)

**Returns:**
```json
{
  "roaming": true,
  "countryCode": "ES",
  "countryName": "Spain"
}
```

### create_roaming_subscription
Subscribe to roaming status changes.

**Parameters:**
- `phone_number` (str, required)
- `webhook_url` (str, required)
- `max_events` (int, optional, default=10)

---

## Location Services

### location_verification
Verify if device is in specified area.

**Parameters:**
- `phone_number` (str, required)
- `latitude` (float, required) - Center latitude
- `longitude` (float, required) - Center longitude
- `radius` (int, optional, default=5000) - Radius in meters
- `max_age` (int, optional, default=120) - Max location age in seconds

**Returns:**
```json
{
  "verificationResult": "TRUE",
  "matchRate": 95,
  "lastLocationTime": "2026-01-26T14:30:00Z"
}
```

**Example:**
```
location_verification("+33612345678", 48.8566, 2.3522, 5000)
```

### location_retrieval
Get device coordinates.

**Parameters:**
- `phone_number` (str, required)
- `max_age` (int, optional, default=0)

**Returns:**
```json
{
  "latitude": 48.8566,
  "longitude": 2.3522,
  "accuracy": 50,
  "timestamp": "2026-01-26T14:30:00Z"
}
```

### create_geofencing_subscription
Subscribe to area entry/exit events.

**Parameters:**
- `phone_number` (str, required)
- `latitude` (float, required)
- `longitude` (float, required)
- `radius` (int, optional, default=2000)
- `webhook` (str, optional)
- `max_events` (int, optional, default=10)

**Returns:** Subscription ID

---

## Number Verification

### number_verification
Verify if phone number matches device.

**Parameters:**
- `phone_number` (str, required)

**Returns:**
```json
{
  "devicePhoneNumberVerified": true
}
```

---

## OTP SMS

### send_otp
Send one-time password via SMS.

**Parameters:**
- `phone_number` (str, required)
- `message` (str, optional, default="{{code}} is your code")

**Returns:**
```json
{
  "authenticationId": "auth-123-456",
  "expiresIn": 300
}
```

---

## QoS & Quality on Demand

### list_qos_profiles
List available QoS profiles.

**Parameters:**
- `profile_name` (str, optional) - Filter by name

**Returns:** Array of QoS profile objects

**Example profiles:**
- `QCI_1_voice` - Voice calls
- `QCI_2_video` - Video streaming
- `QCI_9_web` - Web browsing

### create_qos_session
Create Quality on Demand session.

**Parameters:**
- `phone_number` (str, required)
- `app_server_ip` (str, required) - Application server IPv4
- `qos_profile` (str, required) - Profile name
- `duration` (int, optional, default=3600) - Duration in seconds

**Returns:**
```json
{
  "sessionId": "session-789",
  "duration": 3600,
  "startedAt": "2026-01-26T14:30:00Z",
  "expiresAt": "2026-01-26T15:30:00Z"
}
```

---

## SIM Swap

### sim_swap_check
Check if SIM was swapped recently.

**Parameters:**
- `phone_number` (str, optional)
- `max_age` (int, optional) - Check within X hours

**Returns:**
```json
{
  "swapped": false
}
```

### create_sim_swap_subscription
Subscribe to SIM swap events.

**Parameters:**
- `phone_number` (str, required)
- `webhook` (str, required)

**Returns:** Subscription ID

---

## Version Support

All tools support dual versions via `CAMARA_VERSION` environment variable:

| Version | Release | Status |
|---------|---------|--------|
| **spring25** | r2.2-r2.4 | ✅ Stable |
| **fall25** | r3.2-r3.3 | ✅ Stable |

Set in `.env`:
```bash
CAMARA_VERSION=spring25  # or fall25
```

---

## Error Responses

All tools return structured errors:

```json
{
  "error": 404,
  "detail": "Device not found",
  "endpoint": "device_reachability_retrieve",
  "version": "spring25"
}
```

Common error codes:
- `400` - Invalid parameters
- `401` - Invalid API key
- `404` - Resource not found
- `429` - Rate limit exceeded
- `500` - Operator error

---

## Rate Limits

Operator-specific, typically:
- **100 requests/minute** per API key
- **10,000 requests/day** per subscription

Check operator dashboard for limits.

---

**Complete CAMARA API coverage via simple MCP tools**
