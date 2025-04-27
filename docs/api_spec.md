# Minecraft MCP Server API Specification

## Overview

This document specifies the REST API endpoints for the Minecraft MCP server built with FastMCP, GDPC, and Supabase. The API provides programmatic access to Minecraft worlds for world generation, structure building, and template management.

## Base URL

```
https://api.minecraft-mcp.example.com/v1
```

## Authentication

All API requests require authentication using JWT tokens, except for the authentication endpoints.

**Authentication Header:**
```
Authorization: Bearer <token>
```

## API Endpoints

### Authentication

#### Register User

```
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "username": "minecraft_builder"
}
```

**Response:**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "minecraft_builder",
    "created_at": "2025-04-27T15:49:13Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Status Codes:**
- 201: User created successfully
- 400: Invalid request (e.g., missing fields, invalid email)
- 409: Email already in use

#### Login User

```
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "minecraft_builder"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Status Codes:**
- 200: Login successful
- 400: Invalid request
- 401: Invalid credentials

#### Get Current User

```
GET /auth/user
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "minecraft_builder",
  "created_at": "2025-04-27T15:49:13Z"
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

### World Management

#### List Worlds

```
GET /worlds
```

**Query Parameters:**
- `limit` (optional): Maximum number of worlds to return (default: 20)
- `offset` (optional): Offset for pagination (default: 0)

