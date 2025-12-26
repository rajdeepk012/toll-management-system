"""
FastAPI Routes - HTTP Endpoint Definitions

This file maps HTTP URLs to controller methods.
It's the "waiter" that takes requests and calls the kitchen (controllers).

REFACTORED: Now uses MySQL with dependency injection (Phase 2 Session 9).
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel, ConfigDict
from typing import Optional
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

# Import our existing components
from system import TollManagementSystem
from controllers import VehicleController, PassController, LeaderboardController
from models import Toll, TollBooth, Vehicle, VehicleType

# Import database components
from database.config import get_db

# ============================================================================
# STEP 1: Dependency Injection Helper
# ============================================================================
# PHASE 2 Session 9: Create system per-request with database session

def get_system(db: Session = Depends(get_db)) -> TollManagementSystem:
    """
    Dependency injection function to create TollManagementSystem per request.

    This ensures each HTTP request gets:
    - A fresh database session
    - A system instance with that session
    - Proper session lifecycle (commit/rollback/close)

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        TollManagementSystem instance with database session
    """
    return TollManagementSystem(db)


# ============================================================================
# STEP 2: Lifespan Context Manager (Replaces @app.on_event)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    This is the modern way (replaces deprecated @app.on_event).

    Everything before 'yield' runs on startup.
    Everything after 'yield' runs on shutdown.

    PHASE 2 Session 9: Uses database session to initialize test data.
    """
    # STARTUP: Initialize test data in MySQL (only if empty)
    print("\n" + "="*80)
    print("  Toll Management System API Starting...")
    print("="*80)

    # Create database session for startup initialization
    from database.config import SessionLocal
    db = SessionLocal()

    try:
        # Create system with database session
        startup_system = TollManagementSystem(db)

        # Check if data already exists (from previous runs)
        existing_tolls = startup_system.toll_repo.count()

        if existing_tolls == 0:
            print("  Initializing test data in MySQL...")

            # Create test tolls
            toll1_booths = {
                "B1": TollBooth(booth_id="B1", name="Booth 1", toll_id="T1"),
                "B2": TollBooth(booth_id="B2", name="Booth 2", toll_id="T1"),
                "B3": TollBooth(booth_id="B3", name="Booth 3", toll_id="T1")
            }
            toll1 = Toll(
                toll_id="T1",
                name="Mumbai-Pune Expressway Toll",
                location="Khandala",
                booths=toll1_booths
            )

            toll2_booths = {
                "B1": TollBooth(booth_id="B1", name="Booth 1", toll_id="T2"),
                "B2": TollBooth(booth_id="B2", name="Booth 2", toll_id="T2")
            }
            toll2 = Toll(
                toll_id="T2",
                name="Delhi-Jaipur Highway Toll",
                location="Gurgaon",
                booths=toll2_booths
            )

            # Create test vehicles
            vehicle1 = Vehicle(
                registration_number="MH-12-AB-1234",
                vehicle_type=VehicleType.TWO_WHEELER
            )
            vehicle2 = Vehicle(
                registration_number="MH-14-CD-5678",
                vehicle_type=VehicleType.FOUR_WHEELER
            )
            vehicle3 = Vehicle(
                registration_number="KA-03-GH-3456",
                vehicle_type=VehicleType.TWO_WHEELER
            )
            vehicle4 = Vehicle(
                registration_number="DL-01-EF-9012",
                vehicle_type=VehicleType.FOUR_WHEELER
            )

            # Add to system (persists to MySQL)
            startup_system.add_toll(toll1)
            startup_system.add_toll(toll2)
            startup_system.add_vehicle(vehicle1)
            startup_system.add_vehicle(vehicle2)
            startup_system.add_vehicle(vehicle3)
            startup_system.add_vehicle(vehicle4)

            print("  ✓ Created 2 tolls with multiple booths")
            print("  ✓ Registered 4 test vehicles")
        else:
            print(f"  ✓ Found existing data in MySQL ({existing_tolls} tolls)")
            print("  ✓ Skipping test data initialization")

        print("\n  API is ready! Visit http://localhost:8000/docs for interactive documentation")
        print("="*80 + "\n")

    finally:
        # Close the startup session
        db.close()

    yield  # Server runs here

    # SHUTDOWN: Cleanup (if needed)
    print("\n" + "="*80)
    print("  Toll Management System API Shutting Down...")
    print("="*80 + "\n")


# ============================================================================
# STEP 3: Create FastAPI App with Lifespan
# ============================================================================

app = FastAPI(
    title="Toll Management System API",
    description="API for managing toll plazas, passes, and vehicle processing",
    version="1.0.0",
    lifespan=lifespan  # Modern way to handle startup/shutdown
)

# ============================================================================
# STEP 3: Define Request/Response Models (DTOs)
# ============================================================================
# These are Pydantic models that define the structure of HTTP requests/responses

