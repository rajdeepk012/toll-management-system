"""
Pass Pricing Service - Handles all pricing-related business logic.

This service encapsulates the rules for:
- Pass prices (based on vehicle type and pass type)
- Pass durations (how long each pass type is valid)
- Pass usage limits (how many times each pass type can be used)
"""

from datetime import timedelta
from typing import Dict
from models import VehicleType, PassType


class PassPricingService:
    """
    Service for managing pass pricing rules and calculations.

    This is a STATELESS service - it only contains pricing rules, no data storage.
    """

    # ============================================================================
    # PRICING CONFIGURATION (Business Rules)
    # ============================================================================

    PASS_PRICES: Dict[VehicleType, Dict[PassType, int]] = {
        VehicleType.TWO_WHEELER: {
            PassType.SINGLE: 50,
            PassType.RETURN: 80,
            PassType.SEVEN_DAY: 250,
        },
        VehicleType.FOUR_WHEELER: {
            PassType.SINGLE: 100,
            PassType.RETURN: 150,
            PassType.SEVEN_DAY: 500,
        }
    }

    PASS_DURATIONS: Dict[PassType, timedelta] = {
        PassType.SINGLE: timedelta(hours=1),
        PassType.RETURN: timedelta(hours=24),
        PassType.SEVEN_DAY: timedelta(days=7),
    }

    PASS_USES: Dict[PassType, int] = {
        PassType.SINGLE: 1,
        PassType.RETURN: 2,
        PassType.SEVEN_DAY: 999999,  # Effectively unlimited for 7 days
    }

    # ============================================================================
    # PUBLIC METHODS (Business Logic)
    # ============================================================================

    def get_pass_price(self, vehicle_type: VehicleType, pass_type: PassType) -> int:
        """
        Get the price for a specific vehicle type and pass type.

        Args:
            vehicle_type: Type of vehicle (TWO_WHEELER or FOUR_WHEELER)
            pass_type: Type of pass (SINGLE, RETURN, or SEVEN_DAY)

        Returns:
            Price in rupees

        Raises:
            ValueError: If vehicle_type or pass_type is invalid

        Example:
            >>> service = PassPricingService()
            >>> service.get_pass_price(VehicleType.TWO_WHEELER, PassType.RETURN)
            80
        """
        if vehicle_type not in self.PASS_PRICES:
            raise ValueError(f"Invalid vehicle type: {vehicle_type}")

        if pass_type not in self.PASS_PRICES[vehicle_type]:
            raise ValueError(f"Invalid pass type: {pass_type}")

        return self.PASS_PRICES[vehicle_type][pass_type]

    def get_pass_duration(self, pass_type: PassType) -> timedelta:
        """
        Get the validity duration for a pass type.

        Args:
            pass_type: Type of pass (SINGLE, RETURN, or SEVEN_DAY)

        Returns:
            Duration as timedelta

        Raises:
            ValueError: If pass_type is invalid

        Example:
            >>> service = PassPricingService()
            >>> service.get_pass_duration(PassType.RETURN)
            timedelta(hours=24)
        """
        if pass_type not in self.PASS_DURATIONS:
            raise ValueError(f"Invalid pass type: {pass_type}")

        return self.PASS_DURATIONS[pass_type]

    def get_pass_uses(self, pass_type: PassType) -> int:
        """
        Get the number of uses allowed for a pass type.

        Args:
            pass_type: Type of pass (SINGLE, RETURN, or SEVEN_DAY)

        Returns:
            Number of allowed uses

        Raises:
            ValueError: If pass_type is invalid

        Example:
            >>> service = PassPricingService()
            >>> service.get_pass_uses(PassType.RETURN)
            2
        """
        if pass_type not in self.PASS_USES:
            raise ValueError(f"Invalid pass type: {pass_type}")

        return self.PASS_USES[pass_type]

    def format_duration(self, duration: timedelta) -> str:
        """
        Convert timedelta to human-readable string.

        Args:
            duration: Duration as timedelta

        Returns:
            Human-readable string (e.g., "24 hours", "7 days")

        Example:
            >>> service = PassPricingService()
            >>> service.format_duration(timedelta(hours=24))
            "24 hours"
        """
        if duration.days == 7:
            return "7 days"
        elif duration.days == 1:
            return "24 hours"
        elif duration.seconds == 3600:  # 1 hour
            return "1 hour"
        else:
            return f"{duration.total_seconds() / 3600:.0f} hours"

    def get_all_prices(self) -> Dict[VehicleType, Dict[PassType, int]]:
        """
        Get all pricing information.

        Returns:
            Complete pricing dictionary

        Example:
            >>> service = PassPricingService()
            >>> prices = service.get_all_prices()
            >>> prices[VehicleType.TWO_WHEELER][PassType.SINGLE]
            50
        """
        return self.PASS_PRICES.copy()
