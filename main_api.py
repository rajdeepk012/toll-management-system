"""
Main API Server Entry Point

This file starts the FastAPI server using uvicorn.
Run this file to start the HTTP server.

Usage:
    python3 main_api.py

Then visit:
    - http://localhost:8000          → API root
    - http://localhost:8000/docs     → Interactive API documentation (Swagger UI)
    - http://localhost:8000/redoc    → Alternative documentation
"""

import uvicorn

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  Starting Toll Management System API Server...")
    print("="*80 + "\n")

    # Run the FastAPI server
    uvicorn.run(
        "api:app",              # Import path: api.py → app variable
        host="0.0.0.0",         # Listen on all network interfaces
        port=8000,              # Port number
        reload=True,            # Auto-reload on code changes (development mode)
        log_level="info"        # Logging level
    )
