"""
Model Converters - Convert between Domain Models and Database Models

This file contains helper functions to convert:
- Domain models (models.py) ↔ Database models (db_models.py)

Why separate converters?
1. DRY - Conversion logic written ONCE
2. Maintainability - Easy to update in one place
3. Testability - Can test converters separately
4. Clean architecture - Repositories stay simple
"""

from typing import Optional
from datetime import datetime

# Domain models (business logic)
from models import (
    Toll, TollBooth, Vehicle, TollPass, Transaction,
    VehicleType, PassType, PassStatus
)

# Database models (SQLAlchemy ORM)
from database.db_models import (
    TollDB, TollBoothDB, VehicleDB, TollPassDB, TransactionDB,
    VehicleTypeDB, PassTypeDB, PassStatusDB
)


# ============================================================================
# Enum Converters
# ============================================================================

def vehicle_type_to_db(vehicle_type: VehicleType) -> VehicleTypeDB:
    """Convert domain VehicleType to database VehicleTypeDB"""
    mapping = {
        VehicleType.TWO_WHEELER: VehicleTypeDB.TWO_WHEELER,
        VehicleType.FOUR_WHEELER: VehicleTypeDB.FOUR_WHEELER,
    }
    return mapping[vehicle_type]


def db_to_vehicle_type(db_type: VehicleTypeDB) -> VehicleType:
    """Convert database VehicleTypeDB to domain VehicleType"""
    mapping = {
        VehicleTypeDB.TWO_WHEELER: VehicleType.TWO_WHEELER,
        VehicleTypeDB.FOUR_WHEELER: VehicleType.FOUR_WHEELER,
    }
    return mapping[db_type]


def pass_type_to_db(pass_type: PassType) -> PassTypeDB:
    """Convert domain PassType to database PassTypeDB"""
    mapping = {
        PassType.SINGLE: PassTypeDB.SINGLE,
        PassType.RETURN: PassTypeDB.RETURN,
        PassType.SEVEN_DAY: PassTypeDB.SEVEN_DAY,
    }
    return mapping[pass_type]


def db_to_pass_type(db_type: PassTypeDB) -> PassType:
    """Convert database PassTypeDB to domain PassType"""
    mapping = {
        PassTypeDB.SINGLE: PassType.SINGLE,
        PassTypeDB.RETURN: PassType.RETURN,
        PassTypeDB.SEVEN_DAY: PassType.SEVEN_DAY,
    }
    return mapping[db_type]


def pass_status_to_db(status: PassStatus) -> PassStatusDB:
    """Convert domain PassStatus to database PassStatusDB"""
    mapping = {
        PassStatus.ACTIVE: PassStatusDB.ACTIVE,
        PassStatus.EXPIRED: PassStatusDB.EXPIRED,
        PassStatus.EXHAUSTED: PassStatusDB.EXHAUSTED,
    }
    return mapping[status]


def db_to_pass_status(db_status: PassStatusDB) -> PassStatus:
    """Convert database PassStatusDB to domain PassStatus"""
    mapping = {
        PassStatusDB.ACTIVE: PassStatus.ACTIVE,
        PassStatusDB.EXPIRED: PassStatus.EXPIRED,
        PassStatusDB.EXHAUSTED: PassStatus.EXHAUSTED,
    }
    return mapping[db_status]


# ============================================================================
# Vehicle Converters
# ============================================================================

def vehicle_to_db(vehicle: Vehicle) -> VehicleDB:
    """
    Convert domain Vehicle to database VehicleDB

    Args:
        vehicle: Domain model Vehicle

    Returns:
        Database model VehicleDB
    """
    return VehicleDB(
        registration_number=vehicle.registration_number,
        vehicle_type=vehicle_type_to_db(vehicle.vehicle_type)
    )


def db_to_vehicle(db_vehicle: VehicleDB) -> Vehicle:
    """
    Convert database VehicleDB to domain Vehicle

    Args:
        db_vehicle: Database model VehicleDB

    Returns:
        Domain model Vehicle
    """
    return Vehicle(
        registration_number=db_vehicle.registration_number,
        vehicle_type=db_to_vehicle_type(db_vehicle.vehicle_type)
    )


# ============================================================================
# TollPass Converters (MOST IMPORTANT - Has Bug Fix Fields!)
# ============================================================================

