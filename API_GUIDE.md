# API Usage Guide

Complete guide for using the Dead Man's Switch API.

## Table of Contents

1. [Authentication](#authentication)
2. [Timer Management](#timer-management)
3. [Heartbeat System](#heartbeat-system)
4. [Vault Management](#vault-management)
5. [Beneficiary Management](#beneficiary-management)
6. [Error Handling](#error-handling)
7. [Examples](#examples)

## Authentication

### Register a New User

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "id": "312e641b-d410-40af-9615-43f8c887fdfc",
  "email": "user@example.com",
  "is_active": true
}
```

**Notes:**
- Automatically creates a Timer with 30-day default timeout
- Password must meet your application's requirements
- Email must be unique

### Login

**Endpoint:** `POST /auth/login`

**Request (form-data):**
```
username=user@example.com
password=SecurePassword123!
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Usage:**
Include the token in subsequent requests:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Timer Management

### Get Timer Information

**Endpoint:** `GET /timer`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "user_id": "312e641b-d410-40af-9615-43f8c887fdfc",
  "status": "ACTIVE",
  "timeout_days": 30,
  "last_checkin": "2026-01-18T12:00:00",
  "deadline": "2026-02-17T12:00:00"
}
```

### Update Timer Timeout

**Endpoint:** `PUT /timer`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "timeout_days": 60
}
```

**Response (200 OK):**
```json
{
  "user_id": "312e641b-d410-40af-9615-43f8c887fdfc",
  "status": "ACTIVE",
  "timeout_days": 60,
  "last_checkin": "2026-01-18T12:00:00",
  "deadline": "2026-03-19T12:00:00"
}
```

**Notes:**
- Deadline is automatically recalculated based on new `timeout_days`
- Deadline is calculated from current time, not from `last_checkin`

## Heartbeat System

### Send Heartbeat

**Endpoint:** `POST /heartbeat`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "Heartbeat received successfully",
  "last_checkin": "2026-01-18T12:30:00",
  "deadline": "2026-02-17T12:30:00"
}
```

**Notes:**
- Updates `last_checkin` to current time
- Recalculates `deadline` based on `timeout_days` from current time
- Should be called regularly to prevent timer expiration

## Vault Management

### Create Vault

**Endpoint:** `POST /vaults`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Bank Account Details",
  "encrypted_data": "U2FsdGVkX1+vupppZksvRf5pq5g5XkFy...",
  "client_salt": "random_salt_string"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "312e641b-d410-40af-9615-43f8c887fdfc",
  "name": "Bank Account Details",
  "encrypted_data": "U2FsdGVkX1+vupppZksvRf5pq5g5XkFy...",
  "client_salt": "random_salt_string"
}
```

### List All Vaults

**Endpoint:** `GET /vaults`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "312e641b-d410-40af-9615-43f8c887fdfc",
    "name": "Bank Account Details",
    "encrypted_data": "U2FsdGVkX1+vupppZksvRf5pq5g5XkFy...",
    "client_salt": "random_salt_string"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "312e641b-d410-40af-9615-43f8c887fdfc",
    "name": "Crypto Wallet Keys",
    "encrypted_data": "U2FsdGVkX1+another_encrypted_string...",
    "client_salt": "another_salt"
  }
]
```

### Get Specific Vault

**Endpoint:** `GET /vaults/{vault_id}`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "312e641b-d410-40af-9615-43f8c887fdfc",
  "name": "Bank Account Details",
  "encrypted_data": "U2FsdGVkX1+vupppZksvRf5pq5g5XkFy...",
  "client_salt": "random_salt_string"
}
```

### Update Vault

**Endpoint:** `PUT /vaults/{vault_id}`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Updated Bank Account",
  "encrypted_data": "new_encrypted_data",
  "client_salt": "new_salt"
}
```

**Note:** All fields are optional. Only include fields you want to update.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "312e641b-d410-40af-9615-43f8c887fdfc",
  "name": "Updated Bank Account",
  "encrypted_data": "new_encrypted_data",
  "client_salt": "new_salt"
}
```

### Delete Vault

**Endpoint:** `DELETE /vaults/{vault_id}`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (204 No Content)**

## Beneficiary Management

### Create Beneficiary

**Endpoint:** `POST /beneficiaries`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "email": "beneficiary@example.com",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "312e641b-d410-40af-9615-43f8c887fdfc",
  "email": "beneficiary@example.com",
  "name": "John Doe"
}
```

### List All Beneficiaries

**Endpoint:** `GET /beneficiaries`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user_id": "312e641b-d410-40af-9615-43f8c887fdfc",
    "email": "beneficiary@example.com",
    "name": "John Doe"
  }
]
```

