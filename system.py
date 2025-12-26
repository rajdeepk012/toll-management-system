"""
Toll Management System - Business Logic
This file contains the core system that manages tolls, passes, and transactions.

REFACTORED: Now uses Repository Pattern for data access (Phase 2).
REFACTORED: Now uses Service Layer for business logic (Phase 2 Session 7).
REFACTORED: Now uses MySQL for persistent storage (Phase 2 Session 9).
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from models import (
    Toll, TollBooth, Vehicle, TollPass, Transaction,
    VehicleType, PassType, PassStatus
)

# MySQL repositories (Phase 2 Session 9)
from repositories.toll_repository_mysql import TollRepository
from repositories.vehicle_repository_mysql import VehicleRepository
from repositories.pass_repository_mysql import PassRepository
from repositories.transaction_repository_mysql import TransactionRepository

from services import (
    PassPricingService,
    PassValidationService,
    PassLifecycleService
)


# ============================================================================
# MAIN SYSTEM CLASS
# ============================================================================
# NOTE: Pricing configuration moved to PassPricingService (Phase 2 Session 7)

class TollManagementSystem:
    """
    Core system that manages tolls, vehicles, passes, and transactions.

    REFACTORED: Uses Repository Pattern for data access.
    Business logic stays here, data access delegated to repositories.
    """

    def __init__(self, db_session: Session):
        """
        Initialize with repository and service dependencies.

        Args:
            db_session: SQLAlchemy database session for MySQL access
        """
        # PHASE 2 Session 9: Store database session
        self.db = db_session

        # PHASE 2 Session 9: Inject database session into MySQL repositories
        self.toll_repo = TollRepository(db_session)
        self.vehicle_repo = VehicleRepository(db_session)
        self.pass_repo = PassRepository(db_session)
        self.transaction_repo = TransactionRepository(db_session)

        # PHASE 2 Session 7: Use services for business logic
        self.pricing_service = PassPricingService()
        self.validation_service = PassValidationService()
        self.lifecycle_service = PassLifecycleService(self.pricing_service)

        # Counters for generating IDs
        # PHASE 2 Session 9: Load next available IDs from MySQL
        # Count existing passes and transactions to determine next ID
        existing_passes = self.pass_repo.count()
        existing_transactions = self.transaction_repo.count()

        self._next_pass_id = existing_passes + 1
        self._next_transaction_id = existing_transactions + 1

    # ========================================================================
    # HELPER METHODS (Internal, start with _)
    # ========================================================================

    def _generate_pass_id(self) -> str:
        """Generate unique pass ID"""
        pass_id = f"PASS-{self._next_pass_id:04d}"
        self._next_pass_id += 1
        return pass_id

    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        txn_id = f"TXN-{self._next_transaction_id:05d}"
        self._next_transaction_id += 1
        return txn_id

    def _format_duration(self, duration: timedelta) -> str:
        """
        Convert timedelta to human-readable string.

        REFACTORED: Delegates to PassPricingService (Phase 2 Session 7).
        """
        return self.pricing_service.format_duration(duration)

    def _find_active_pass(self, vehicle_reg: str, toll_id: str) -> Optional[TollPass]:
        """
        Search for an active pass for a vehicle at a specific toll.

        REFACTORED: Delegates to PassRepository (Phase 2).
        This helper method now just wraps the repository call for backward compatibility.
        """
        return self.pass_repo.find_active_pass(vehicle_reg, toll_id)

    # ========================================================================
    # FEATURE METHODS (We'll implement these one by one)
    # ========================================================================

    def display_pass_options(self, vehicle_type: VehicleType) -> List[Dict]:
        """
        Display available pass options for a given vehicle type.

        REFACTORED: Uses PassPricingService for pricing logic (Phase 2 Session 7).

        Args:
            vehicle_type: Type of vehicle (TWO_WHEELER or FOUR_WHEELER)

        Returns:
            List of dicts, each containing pass details:
            {
                "pass_type": PassType enum,
                "price": int (in rupees),
                "duration": str (human-readable),
                "uses": int (number of uses),
                "description": str (explanation)
            }
        """
        options = []

        # Loop through all pass types
        for pass_type in PassType:
            # REFACTORED: Get price from pricing service
            price = self.pricing_service.get_pass_price(vehicle_type, pass_type)

            # REFACTORED: Get duration from pricing service
            duration = self.pricing_service.get_pass_duration(pass_type)
            duration_str = self._format_duration(duration)

            # REFACTORED: Get number of uses from pricing service
            uses = self.pricing_service.get_pass_uses(pass_type)

            # Create description based on pass type
            if pass_type == PassType.SINGLE:
                description = "Single journey pass, valid for 1 use"
            elif pass_type == PassType.RETURN:
                description = "Return journey pass, valid for 2 uses"
            else:  # SEVEN_DAY
                description = "Weekly pass, unlimited uses for 7 days"

            # Build the option dict
            option = {
                "pass_type": pass_type,
                "price": price,
                "duration": duration_str,
                "uses": uses,
                "description": description
            }

            options.append(option)

        return options

    def purchase_pass(self, vehicle_reg: str, toll_id: str, booth_id: str, pass_type: PassType) -> TollPass:
        """
        Purchase a toll pass for a vehicle at a specific toll booth.

        Args:
            vehicle_reg: Vehicle registration number
            toll_id: Toll plaza ID
            booth_id: Booth ID where purchase is happening
            pass_type: Type of pass to purchase (SINGLE, RETURN, SEVEN_DAY)

        Returns:
            The newly created TollPass object

        Raises:
            ValueError: If validation fails (vehicle/toll not found, already has pass, etc.)
        """
        # ============ STEP 1: VALIDATIONS ============

        # REFACTORED: Use repositories instead of direct dict access
        # Validate vehicle exists
        if not self.vehicle_repo.exists(vehicle_reg):
            raise ValueError(f"Vehicle {vehicle_reg} not registered in system")

        # Validate toll exists
        if not self.toll_repo.exists(toll_id):
            raise ValueError(f"Toll {toll_id} not found")

        # Validate booth exists at this toll
        toll = self.toll_repo.get_toll(toll_id)
        if booth_id not in toll.booths:
            raise ValueError(f"Booth {booth_id} not found at toll {toll_id}")

        # Check if vehicle already has ACTIVE pass at this toll
        existing_pass = self._find_active_pass(vehicle_reg, toll_id)
        if existing_pass:
            raise ValueError(
                f"Vehicle already has an active {existing_pass.pass_type.value} pass at this toll. "
                f"Pass ID: {existing_pass.pass_id}"
            )

        # ============ STEP 2: CALCULATE PRICE ============

        # REFACTORED: Use repository to get vehicle
        vehicle = self.vehicle_repo.get_vehicle(vehicle_reg)
        vehicle_type = vehicle.vehicle_type

        # REFACTORED: Use pricing service to get price and uses
        price = self.pricing_service.get_pass_price(vehicle_type, pass_type)
        uses = self.pricing_service.get_pass_uses(pass_type)

        # ============ STEP 3: CREATE TOLL PASS ============

        pass_id = self._generate_pass_id()

        new_pass = TollPass(
            pass_id=pass_id,
            vehicle_reg=vehicle_reg,
            toll_id=toll_id,
            pass_type=pass_type,
            vehicle_type=vehicle_type,
            price=price,
            purchased_at=datetime.now(),
            first_used_at=None,           # Not used yet
            valid_until=None,             # Will be set on first use
            uses_remaining=uses,          # REFACTORED: Use pricing service
            status=PassStatus.ACTIVE
        )

        # REFACTORED: Store pass using repository
        self.pass_repo.add_pass(new_pass)

        # ============ STEP 4: RECORD TRANSACTION ============

        txn_id = self._generate_transaction_id()

        transaction = Transaction(
            transaction_id=txn_id,
            booth_id=booth_id,
            toll_id=toll_id,
            vehicle_reg=vehicle_reg,
            vehicle_type=vehicle_type,
            transaction_type="PURCHASE",
            pass_id=pass_id,
            amount=price,
            timestamp=datetime.now()
        )

        # REFACTORED: Store transaction using repository
        self.transaction_repo.add_transaction(transaction)

        # ============ STEP 5: UPDATE BOOTH STATISTICS ============

        booth = toll.booths[booth_id]
        # For purchase: add revenue but DON'T increment vehicles_processed
        booth.total_charges_collected += price

        # PHASE 2 Session 9: Persist booth updates to MySQL
        self.toll_repo.update_booth(booth)

        return new_pass

    def process_vehicle(self, vehicle_reg: str, toll_id: str, booth_id: str) -> Dict:
        """
        Process a vehicle passing through a toll booth.
        Checks for valid pass, allows/denies passage, updates statistics.

        Args:
            vehicle_reg: Vehicle registration number
            toll_id: Toll plaza ID
            booth_id: Booth ID where vehicle is passing

        Returns:
            Dict with keys:
            - "allowed": bool (whether passage was allowed)
            - "message": str (explanation)
            - "pass_info": dict or None (details about the pass used)
            - "pass_options": list or None (available passes if denied)
        """
        # ============ STEP 1: VALIDATIONS ============

        # REFACTORED: Use repositories for validation
        if not self.vehicle_repo.exists(vehicle_reg):
            return {
                "allowed": False,
                "message": f"Vehicle {vehicle_reg} not registered",
                "pass_info": None,
                "pass_options": None
            }

        if not self.toll_repo.exists(toll_id):
            return {
                "allowed": False,
                "message": f"Toll {toll_id} not found",
                "pass_info": None,
                "pass_options": None
            }

        toll = self.toll_repo.get_toll(toll_id)
        if booth_id not in toll.booths:
            return {
                "allowed": False,
                "message": f"Booth {booth_id} not found at toll {toll_id}",
                "pass_info": None,
                "pass_options": None
            }

        vehicle = self.vehicle_repo.get_vehicle(vehicle_reg)
        booth = toll.booths[booth_id]

        # ============ STEP 2: FIND ACTIVE PASS ============

        toll_pass = self._find_active_pass(vehicle_reg, toll_id)

        if toll_pass is None:
            # No active pass found - DENY passage, show options
            pass_options = self.display_pass_options(vehicle.vehicle_type)
            return {
                "allowed": False,
                "message": "No valid pass found for this toll",
                "pass_info": None,
                "pass_options": pass_options
            }

        # ============ STEP 3: VALIDATE PASS (Time + Uses) ============

        current_time = datetime.now()

        # REFACTORED: Use validation service to check pass validity
        validation_result = self.validation_service.validate_pass(toll_pass)

        # If this is the FIRST USE, set validity timer (BUG FIX!)
        if validation_result.is_first_use:
            # REFACTORED: Use lifecycle service to set first use
            self.lifecycle_service.set_first_use(toll_pass, current_time)
            # PHASE 2 Session 9: Persist pass updates to MySQL
            self.pass_repo.update_pass(toll_pass)

        # Update pass status based on validation results
        if not validation_result.is_first_use:
            # REFACTORED: Use lifecycle service to update status
            self.lifecycle_service.update_pass_status(
                toll_pass,
                validation_result.is_time_valid,
                validation_result.has_uses_remaining
            )
            # PHASE 2 Session 9: Persist pass updates to MySQL
            self.pass_repo.update_pass(toll_pass)

        # Check if pass can be used
        if not validation_result.is_valid:
            # Pass is invalid (expired or exhausted) - DENY passage
            pass_options = self.display_pass_options(vehicle.vehicle_type)

            # REFACTORED: Use validation result reason
            reason = validation_result.reason

            return {
                "allowed": False,
                "message": f"Pass {toll_pass.pass_id} is {reason}",
                "pass_info": {
                    "pass_id": toll_pass.pass_id,
                    "pass_type": toll_pass.pass_type.value,
                    "status": toll_pass.status.value,
                    "valid_until": toll_pass.valid_until.strftime("%Y-%m-%d %H:%M:%S"),
                    "uses_remaining": toll_pass.uses_remaining
                },
                "pass_options": pass_options
            }

        # ============ STEP 4: ALLOW PASSAGE - USE THE PASS ============

        # REFACTORED: Use lifecycle service to use the pass
        self.lifecycle_service.use_pass(toll_pass)

        # PHASE 2 Session 9: Persist pass updates to MySQL
        self.pass_repo.update_pass(toll_pass)

        # ============ STEP 5: RECORD TRANSACTION ============

        txn_id = self._generate_transaction_id()

        transaction = Transaction(
            transaction_id=txn_id,
            booth_id=booth_id,
            toll_id=toll_id,
            vehicle_reg=vehicle_reg,
            vehicle_type=vehicle.vehicle_type,
            transaction_type="PASSAGE",  # This is a passage, not a purchase
            pass_id=toll_pass.pass_id,
            amount=0,  # No money collected (using valid pass)
            timestamp=current_time
        )

        # REFACTORED: Store transaction using repository
        self.transaction_repo.add_transaction(transaction)

        # ============ STEP 6: UPDATE BOOTH STATISTICS ============

        # For passage: increment vehicles_processed, no revenue added
        booth.vehicles_processed += 1

        # PHASE 2 Session 9: Persist booth updates to MySQL
        self.toll_repo.update_booth(booth)

        # ============ STEP 7: RETURN SUCCESS ============

        return {
            "allowed": True,
            "message": "Passage allowed",
            "pass_info": {
                "pass_id": toll_pass.pass_id,
                "pass_type": toll_pass.pass_type.value,
                "status": toll_pass.status.value,
                "valid_until": toll_pass.valid_until.strftime("%Y-%m-%d %H:%M:%S"),
                "uses_remaining": toll_pass.uses_remaining
            },
            "pass_options": None
        }

    def get_leaderboard(self, metric: str = "vehicles_processed") -> List[Dict]:
        """
        Get leaderboard of booths sorted by specified metric.

        Args:
            metric: Either "vehicles_processed" or "total_charges_collected"

        Returns:
            List of booth info dicts, sorted by metric (descending - highest first)
            Each dict contains:
            {
                "rank": int,
                "toll_id": str,
                "toll_name": str,
                "booth_id": str,
                "vehicles_processed": int,
                "total_charges_collected": int
            }
        """
        # ============ STEP 1: VALIDATE METRIC ============

        valid_metrics = ["vehicles_processed", "total_charges_collected"]
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric '{metric}'. Must be one of: {valid_metrics}")

        # ============ STEP 2: COLLECT ALL BOOTHS ============

        booth_stats = []

        # REFACTORED: Use repository instead of direct dict access
        # Loop through all tolls
        for toll in self.toll_repo.get_all_tolls():
            # Loop through all booths at this toll
            for booth_id, booth in toll.booths.items():
                booth_info = {
                    "toll_id": toll.toll_id,
                    "toll_name": toll.name,
                    "booth_id": booth_id,
                    "vehicles_processed": booth.vehicles_processed,
                    "total_charges_collected": booth.total_charges_collected
                }
                booth_stats.append(booth_info)

        # ============ STEP 3: SORT BY METRIC ============

        # Sort by the specified metric (descending - highest first)
        booth_stats.sort(key=lambda b: b[metric], reverse=True)

        # ============ STEP 4: ADD RANKINGS ============

        # Add rank field (1 for highest, 2 for second, etc.)
        for i, booth in enumerate(booth_stats, start=1):
            booth["rank"] = i

        return booth_stats

    # ========================================================================
    # SETUP METHODS (For populating test data)
    # ========================================================================

    def add_toll(self, toll: Toll) -> None:
        """
        Add a toll plaza to the system.

        REFACTORED: Uses TollRepository (Phase 2).
        """
        self.toll_repo.add_toll(toll)

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """
        Register a vehicle in the system.

        REFACTORED: Uses VehicleRepository (Phase 2).
        """
        self.vehicle_repo.add_vehicle(vehicle)