class PurchasePassRequest(BaseModel):
    """Request body for purchasing a pass"""
    vehicle_reg: str
    toll_id: str
    booth_id: str
    pass_type: str  # "single", "return", or "seven_day"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicle_reg": "MH-12-AB-1234",
                "toll_id": "T1",
                "booth_id": "B1",
                "pass_type": "return"
            }
        }
    )


class ProcessVehicleRequest(BaseModel):
    """Request body for processing vehicle passage"""
    vehicle_reg: str
    toll_id: str
    booth_id: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicle_reg": "MH-12-AB-1234",
                "toll_id": "T1",
                "booth_id": "B1"
            }
        }
    )


# ============================================================================
# STEP 4: Define API Routes (Endpoints)
# ============================================================================

# ----------------------------------------------------------------------------
# Health Check Endpoint
# ----------------------------------------------------------------------------

@app.get("/")
def root():
    """
    Health check endpoint - verify API is running

    Try it: http://localhost:8000/
    """
    return {
        "message": "Toll Management System API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """
    Detailed health check

    Try it: http://localhost:8000/health
    """
    return {
        "status": "healthy",
        "system": "operational"
    }


# ----------------------------------------------------------------------------
# Pass Endpoints
# ----------------------------------------------------------------------------

@app.get("/api/pass/options")
def get_pass_options(
    vehicle_type: str = Query(..., description="Vehicle type: two_wheeler or four_wheeler"),
    system: TollManagementSystem = Depends(get_system)
):
    """
    Get available pass options for a vehicle type

    Try it: http://localhost:8000/api/pass/options?vehicle_type=two_wheeler

    Args:
        vehicle_type: Type of vehicle (two_wheeler or four_wheeler)
        system: TollManagementSystem instance (injected)

    Returns:
        List of available pass options with pricing
    """
    # Create controller with injected system
    pass_controller = PassController(system)

    # Call the controller
    result = pass_controller.get_pass_options(vehicle_type)

    # Check if controller returned an error
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])

    # Return successful response
    return result


@app.post("/api/pass/purchase")
def purchase_pass(
    request: PurchasePassRequest,
    system: TollManagementSystem = Depends(get_system)
):
    """
    Purchase a toll pass

    Try it: POST http://localhost:8000/api/pass/purchase
    Body: {"vehicle_reg": "MH-12-AB-1234", "toll_id": "T1", "booth_id": "B1", "pass_type": "return"}

    Args:
        request: Purchase request with vehicle, toll, booth, and pass type info
        system: TollManagementSystem instance (injected)

    Returns:
        Newly created pass details
    """
    # Create controller with injected system
    pass_controller = PassController(system)

    # Call the controller
    result = pass_controller.purchase_pass(
        vehicle_reg=request.vehicle_reg,
        toll_id=request.toll_id,
        booth_id=request.booth_id,
        pass_type=request.pass_type
    )

    # Check if controller returned an error
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])

    # Return successful response
    return result


# ----------------------------------------------------------------------------
# Vehicle Endpoints
# ----------------------------------------------------------------------------

@app.post("/api/vehicle/process")
def process_vehicle(
    request: ProcessVehicleRequest,
    system: TollManagementSystem = Depends(get_system)
):
    """
    Process a vehicle passing through a toll booth

    Try it: POST http://localhost:8000/api/vehicle/process
    Body: {"vehicle_reg": "MH-12-AB-1234", "toll_id": "T1", "booth_id": "B1"}

    This is where the BUG FIX happens!
    - First use: Sets validity timer from NOW (not purchase time)
    - Subsequent uses: Validates against time and usage limits

    Args:
        request: Vehicle passage request with vehicle, toll, and booth info
        system: TollManagementSystem instance (injected)

    Returns:
        Passage result (allowed/denied) with pass info
    """
    # Create controller with injected system
    vehicle_controller = VehicleController(system)

    # Call the controller
    result = vehicle_controller.process_vehicle_passage(
        vehicle_reg=request.vehicle_reg,
        toll_id=request.toll_id,
        booth_id=request.booth_id
    )

    # Check if controller returned an error
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])

    # Return successful response
    return result


# ----------------------------------------------------------------------------
# Leaderboard Endpoint
# ----------------------------------------------------------------------------

@app.get("/api/leaderboard")
def get_leaderboard(
    metric: str = Query("vehicles_processed", description="Metric to sort by: vehicles_processed or total_charges_collected"),
    system: TollManagementSystem = Depends(get_system)
):
    """
    Get booth leaderboard sorted by metric

    Try it: http://localhost:8000/api/leaderboard?metric=vehicles_processed

    Args:
        metric: Sorting metric (vehicles_processed or total_charges_collected)
        system: TollManagementSystem instance (injected)

    Returns:
        Ranked list of booths by the specified metric
    """
    # Create controller with injected system
    leaderboard_controller = LeaderboardController(system)

    # Call the controller
    result = leaderboard_controller.get_leaderboard(metric)

    # Check if controller returned an error
    if result["status"] == "error":
        raise HTTPException(status_code=result["code"], detail=result["message"])

    # Return successful response
    return result


# ============================================================================
