"""
Main FastAPI application for AI Telematics Report Interpreter.

FastAPI is a modern Python web framework that automatically generates
API documentation and validates request/response data.

This file defines the API endpoints (URLs) that the frontend calls.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .models import InterpretRequest, InterpretResponse
from .ai_service import interpret_report

# Load environment variables from .env file
load_dotenv()

# Create the FastAPI application instance
app = FastAPI(
    title="AI Telematics Report Interpreter",
    description="Interprets telematics reports using AI for different user profiles",
    version="1.0.0",
)

# CORS Middleware - allows the frontend (running on a different port)
# to make requests to this backend.
# Without this, the browser would block requests between different origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Health check endpoint - verifies the API is running."""
    return {
        "status": "ok",
        "message": "AI Telematics Report Interpreter API is running",
    }


@app.get("/health")
def health_check():
    """Health check for Docker."""
    return {"status": "healthy"}


@app.post("/interpret", response_model=InterpretResponse)
def interpret(request: InterpretRequest):
    """
    Main endpoint: receives a telematics report and a user profile,
    then returns an AI-generated interpretation.

    - **report**: The telematics report data (JSON)
    - **profile**: User profile ('gerente' or 'operaciones')
    """
    try:
        # Convert the Pydantic model to a dictionary for the AI service
        report_dict = request.report.model_dump()

        # Call the AI service to interpret the report
        result = interpret_report(report_dict, request.profile)

        # Return the structured response
        return InterpretResponse(
            profile=request.profile,
            interpretation=result["interpretation"],
            model_used=result["model_used"],
            tokens_used=result["tokens_used"],
        )

    except ValueError as e:
        # ValueError is raised when the API key is missing or profile is invalid
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch any unexpected errors and return a 500 response
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )
