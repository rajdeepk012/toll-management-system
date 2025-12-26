"""
Toll Management System - Data Models
This file contains all entity definitions and enums for the system.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


# ============================================================================
# ENUMS - Define constant types used throughout the system
# ============================================================================

class VehicleType(Enum):
    """Types of vehicles that can use the toll system"""
    TWO_WHEELER = "two_wheeler"
    FOUR_WHEELER = "four_wheeler"


class PassType(Enum):
    """Types of toll passes available for purchase"""
    SINGLE = "single"        # One-time use
    RETURN = "return"        # Two uses within 24 hours
    SEVEN_DAY = "seven_day"  # Unlimited uses for 7 days


class PassStatus(Enum):
    """Current status of a toll pass"""
    ACTIVE = "active"        # Pass is valid and can be used
    EXPIRED = "expired"      # Pass validity period has ended
    EXHAUSTED = "exhausted"  # Pass has no remaining uses


# ============================================================================
# ENTITIES - Core domain objects
# ============================================================================

@dataclass
class Vehicle:
    """
    Represents a vehicle that uses the toll system.
    This is a simple identifier entity - just stores vehicle information.
    """
    registration_number: str  # Unique identifier like "MH-12-AB-1234"
    vehicle_type: VehicleType  # TWO_WHEELER or FOUR_WHEELER


@dataclass
class Toll:
    """
    Represents a toll plaza on the highway.
    A toll has multiple booths (HAS-A relationship - composition).
    """
    toll_id: str              # Unique identifier like "T1"
    name: str                 # Human-readable name like "Mumbai-Pune Toll"
    location: str             # Physical location like "Lonavala, Maharashtra"
    booths: Dict[str, 'TollBooth']  # booth_id -> TollBooth object (we'll define TollBooth next)


@dataclass
class   TollBooth:
    """
    Represents a single toll gate at a toll plaza.
    Tracks statistics for leaderboard functionality.
    Links back to parent Toll via toll_id (association).
    """
    booth_id: str                    # Unique identifier like "B1"
    toll_id: str                     # LINKING FIELD - references parent Toll
    name: str                        # Human-readable name like "Booth A"
    vehicles_processed: int = 0      # Count of vehicles that passed through
    total_charges_collected: int = 0 # Total revenue collected (in rupees)


@dataclass
class TollPass:
    """
    LINK ENTITY: Connects a Vehicle to a Toll with validity and usage tracking.

    This is the heart of the system - manages pass lifecycle and validity.

    KEY CONCEPT (Bug Fix): Validity starts from FIRST USE, not purchase time!
    - When purchased: first_used_at = None, valid_until = None
    - When first used: first_used_at = now(), valid_until = now() + duration
    """
    # Identification
    pass_id: str

    # Linking fields (connects Vehicle to Toll)
    vehicle_reg: str       # LINKING FIELD - references Vehicle by registration
    toll_id: str           # LINKING FIELD - references Toll

    # Pass details
    pass_type: PassType    # SINGLE, RETURN, or SEVEN_DAY
    vehicle_type: VehicleType  # Needed for pricing validation
    price: int             # Amount paid in rupees

    # Lifecycle tracking
    purchased_at: datetime        # When the pass was bought
    first_used_at: Optional[datetime] = None  # When first used (None until used)
    valid_until: Optional[datetime] = None    # Expiry time (calculated on first use)

    # Usage tracking
    uses_remaining: int = 1    # How many uses left (default 1, updated at purchase)

    # Status
    status: PassStatus = PassStatus.ACTIVE  # Current state


@dataclass
class Transaction:
    """
    Immutable audit record of all toll activities.
    Records both PASSAGE events (vehicle passing through) and PURCHASE events (buying a pass).
    """
    transaction_id: str
    booth_id: str              # Which booth processed this transaction
    toll_id: str               # Which toll plaza
    vehicle_reg: str           # Which vehicle
    vehicle_type: VehicleType  # Type of vehicle (for reporting)
    transaction_type: str      # "PASSAGE" or "PURCHASE"
    pass_id: Optional[str]     # Related pass (None for direct cash payments in future)
    amount: int                # Money involved (0 for free passage with valid pass)
    timestamp: datetime        # When this happened
