# API Documentation

Complete REST API documentation for BookLeaf AI Assistant backend.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required (demo/MVP). In production, implement:
- API keys
- OAuth 2.0
- JWT tokens

## Common Headers

```
Content-Type: application/json
Accept: application/json
```

## API Endpoints

### Root & Health

#### GET /

Get application information.

**Response**:
```json
{
  "name": "BookLeaf AI Assistant",
  "version": "1.0.0",
  "environment": "development",
  "status": "operational",
  "docs": "/docs"
}
```

#### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

---

## Chat Endpoints

### POST /api/v1/chat/message

Send a message and get AI response.

**Request Body**:
```json
{
  "message": "When will my royalty payment be processed?",
  "name": "Sarah Johnson",
  "email": "sarah.johnson@email.com",
  "phone": "+1-555-0101",
  "platform": "web_chat",
  "conversation_id": "optional-existing-conversation-id"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "response": "Royalty payments are processed quarterly...",
  "confidence": 0.87,
  "confidence_breakdown": {
    "overall_confidence": 0.87,
    "action": "auto_respond",
    "factors": {
      "identity": {
        "score": 1.0,
        "weight": 0.3,
        "contribution": 0.3
      },
      "intent": {
        "score": 0.92,
        "weight": 0.2,
        "contribution": 0.184
      },
      "rag": {
        "score": 0.85,
        "weight": 0.25,
        "contribution": 0.2125
      },
      "llm": {
        "score": 0.75,
        "weight": 0.25,
        "contribution": 0.1875
      }
    },
    "threshold": 0.8,
    "weakest_factor": {
      "name": "llm",
      "score": 0.75
    }
  },
  "should_escalate": false,
  "escalation": null,
  "metadata": {
    "conversation_id": "abc-123-def",
    "author_id": "author-uuid",
    "identity_id": "identity-uuid",
    "identity_confidence": 1.0,
    "identity_method": "exact_match",
    "intent": "general_knowledge",
    "intent_confidence": 0.92,
    "processing_time_ms": 1250,
    "llm_model": "gpt-4-turbo-preview",
    "tokens_used": 850
  }
}
```

**Response** (with Escalation):
```json
{
  "success": true,
  "response": "I understand you have a question...",
  "confidence": 0.65,
  "should_escalate": true,
  "escalation": {
    "id": "escalation-uuid",
    "conversation_id": "conversation-uuid",
    "reason": "Overall confidence (65%) below threshold (80%)",
    "priority": "medium",
    "status": "pending",
    "created_at": "2026-02-27T10:30:00Z"
  },
  "metadata": { ... }
}
```

**Error** (400 Bad Request):
```json
{
  "detail": "At least one of name, email, or phone must be provided"
}
```

### GET /api/v1/chat/conversation/{conversation_id}

Get conversation history.

**Parameters**:
- `conversation_id` (path): UUID of conversation

**Response** (200 OK):
```json
{
  "id": "conversation-uuid",
  "author_id": "author-uuid",
  "platform": "web_chat",
  "status": "active",
  "started_at": "2026-02-27T10:00:00Z",
  "last_message_at": "2026-02-27T10:15:00Z",
  "messages": [
    {
      "id": "message-1",
      "role": "user",
      "content": "Hello, how are you?",
      "intent": null,
      "confidence_score": null,
      "created_at": "2026-02-27T10:00:00Z"
    },
    {
      "id": "message-2",
      "role": "assistant",
      "content": "Hello! I'm here to help...",
      "intent": "general_knowledge",
      "confidence_score": 0.85,
      "created_at": "2026-02-27T10:00:05Z"
    }
  ]
}
```

### POST /api/v1/chat/conversation

Create a new conversation.

**Request Body**:
```json
{
  "name": "Sarah Johnson",
  "email": "sarah.johnson@email.com",
  "phone": "+1-555-0101",
  "platform": "web_chat"
}
```

**Response** (200 OK):
```json
{
  "conversation_id": "new-conversation-uuid",
  "author_id": "author-uuid",
  "identity_id": "identity-uuid"
}
```

---

## Identity Endpoints

### POST /api/v1/identity/resolve

Resolve user identity.

**Request Body**:
```json
{
  "name": "Sarah Johnson",
  "email": "sarah.j@email.com",
  "phone": null,
  "platform": "web_chat",
  "context": "Optional conversation context for disambiguation"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "author": {
    "id": "author-uuid",
    "full_name": "Sarah Johnson",
    "email": "sarah.johnson@email.com",
    "phone": "+1-555-0101",
    "metadata": {
      "genre": "Mystery",
      "books_published": 3
    },
    "created_at": "2022-03-15T00:00:00Z"
  },
  "identity": {
    "id": "identity-uuid",
    "author_id": "author-uuid",
    "platform": "web_chat",
    "platform_identifier": "sarah.j@email.com",
    "confidence_score": 0.95,
    "matching_method": "fuzzy_match",
    "verified": false,
    "created_at": "2026-02-27T10:00:00Z"
  },
  "confidence": 0.95,
  "method": "fuzzy_match",
  "reasoning": "Fuzzy name match (score: 95) with email verification"
}
```

### GET /api/v1/identity/author/{author_id}

Get all identities for an author.

**Parameters**:
- `author_id` (path): UUID of author

**Response** (200 OK):
```json
{
  "identities": [
    {
      "id": "identity-1",
      "author_id": "author-uuid",
      "platform": "email",
      "platform_identifier": "sarah.johnson@email.com",
      "confidence_score": 1.0,
      "matching_method": "exact",
      "verified": true,
      "created_at": "2022-03-15T00:00:00Z"
    },
    {
      "id": "identity-2",
      "author_id": "author-uuid",
      "platform": "whatsapp",
      "platform_identifier": "+1-555-0101",
      "confidence_score": 1.0,
      "matching_method": "exact",
      "verified": true,
      "created_at": "2022-03-20T00:00:00Z"
    }
  ],
  "count": 2
}
```