### Get Specific Beneficiary

**Endpoint:** `GET /beneficiaries/{beneficiary_id}`

**Headers:**
```
Authorization: Bearer {token}
```

### Update Beneficiary

**Endpoint:** `PUT /beneficiaries/{beneficiary_id}`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "email": "newemail@example.com",
  "name": "Jane Doe"
}
```

**Note:** All fields are optional.

### Delete Beneficiary

**Endpoint:** `DELETE /beneficiaries/{beneficiary_id}`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (204 No Content)**

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### 404 Not Found
```json
{
  "detail": "Vault not found"
}
```

#### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Examples

### Complete Workflow Example

```bash
# 1. Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# 2. Login
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePassword123!" \
  | jq -r '.access_token')

# 3. Create Beneficiary
curl -X POST "http://localhost:8000/beneficiaries" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "beneficiary@example.com",
    "name": "John Doe"
  }'

# 4. Create Vault
curl -X POST "http://localhost:8000/vaults" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Important Data",
    "encrypted_data": "encrypted_string",
    "client_salt": "salt_string"
  }'

# 5. Send Heartbeat
curl -X POST "http://localhost:8000/heartbeat" \
  -H "Authorization: Bearer $TOKEN"

# 6. Check Timer
curl -X GET "http://localhost:8000/timer" \
  -H "Authorization: Bearer $TOKEN"

# 7. Update Timer
curl -X PUT "http://localhost:8000/timer" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timeout_days": 60
  }'
```

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "user@example.com",
    "password": "SecurePassword123!"
})
user = response.json()

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "user@example.com", "password": "SecurePassword123!"}
)
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Create Beneficiary
response = requests.post(
    f"{BASE_URL}/beneficiaries",
    headers=headers,
    json={"email": "beneficiary@example.com", "name": "John Doe"}
)
beneficiary = response.json()

# Create Vault
response = requests.post(
    f"{BASE_URL}/vaults",
    headers=headers,
    json={
        "name": "Important Data",
        "encrypted_data": "encrypted_string",
        "client_salt": "salt_string"
    }
)
vault = response.json()

# Send Heartbeat
response = requests.post(f"{BASE_URL}/heartbeat", headers=headers)
heartbeat = response.json()

# Get Timer
response = requests.get(f"{BASE_URL}/timer", headers=headers)
timer = response.json()
```

### JavaScript/TypeScript Example

```javascript
const BASE_URL = 'http://localhost:8000';

// Register
const registerResponse = await fetch(`${BASE_URL}/auth/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePassword123!'
  })
});
const user = await registerResponse.json();

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: 'user@example.com',
    password: 'SecurePassword123!'
  })
});
const { access_token } = await loginResponse.json();

const headers = {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
};

// Create Beneficiary
const beneficiaryResponse = await fetch(`${BASE_URL}/beneficiaries`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    email: 'beneficiary@example.com',
    name: 'John Doe'
  })
});
const beneficiary = await beneficiaryResponse.json();

// Create Vault
const vaultResponse = await fetch(`${BASE_URL}/vaults`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    name: 'Important Data',
    encrypted_data: 'encrypted_string',
    client_salt: 'salt_string'
  })
});
const vault = await vaultResponse.json();

// Send Heartbeat
const heartbeatResponse = await fetch(`${BASE_URL}/heartbeat`, {
  method: 'POST',
  headers
});
const heartbeat = await heartbeatResponse.json();
```

## Best Practices

1. **Store tokens securely** - Never expose tokens in client-side code or logs
2. **Send heartbeats regularly** - Set up a cron job or scheduled task
3. **Use HTTPS in production** - Never send sensitive data over HTTP
4. **Encrypt data client-side** - The server never decrypts your data (zero-knowledge)
5. **Keep beneficiaries updated** - Ensure contact information is current
6. **Monitor timer status** - Check timer regularly to prevent expiration
7. **Use meaningful vault names** - Helps organize multiple vaults