def toll_pass_to_db(toll_pass: TollPass) -> TollPassDB:
    """
    Convert domain TollPass to database TollPassDB

    Args:
        toll_pass: Domain model TollPass

    Returns:
        Database model TollPassDB
    """
    return TollPassDB(
        pass_id=toll_pass.pass_id,
        vehicle_reg=toll_pass.vehicle_reg,
        toll_id=toll_pass.toll_id,
        pass_type=pass_type_to_db(toll_pass.pass_type),
        vehicle_type=vehicle_type_to_db(toll_pass.vehicle_type),
        price=toll_pass.price,
        status=pass_status_to_db(toll_pass.status),
        uses_remaining=toll_pass.uses_remaining,
        purchased_at=toll_pass.purchased_at,
        first_used_at=toll_pass.first_used_at,  # BUG FIX field!
        valid_until=toll_pass.valid_until        # BUG FIX field!
    )


def db_to_toll_pass(db_pass: TollPassDB) -> TollPass:
    """
    Convert database TollPassDB to domain TollPass

    Args:
        db_pass: Database model TollPassDB

    Returns:
        Domain model TollPass
    """
    return TollPass(
        pass_id=db_pass.pass_id,
        vehicle_reg=db_pass.vehicle_reg,
        toll_id=db_pass.toll_id,
        pass_type=db_to_pass_type(db_pass.pass_type),
        vehicle_type=db_to_vehicle_type(db_pass.vehicle_type),
        price=db_pass.price,
        status=db_to_pass_status(db_pass.status),
        uses_remaining=db_pass.uses_remaining,
        purchased_at=db_pass.purchased_at,
        first_used_at=db_pass.first_used_at,  # BUG FIX field!
        valid_until=db_pass.valid_until        # BUG FIX field!
    )


# ============================================================================
# Transaction Converters
# ============================================================================

def transaction_to_db(transaction: Transaction) -> TransactionDB:
    """
    Convert domain Transaction to database TransactionDB

    Args:
        transaction: Domain model Transaction

    Returns:
        Database model TransactionDB
    """
    return TransactionDB(
        transaction_id=transaction.transaction_id,
        booth_id=transaction.booth_id,
        toll_id=transaction.toll_id,
        vehicle_reg=transaction.vehicle_reg,
        vehicle_type=vehicle_type_to_db(transaction.vehicle_type),
        transaction_type=transaction.transaction_type,
        pass_id=transaction.pass_id,
        amount=transaction.amount,
        timestamp=transaction.timestamp
    )


def db_to_transaction(db_txn: TransactionDB) -> Transaction:
    """
    Convert database TransactionDB to domain Transaction

    Args:
        db_txn: Database model TransactionDB

    Returns:
        Domain model Transaction
    """
    return Transaction(
        transaction_id=db_txn.transaction_id,
        booth_id=db_txn.booth_id,
        toll_id=db_txn.toll_id,
        vehicle_reg=db_txn.vehicle_reg,
        vehicle_type=db_to_vehicle_type(db_txn.vehicle_type),
        transaction_type=db_txn.transaction_type,
        pass_id=db_txn.pass_id,
        amount=db_txn.amount,
        timestamp=db_txn.timestamp
    )


# ============================================================================
# TollBooth Converters
# ============================================================================

def toll_booth_to_db(booth: TollBooth) -> TollBoothDB:
    """
    Convert domain TollBooth to database TollBoothDB

    Args:
        booth: Domain model TollBooth

    Returns:
        Database model TollBoothDB
    """
    return TollBoothDB(
        booth_id=booth.booth_id,
        toll_id=booth.toll_id,
        name=booth.name,
        vehicles_processed=booth.vehicles_processed,
        total_charges_collected=booth.total_charges_collected
    )


def db_to_toll_booth(db_booth: TollBoothDB) -> TollBooth:
    """
    Convert database TollBoothDB to domain TollBooth

    Args:
        db_booth: Database model TollBoothDB

    Returns:
        Domain model TollBooth
    """
    return TollBooth(
        booth_id=db_booth.booth_id,
        toll_id=db_booth.toll_id,
        name=db_booth.name,
        vehicles_processed=db_booth.vehicles_processed,
        total_charges_collected=db_booth.total_charges_collected
    )


# ============================================================================
# Toll Converters (Complex - Has Booths Dictionary)
# ============================================================================

def toll_to_db(toll: Toll) -> TollDB:
    """
    Convert domain Toll to database TollDB

    Note: Booths are stored separately in toll_booths table,
    so we don't include them here.

    Args:
        toll: Domain model Toll

    Returns:
        Database model TollDB
    """
    return TollDB(
        toll_id=toll.toll_id,
        name=toll.name,
        location=toll.location
    )


def db_to_toll(db_toll: TollDB, booths_dict: dict = None) -> Toll:
    """
    Convert database TollDB to domain Toll

    Args:
        db_toll: Database model TollDB
        booths_dict: Optional dictionary of booths (from separate query)

    Returns:
        Domain model Toll
    """
    return Toll(
        toll_id=db_toll.toll_id,
        name=db_toll.name,
        location=db_toll.location,
        booths=booths_dict or {}
    )
