from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import files, search, live
import uvicorn

app = FastAPI(
    title="Gemini Vision API",
    version="1.0.0",
    description="""
    API for video analysis using Google Gemini AI.

    ## Authentication

    All endpoints require headers:
    - `X-Admin-API-Key`: Your admin API key (set via ADMIN_API_KEY environment variable)
    - `X-Gemini-API-Key`: Your Google Gemini API key (required for all file and search operations)

    ## Environment Variables

    - `ADMIN_API_KEY`: Admin API key for authenticating requests (generated if not set)
    """,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(search.router)
app.include_router(live.router)


@app.get("/")
async def root():
    return {
        "message": "Gemini Vision API",
        "version": "1.0.0",
        "security": "All endpoints require X-Admin-API-Key header",
        "endpoints": {
            "upload": "POST /files/upload (uploads to Gemini Files API)",
            "list_files": "GET /files/list",
            "get_file": "GET /files/{file_id}",
            "delete_file": "DELETE /files/{file_id}",
            "query_video": "POST /search/query (uses Gemini file URI)",
            "ask_timestamp": "POST /search/ask (supports timestamps)",
            "detect_objects": "POST /search/boxes (object detection with bounding boxes)",
            "live_udp": "POST /live/udp (UDP stream processing with SSE)",
        },
        "note": "All endpoints require X-Admin-API-Key and X-Gemini-API-Key headers",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
