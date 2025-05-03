from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files
static_dir = Path(__file__).parent.parent / "assets"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir)), name="assets")

@app.get("/")
async def read_root():
    try:
        return HTMLResponse(
            content="""
            <html>
                <head>
                    <title>TrendLens Dashboard</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 0;
                            padding: 20px;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                            min-height: 100vh;
                            background: #f0f2f5;
                        }
                        h1 {
                            color: #1a73e8;
                            margin-bottom: 20px;
                        }
                        p {
                            color: #5f6368;
                            text-align: center;
                            max-width: 600px;
                            line-height: 1.6;
                        }
                    </style>
                </head>
                <body>
                    <h1>Welcome to TrendLens Dashboard</h1>
                    <p>
                        This is a serverless deployment of TrendLens. 
                        For the full interactive dashboard experience, 
                        please run the Streamlit app locally.
                    </p>
                </body>
            </html>
            """
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# API endpoints for data processing
@app.get("/api/features")
async def get_features():
    try:
        from modules.feature_engineering import generate_features
        # Note: This is just a placeholder. In production,
        # you would need to handle data storage and retrieval
        return JSONResponse({"message": "Feature engineering endpoint"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_insights():
    try:
        from modules.insights import generate_insights
        # Note: This is just a placeholder. In production,
        # you would need to handle data storage and retrieval
        return JSONResponse({"message": "Insights endpoint"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def server_error(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred"}
    )