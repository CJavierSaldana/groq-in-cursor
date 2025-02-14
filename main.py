import os
import json
import time
from typing import Any, Dict
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv
from pathlib import Path
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

app = FastAPI(title="OpenAI API Proxy with Request Tracking")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

OPENAI_BASE_URL = "https://api.openai.com/v1"
LOGS_DIR = Path("logs")

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

async def save_request_response(request_data: Dict[str, Any], response_data: Dict[str, Any], endpoint: str):
    """Save request and response data to a file with timestamp."""
    timestamp = int(time.time() * 1000)  # Get current timestamp in milliseconds
    filename = LOGS_DIR / f"{endpoint.replace('/', '_')}_{timestamp}.json"
    
    log_data = {
        "timestamp": timestamp,
        "endpoint": endpoint,
        "request": request_data,
        "response": response_data
    }
    
    with open(filename, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    return filename

@app.options("/{path:path}")
async def options_request(path: str):
    """Handle OPTIONS requests and return available methods."""
    # Define available methods based on the endpoint
    available_methods = ["OPTIONS"]
    endpoint_info = {}
    
    # Add GET for /models endpoint
    if path == "models":
        available_methods.append("GET")
        endpoint_info["GET"] = {
            "description": "List available models",
            "requires_auth": True
        }
    else:
        available_methods.append("POST")
        endpoint_info["POST"] = {
            "description": "Forward requests to OpenAI API and log interactions",
            "requires_auth": True,
            "content_type": "application/json"
        }
    
    endpoint_info["OPTIONS"] = {
        "description": "Get available methods and endpoint information",
        "requires_auth": False
    }
    
    return JSONResponse(
        content={
            "methods": available_methods,
            "description": "OpenAI API Proxy with Request Tracking",
            "endpoints": endpoint_info
        },
        headers={
            "Allow": ", ".join(available_methods),
            "Access-Control-Allow-Methods": ", ".join(available_methods),
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.get("/models")
async def get_models():
    """Get available models from OpenAI API."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{OPENAI_BASE_URL}/models",
                headers=headers
            )
            
            # Get response data
            response_data = response.json()
            
            # Add qwen-2.5-coder-32b model
            response_data["data"].append({
                "id": "qwen-2.5-coder-32b",
                "object": "model", 
                "created": int(time.time()),
                "owned_by": "system"
            })
            
            # Save request and response
            await save_request_response(
                request_data={},
                response_data=response_data,
                endpoint="models"
            )
            
            return response_data
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")

@app.post("/{path:path}")
async def proxy_request(path: str, request: Request):
    """Proxy endpoint that forwards requests to OpenAI API and logs the interaction."""
    if path == "models":
        raise HTTPException(status_code=405, detail="Method not allowed. Use GET for /models endpoint")
        
    # Get the full request body
    body = await request.json()
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Forward the request to OpenAI
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OPENAI_BASE_URL}/{path}",
                json=body,
                headers=headers
            )
            
            # Get response data
            response_data = response.json()
            
            # Save request and response
            await save_request_response(
                request_data=body,
                response_data=response_data,
                endpoint=path
            )
            
            # Return the OpenAI API response
            return response_data
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error forwarding request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 