---

## Escalation Endpoints

### GET /api/v1/escalations

List escalations with optional filtering.

**Query Parameters**:
- `status` (optional): Filter by status (pending, in_progress, resolved, cancelled)
- `priority` (optional): Filter by priority (low, medium, high, urgent)
- `limit` (optional, default=50): Maximum results to return

**Examples**:
```
GET /api/v1/escalations
GET /api/v1/escalations?status=pending
GET /api/v1/escalations?priority=high&limit=10
```

**Response** (200 OK):
```json
{
  "escalations": [
    {
      "id": "escalation-uuid",
      "conversation_id": "conversation-uuid",
      "message_id": "message-uuid",
      "reason": "Overall confidence (65%) below threshold (80%)",
      "priority": "medium",
      "status": "pending",
      "assigned_to": null,
      "resolution_notes": null,
      "created_at": "2026-02-27T10:30:00Z",
      "assigned_at": null,
      "resolved_at": null
    }
  ],
  "count": 1,
  "pending_count": 1,
  "in_progress_count": 0
}
```

### GET /api/v1/escalations/{escalation_id}

Get escalation details.

**Parameters**:
- `escalation_id` (path): UUID of escalation

**Response** (200 OK):
```json
{
  "id": "escalation-uuid",
  "conversation_id": "conversation-uuid",
  "message_id": "message-uuid",
  "reason": "Unclear intent or ambiguous question",
  "priority": "medium",
  "status": "pending",
  "assigned_to": null,
  "resolution_notes": null,
  "created_at": "2026-02-27T10:30:00Z",
  "assigned_at": null,
  "resolved_at": null
}
```

### PATCH /api/v1/escalations/{escalation_id}

Update escalation.

**Request Body** (all fields optional):
```json
{
  "status": "in_progress",
  "assigned_to": "agent@bookleaf.com",
  "priority": "high",
  "resolution_notes": "Working on this issue"
}
```

**Response** (200 OK):
```json
{
  "id": "escalation-uuid",
  "status": "in_progress",
  "assigned_to": "agent@bookleaf.com",
  ...
}
```

### POST /api/v1/escalations/{escalation_id}/resolve

Resolve an escalation.

**Request Body**:
```json
{
  "resolution_notes": "Issue resolved by providing direct assistance to author."
}
```

**Response** (200 OK):
```json
{
  "id": "escalation-uuid",
  "status": "resolved",
  "resolution_notes": "Issue resolved...",
  "resolved_at": "2026-02-27T11:00:00Z",
  ...
}
```

---

## Analytics Endpoints

### GET /api/v1/analytics/stats

Get aggregate statistics.

**Response** (200 OK):
```json
{
  "total_queries": 150,
  "successful_queries": 145,
  "failed_queries": 5,
  "escalated_queries": 25,
  "escalation_rate": 0.167,
  "average_confidence": 0.823,
  "average_response_time_ms": 1250,
  "pending_escalations": 5,
  "resolved_escalations": 20,
  "intent_distribution": {
    "general_knowledge": 80,
    "author_specific": 45,
    "technical_support": 20,
    "out_of_scope": 5
  }
}
```

### GET /api/v1/analytics/confidence-distribution

Get confidence score distribution.

**Response** (200 OK):
```json
{
  "total_count": 150,
  "bins": [
    { "range": "0.0-0.2", "count": 2 },
    { "range": "0.2-0.4", "count": 5 },
    { "range": "0.4-0.6", "count": 18 },
    { "range": "0.6-0.8", "count": 45 },
    { "range": "0.8-1.0", "count": 80 }
  ]
}
```

---

## Error Responses

### 400 Bad Request

Invalid request parameters or validation failure.

```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found

Resource not found.

```json
{
  "detail": "Conversation abc-123 not found"
}
```

### 500 Internal Server Error

Server error.

```json
{
  "error": "Internal server error",
  "message": "Detailed error message (in debug mode)",
  "path": "/api/v1/chat/message"
}
```

---

## Rate Limiting

Currently no rate limiting (demo/MVP). In production:
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## OpenAPI Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Example API Calls

### Using cURL

**Send a message**:
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your royalty rates?",
    "name": "Sarah Johnson",
    "email": "sarah.johnson@email.com"
  }'
```

**Get escalations**:
```bash
curl http://localhost:8000/api/v1/escalations?status=pending
```

### Using Python

```python
import requests

# Send a message
response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "When will my payment be processed?",
        "name": "Sarah Johnson",
        "email": "sarah.johnson@email.com"
    }
)

data = response.json()
print(f"Response: {data['response']}")
print(f"Confidence: {data['confidence']}")
```

### Using JavaScript

```javascript
// Send a message
const response = await fetch('http://localhost:8000/api/v1/chat/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'What are your premium services?',
    name: 'Sarah Johnson',
    email: 'sarah.johnson@email.com',
  }),
});

const data = await response.json();
console.log('Response:', data.response);
console.log('Confidence:', data.confidence);
```

---

## Webhooks (Future Feature)

For multi-channel integration:

### WhatsApp Webhook

```
POST /api/v1/webhooks/whatsapp
```

### Instagram Webhook

```
POST /api/v1/webhooks/instagram
```

### Email Webhook

```
POST /api/v1/webhooks/email
```

---

## Changelog

### v1.0.0 (2026-02-27)
- Initial release
- Chat endpoints
- Identity resolution
- Escalation management
- Analytics endpoints
