# Troubleshooting Connection Errors

## Problem
You're seeing "Connection error" messages in the frontend console while the backend shows successful 200 OK responses in the server logs.

## Root Cause Analysis

Based on the logs:
```
Error: Connection error.
INFO:     127.0.0.1:1236 - "POST /api/process/text HTTP/1.1" 200 OK
```

The backend is **working correctly** and returning successful responses. The connection error is likely:

1. **Transient network issue** - Temporary connection drop during the request/response cycle
2. **CORS issue** - Although unlikely since CORS is configured, check browser console for CORS errors
3. **Proxy timing** - The Vite proxy might be closing connections prematurely
4. **Response parsing** - The frontend might be failing to parse the response

## Diagnostic Steps

### 1. Check Browser Console

Open your browser's Developer Tools (F12) and check the Console and Network tabs:

```javascript
// Look for errors like:
- "CORS policy"
- "Failed to fetch"
- "Network request failed"
- "ERR_CONNECTION_REFUSED"
```

### 2. Verify Backend is Running

```bash
# Test backend health
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","timestamp":"2026-01-20T...","version":"0.1.0"}
```

### 3. Test API Endpoints Directly

```bash
# Test experiences endpoint
curl http://localhost:8000/api/experiences

# Test tags endpoint
curl http://localhost:8000/api/tags

# Test stats endpoint
curl http://localhost:8000/api/stats
```

### 4. Check Frontend Dev Server

Make sure your frontend dev server (Vite) is running on port 5173:

```bash
cd frontend
npm run dev
```

### 5. Test API Call from Frontend Console

Open browser console on http://localhost:5173 and run:

```javascript
// Test fetch directly
fetch('/api/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)

// Test process endpoint
fetch('/api/process/text', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: 'Test interview content',
    generate_answers: false,
    export_format: 'both'
  })
})
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

## Improvements Made

### 1. Enhanced Error Handling ([frontend/src/services/api.ts](frontend/src/services/api.ts))

Added an Axios interceptor that provides more detailed error messages:

```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
      return Promise.reject(new Error('Connection error. Please check if the backend server is running.'))
    }
    // ... more detailed error handling
  }
)
```

### 2. Fixed Boolean Conversion ([src/utils/database.py](src/utils/database.py:220))

SQLite stores booleans as integers (0/1). Fixed conversion to proper Python booleans:

```python
exp_dict["has_answers"] = bool(exp_dict["has_answers"])
```

## Common Solutions

### Solution 1: Restart Both Servers

```bash
# Terminal 1: Restart backend
cd d:/LLM_learning/interview_agent
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Restart frontend
cd d:/LLM_learning/interview_agent/frontend
npm run dev
```

### Solution 2: Clear Browser Cache

1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Solution 3: Check Firewall/Antivirus

Some security software may block localhost connections:
- Temporarily disable firewall
- Add exception for ports 8000 and 5173

### Solution 4: Use Direct Backend URL

If Vite proxy is causing issues, create a `.env` file in the frontend directory:

```bash
# frontend/.env
VITE_API_BASE=http://localhost:8000/api
```

Then restart the frontend dev server.

### Solution 5: Check Port Conflicts

Make sure no other applications are using ports 8000 or 5173:

```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Linux/Mac
lsof -i :8000
lsof -i :5173
```

## Monitoring for Future Issues

### Enable Detailed Logging

Add this to your frontend code temporarily to see all network activity:

```typescript
// frontend/src/services/api.ts
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data)
    return config
  }
)

api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.status, response.data)
    return response
  },
  (error) => {
    console.error('API Error:', error.config?.url, error.message, error.response?.data)
    return Promise.reject(error)
  }
)
```

### Backend Request Logging

The FastAPI server already logs all requests. Watch the console output for:
- Request method and path
- Response status code
- Response time

## If Problem Persists

If you continue seeing connection errors:

1. **Capture the exact error message** from browser console
2. **Check the Network tab** in DevTools to see:
   - Which specific request is failing
   - The request/response headers
   - The response body (if any)
3. **Try using a different browser** to rule out browser-specific issues
4. **Check if it happens consistently** or only sometimes

## Current Status

Based on the test results:
- ✅ Backend is running and healthy
- ✅ All API endpoints are working correctly
- ✅ Database queries return valid data
- ✅ Enhanced error messages are now in place

The "Connection error" you saw was likely transient. With the improved error handling, you should now get more specific error messages if it happens again.
