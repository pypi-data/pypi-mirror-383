# Gemini Vision API

FastAPI server for video analysis using Google Gemini AI's Files API.

## Features

- **Direct Gemini Files API Integration**: Videos are uploaded directly to Google's Gemini Files API for optimal processing
- **Video Analysis**: Query videos with natural language prompts
- **Timestamp Search**: Find specific moments in videos based on descriptions
- **Secure API**: Header-based authentication with admin and Gemini API keys

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set environment variables (optional):
```bash
export ADMIN_API_KEY="your-admin-api-key"  # Optional, will be generated if not set
```

3. Create a `.env` file (optional):
```bash
ADMIN_API_KEY=your-admin-api-key
```

## Running the Server

```bash
python main.py
```

Server will run on `http://localhost:8000`

## API Authentication

All endpoints require authentication headers:

- **`X-Admin-API-Key`**: Required for all endpoints (protects your API)
- **`X-Gemini-API-Key`**: Required for all endpoints (your Google Gemini API key)

## Endpoints

### File Management

#### Upload Video
Uploads a video directly to Gemini Files API for processing.

```bash
curl -X POST http://localhost:8000/files/upload \
  -H "X-Admin-API-Key: your-admin-key" \
  -H "X-Gemini-API-Key: your-gemini-key" \
  -F "file=@video.mp4"
```

Returns:
- `file_id`: Unique identifier for your file
- `gemini_name`: Gemini's internal file name
- `gemini_uri`: URI for accessing the file in Gemini

#### List Files
```bash
curl http://localhost:8000/files/list \
  -H "X-Admin-API-Key: your-admin-key" \
  -H "X-Gemini-API-Key: your-gemini-key"
```

#### Get File Info
```bash
curl http://localhost:8000/files/{file_id} \
  -H "X-Admin-API-Key: your-admin-key" \
  -H "X-Gemini-API-Key: your-gemini-key"
```

#### Delete File
```bash
curl -X DELETE http://localhost:8000/files/{file_id} \
  -H "X-Admin-API-Key: your-admin-key" \
  -H "X-Gemini-API-Key: your-gemini-key"
```

### Video Analysis

#### Query Video
Uses the uploaded Gemini file to answer questions about the video.

```bash
curl -X POST http://localhost:8000/search/query \
  -H "X-Admin-API-Key: your-admin-key" \
  -H "X-Gemini-API-Key: your-gemini-key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your-file-id",
    "prompt": "What happens in this video?"
  }'
```

#### Find Timestamp
Returns a specific timestamp in the video based on your description.

```bash
curl -X POST http://localhost:8000/search/ask \
  -H "X-Admin-API-Key: your-admin-key" \
  -H "X-Gemini-API-Key: your-gemini-key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your-file-id",
    "query": "When does the person wave?"
  }'
```

Returns:
- `timestamp`: Time in seconds
- `confidence`: Confidence score (0-1)
- `description`: Description of what happens at that timestamp

## How It Works

1. **Upload**: Videos are uploaded directly to Google's Gemini Files API
2. **Storage**: File metadata and Gemini URIs are stored locally for reference
3. **Query**: When you query a video, the API uses the Gemini file URI for efficient processing
4. **Response**: Gemini analyzes the entire video and returns detailed responses

## Security

- Admin API key protects your API from unauthorized access
- Gemini API key is passed per-request, allowing different users to use their own keys
- If ADMIN_API_KEY is not set, a temporary key is generated and displayed on startup

## Supported Formats

- Video: MP4, AVI, MOV, MKV, WebM
- Audio: WAV, MP3

## Benefits of Using Gemini Files API

- **Better Performance**: No need to extract frames locally
- **Full Video Context**: Gemini can analyze the entire video, not just sampled frames
- **Reduced Latency**: Direct API integration is faster than frame extraction
- **Lower Memory Usage**: No need to process video frames in memory
