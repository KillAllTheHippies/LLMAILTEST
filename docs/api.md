# LLMailTest API Documentation

## Overview
The LLMailTest API provides endpoints for managing email testing jobs and retrieving results for teams.

## Base URL
`https://llmailinject.azurewebsites.net/api`

## Authentication
All endpoints require API key authentication. Include your API key in the request header:

```http
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Submit Job
**POST** `/teams/mine/jobs`

Submit a new email testing job for the authenticated team.

#### Request Body
```json
{
  "scenario": "string",
  "subject": "string",
  "body": "string"
}
```

#### Response
```json
{
  "job_id": "string",
  "team_id": "string",
  "scenario": "string",
  "subject": "string",
  "body": "string",
  "scheduled_time": "string",
  "started_time": "string",
  "completed_time": "string",
  "output": "string",
  "objectives": {
    "email.retrieved": "boolean",
    "defense.undetected": "boolean",
    "exfil.sent": "boolean",
    "exfil.destination": "boolean",
    "exfil.content": "boolean"
  }
}
```

### Get Job Status
**GET** `/teams/mine/jobs/{job_id}`

Retrieve the status of a specific job for the authenticated team.

#### Response
```json
{
  "job_id": "string",
  "team_id": "string",
  "scenario": "string",
  "subject": "string",
  "body": "string",
  "scheduled_time": "string",
  "started_time": "string",
  "completed_time": "string",
  "output": "string",
  "objectives": {
    "email.retrieved": "boolean",
    "defense.undetected": "boolean",
    "exfil.sent": "boolean",
    "exfil.destination": "boolean",
    "exfil.content": "boolean"
  }
}
```

### List Jobs
**GET** `/teams/mine/jobs`

Retrieve a list of all jobs for the authenticated team.

#### Response
```json
[
  {
    "job_id": "string",
    "team_id": "string",
    "scenario": "string",
    "subject": "string",
    "body": "string",
    "scheduled_time": "string",
    "started_time": "string",
    "completed_time": "string",
    "output": "string",
    "objectives": {
      "email.retrieved": "boolean",
      "defense.undetected": "boolean",
      "exfil.sent": "boolean",
      "exfil.destination": "boolean",
      "exfil.content": "boolean"
    }
  }
]
```

## Error Responses

### Error Response Format
```json
{
  "message": "string",
  "advice": "string"
}
```

## Rate Limiting
- Rate limits are applied per team
- Exceeding limit returns 429 status code
- Retry-After header indicates wait time

## Support
For API support, contact: support@llmailinject.com