**Response:**
```json
{
  "worlds": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Creative World",
      "seed": "12345",
      "settings": {
        "gameMode": "creative",
        "difficulty": "peaceful"
      },
      "created_at": "2025-04-27T15:49:13Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "Survival World",
      "seed": "67890",
      "settings": {
        "gameMode": "survival",
        "difficulty": "normal"
      },
      "created_at": "2025-04-27T15:49:13Z"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

#### Get World Details

```
GET /worlds/{world_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Creative World",
  "seed": "12345",
  "settings": {
    "gameMode": "creative",
    "difficulty": "peaceful"
  },
  "created_at": "2025-04-27T15:49:13Z",
  "build_area": {
    "min_x": -100,
    "min_y": 0,
    "min_z": -100,
    "max_x": 100,
    "max_y": 256,
    "max_z": 100
  }
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: World not found

#### Place Blocks

```
POST /worlds/{world_id}/blocks
```

**Request Body:**
```json
{
  "start_pos": [100, 64, 100],
  "end_pos": [105, 64, 105],
  "blocks": ["minecraft:stone", "minecraft:oak_planks", "minecraft:glass"],
  "pattern": "random"
}
```

**Response:**
```json
{
  "success": true,
  "blocks_placed": 36,
  "operation_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid request
- 401: Unauthorized
- 404: World not found

#### Get Blocks

```
GET /worlds/{world_id}/blocks
```

**Query Parameters:**
- `start_x` (required): Start X coordinate
- `start_y` (required): Start Y coordinate
- `start_z` (required): Start Z coordinate
- `end_x` (required): End X coordinate
- `end_y` (required): End Y coordinate
- `end_z` (required): End Z coordinate

**Response:**
```json
{
  "blocks": [
    {
      "x": 100,
      "y": 64,
      "z": 100,
      "block_type": "minecraft:stone",
      "block_state": {
        "variant": "stone"
      }
    },
    {
      "x": 101,
      "y": 64,
      "z": 100,
      "block_type": "minecraft:oak_planks",
      "block_state": {}
    }
    // More blocks...
  ],
  "total": 36
}
```

**Status Codes:**
- 200: Success
- 400: Invalid request (e.g., area too large)
- 401: Unauthorized
- 404: World not found

#### Place Structure

```
POST /worlds/{world_id}/structures
```

**Request Body:**
```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440004",
  "position": [100, 64, 100],
  "rotation": 90,
  "mirror": false,
  "adapt_to_terrain": true
}
```

**Response:**
```json
{
  "success": true,
  "blocks_placed": 250,
  "operation_id": "550e8400-e29b-41d4-a716-446655440005"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid request
- 401: Unauthorized
- 404: World or template not found

#### Generate Terrain

```
POST /worlds/{world_id}/generate
```

**Request Body:**
```json
{
  "region": {
    "start_x": 0,
    "start_z": 0,
    "end_x": 256,
    "end_z": 256
  },
  "algorithm": "perlin_mountains",
  "parameters": {
    "height_scale": 64,
    "noise_scale": 0.01,
    "biome": "forest"
  }
}
```

**Response:**
```json
{
  "success": true,
  "operation_id": "550e8400-e29b-41d4-a716-446655440006",
  "estimated_time": 120
}
```

**Status Codes:**
- 202: Accepted (operation started)
- 400: Invalid request
- 401: Unauthorized
- 404: World not found

### Template Management

#### List Templates

```
GET /templates
```

**Query Parameters:**
- `limit` (optional): Maximum number of templates to return (default: 20)
- `offset` (optional): Offset for pagination (default: 0)
- `tags` (optional): Filter by tags (comma-separated)
- `search` (optional): Search term for name/description

**Response:**
```json
{
  "templates": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440007",
      "name": "Medieval House",
      "description": "A small medieval-style house",
      "tags": ["medieval", "house", "small"],
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-04-27T15:49:13Z",
      "updated_at": "2025-04-27T15:49:13Z",
      "preview_url": "https://example.com/previews/medieval_house.png"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440008",
      "name": "Fantasy Tower",
      "description": "A tall wizard tower with magical elements",
      "tags": ["fantasy", "tower", "magical"],
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-04-27T15:49:13Z",
      "updated_at": "2025-04-27T15:49:13Z",
      "preview_url": "https://example.com/previews/fantasy_tower.png"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized

#### Create Template

```
POST /templates
```

**Request Body:**
```json
{
  "name": "Modern House",
  "description": "A contemporary house with glass and concrete",
  "tags": ["modern", "house", "large"],
  "blueprint": {
    "dimensions": [10, 8, 12],
    "blocks": [
      // Block definitions...
    ],
    "components": [
      // Component references...
    ]
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440009",
  "name": "Modern House",
  "description": "A contemporary house with glass and concrete",
  "tags": ["modern", "house", "large"],
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-04-27T15:49:13Z",
  "updated_at": "2025-04-27T15:49:13Z",
  "preview_url": null
}
```

**Status Codes:**
- 201: Template created
- 400: Invalid request
- 401: Unauthorized

#### Get Template Details

```
GET /templates/{template_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440009",
  "name": "Modern House",
  "description": "A contemporary house with glass and concrete",
  "tags": ["modern", "house", "large"],
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-04-27T15:49:13Z",
  "updated_at": "2025-04-27T15:49:13Z",
  "preview_url": "https://example.com/previews/modern_house.png",
  "blueprint": {
    "dimensions": [10, 8, 12],
    "blocks": [
      // Block definitions...
    ],
    "components": [
      // Component references...
    ]
  }
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Template not found

#### Update Template

```
PUT /templates/{template_id}
```

**Request Body:**
```json
{
  "name": "Modern House v2",
  "description": "An updated contemporary house with glass and concrete",
  "tags": ["modern", "house", "large", "updated"],
  "blueprint": {
    "dimensions": [12, 8, 14],
    "blocks": [
      // Updated block definitions...
    ],
    "components": [
      // Updated component references...
    ]
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440009",
  "name": "Modern House v2",
  "description": "An updated contemporary house with glass and concrete",
  "tags": ["modern", "house", "large", "updated"],
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-04-27T15:49:13Z",
  "updated_at": "2025-04-27T16:00:00Z",
  "preview_url": "https://example.com/previews/modern_house.png"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid request
- 401: Unauthorized
- 403: Forbidden (not template owner)
- 404: Template not found

#### Delete Template

```
DELETE /templates/{template_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Template deleted successfully"
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 403: Forbidden (not template owner)
- 404: Template not found

### Operation Status

#### Get Operation Status

```
GET /operations/{operation_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "status": "in_progress",
  "type": "terrain_generation",
  "progress": 45,
  "estimated_completion": "2025-04-27T16:10:00Z",
  "created_at": "2025-04-27T15:49:13Z"
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Operation not found

## WebSocket API

### Connection

```
wss://api.minecraft-mcp.example.com/v1/ws
```

**Query Parameters:**
- `token`: JWT authentication token

### Events

#### Operation Progress

```json
{
  "type": "operation_progress",
  "data": {
    "operation_id": "550e8400-e29b-41d4-a716-446655440006",
    "status": "in_progress",
    "progress": 75,
    "estimated_completion": "2025-04-27T16:05:00Z"
  }
}
```

#### Operation Completed

```json
{
  "type": "operation_completed",
  "data": {
    "operation_id": "550e8400-e29b-41d4-a716-446655440006",
    "status": "completed",
    "result": {
      "blocks_modified": 65536,
      "time_taken": 120
    }
  }
}
```

#### Operation Failed

```json
{
  "type": "operation_failed",
  "data": {
    "operation_id": "550e8400-e29b-41d4-a716-446655440006",
    "status": "failed",
    "error": "Region outside build limits",
    "error_code": "BUILD_LIMIT_EXCEEDED"
  }
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details if applicable
    }
  }
}
```

### Common Error Codes

- `INVALID_REQUEST`: Request validation failed
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests
- `SERVER_ERROR`: Internal server error
- `BUILD_LIMIT_EXCEEDED`: Operation exceeds build limits
- `WORLD_NOT_CONNECTED`: Minecraft world is not accessible

## Rate Limiting

The API implements rate limiting to prevent abuse. Rate limits are applied per user and vary by endpoint.

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1619539753
```

When rate limited, the API returns a 429 Too Many Requests status code.