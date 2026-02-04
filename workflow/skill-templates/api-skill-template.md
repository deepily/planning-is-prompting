# API Skill Template

**Purpose**: Template for creating API-related skills that help AI understand project-specific API conventions, authentication patterns, and endpoint documentation.

**Usage**: Copy this template to `.claude/skills/api-conventions/SKILL.md` in your target repository and customize for your project.

---

## Template Content

```yaml
---
name: api-conventions
description: API conventions and patterns for this project. Use when creating endpoints, handling authentication, making API calls, documenting APIs, or debugging HTTP errors.
metadata:
  author: your-team
  version: "1.0"
  last-updated: "YYYY-MM-DD"
---

# API Conventions

## Quick Reference

| Aspect | Convention | Example |
|--------|------------|---------|
| Base URL | `/api/v1/` | `GET /api/v1/users` |
| Auth | Bearer token | `Authorization: Bearer <token>` |
| Format | JSON | `Content-Type: application/json` |
| Errors | RFC 7807 | `{"type": "...", "title": "...", "status": ...}` |

## Endpoint Patterns

### Resource Naming
- Use plural nouns: `/users`, `/orders`, `/products`
- Use kebab-case for multi-word: `/order-items`, `/user-profiles`
- Nest related resources: `/users/{id}/orders`

### HTTP Methods
| Method | Use Case | Idempotent |
|--------|----------|------------|
| GET | Retrieve resource(s) | Yes |
| POST | Create resource | No |
| PUT | Replace resource | Yes |
| PATCH | Partial update | Yes |
| DELETE | Remove resource | Yes |

### Standard Responses
```json
// Success (single resource)
{
  "data": { ... },
  "meta": { "timestamp": "..." }
}

// Success (collection)
{
  "data": [ ... ],
  "meta": { "total": 100, "page": 1, "per_page": 20 }
}

// Error (RFC 7807)
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Email field is required",
  "instance": "/api/v1/users"
}
```

## Authentication

### Token Flow
1. Client sends credentials to `/api/v1/auth/login`
2. Server returns access token (short-lived) + refresh token (long-lived)
3. Client includes access token in `Authorization` header
4. When access token expires, use refresh token to get new one

### Headers
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
Accept: application/json
```

### Common Auth Errors
| Status | Meaning | Action |
|--------|---------|--------|
| 401 | Token missing/invalid | Re-authenticate |
| 403 | Token valid, no permission | Check user roles |
| 419 | Token expired | Use refresh token |

## Validation

### Request Validation
- Use Pydantic models for request bodies
- Validate at route handler level
- Return 400 with field-specific errors

### Validation Response
```json
{
  "type": "validation_error",
  "title": "Validation Error",
  "status": 400,
  "errors": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "age", "message": "Must be positive integer"}
  ]
}
```

## Rate Limiting

### Limits
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Admin: 10000 requests/hour

### Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

## Anti-Patterns
- Verbs in URLs (`/getUser` → `/users/{id}`)
- Inconsistent naming (`/Users` vs `/orders`)
- Returning 200 for errors
- Missing pagination on collections
- Exposing internal IDs without mapping

## See Also
- [Authentication flow details](references/auth-flow.md)
- [Error code reference](references/error-codes.md)
- [OpenAPI specification](references/openapi.yaml)
```

---

## Customization Guide

### Required Customizations

1. **Base URL**: Update to match your API versioning scheme
2. **Authentication**: Document your actual auth mechanism (JWT, OAuth, API keys)
3. **Response Format**: Match your actual response structure
4. **Rate Limits**: Document actual limits if applicable

### Optional Customizations

1. **Versioning Strategy**: URL path, header, or query parameter
2. **CORS Configuration**: If frontend clients need this info
3. **Webhooks**: If your API supports webhooks
4. **GraphQL**: If using GraphQL instead of/alongside REST

### References Directory

For complex APIs, create a `references/` directory:

```
.claude/skills/api-conventions/
├── SKILL.md (this file, <200 lines)
└── references/
    ├── auth-flow.md
    ├── error-codes.md
    ├── openapi.yaml
    └── rate-limiting.md
```

### Trigger Keywords to Consider

Include relevant keywords in your description:
- Protocols: REST, GraphQL, gRPC, WebSocket
- Auth: JWT, OAuth, Bearer, token, authentication
- HTTP: endpoint, request, response, header, status
- Actions: create, update, delete, fetch, call
- Errors: 400, 401, 403, 404, 500, debug, error
