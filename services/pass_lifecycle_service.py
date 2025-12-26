"""
Pass Lifecycle Service - Manages pass state transitions.

This service encapsulates the logic for:
- Setting first use time (BUG FIX: validity starts from first use)
- Using a pass (decrementing uses, updating status)
- Managing pass lifecycle transitions
"""

from datetime import datetime, timedelta
from models import TollPass, PassStatus, PassType


class PassLifecycleService:
    """
    Service for managing toll pass lifecycle and state transitions.

    This service MODIFIES pass state - it's responsible for:
    - Initializing pass on first use (the critical bug fix!)
    - Decrementing uses
    - Updating pass status
    """

    def __init__(self, pricing_service):
        """
        Initialize with dependency on pricing service.

        Args:
            pricing_service: PassPricingService instance for getting durations
        """
        self.pricing_service = pricing_service

    def set_first_use(self, toll_pass: TollPass, current_time: datetime) -> None:
        """
        Set the first use time and validity period for a pass.

        THIS IS THE BUG FIX!
        Validity timer starts from FIRST USE, not from PURCHASE.

        Args:
            toll_pass: The pass to initialize
            current_time: The time of first use

        Side Effects:
            Modifies toll_pass.first_used_at and toll_pass.valid_until

        Example:
            >>> service = PassLifecycleService(pricing_service)
            >>> service.set_first_use(my_pass, datetime.now())
            >>> print(my_pass.first_used_at)  # Now set!
            >>> print(my_pass.valid_until)    # Now set!
        """
        # Get the duration for this pass type
        duration = self.pricing_service.get_pass_duration(toll_pass.pass_type)

        # BUG FIX: Set validity from FIRST USE, not purchase!
        toll_pass.first_used_at = current_time
        toll_pass.valid_until = current_time + duration

    def use_pass(self, toll_pass: TollPass) -> None:
        """
        Use a pass - decrement uses and update status if exhausted.

        This method should be called AFTER validation confirms the pass is valid.

        Args:
            toll_pass: The pass to use

        Side Effects:
            - Decrements toll_pass.uses_remaining by 1
            - Sets status to EXHAUSTED if uses reach 0

        Example:
            >>> service = PassLifecycleService(pricing_service)
            >>> service.use_pass(my_pass)
            >>> print(my_pass.uses_remaining)  # Decremented by 1
        """
        # Decrement uses
        toll_pass.uses_remaining -= 1

        # Update status if exhausted
        if toll_pass.uses_remaining == 0:
            toll_pass.status = PassStatus.EXHAUSTED

    def update_pass_status(
        self,
        toll_pass: TollPass,
        is_time_valid: bool,
        has_uses_remaining: bool
    ) -> None:
        """
        Update pass status based on validation results.

        Args:
            toll_pass: The pass to update
            is_time_valid: Whether the pass is within validity period
            has_uses_remaining: Whether the pass has uses left

        Side Effects:
            Updates toll_pass.status

        Example:
            >>> service = PassLifecycleService(pricing_service)
            >>> service.update_pass_status(my_pass, False, True)
            >>> print(my_pass.status)  # PassStatus.EXPIRED
        """
        if not has_uses_remaining:
            toll_pass.status = PassStatus.EXHAUSTED
        elif not is_time_valid:
            toll_pass.status = PassStatus.EXPIRED
        else:
            toll_pass.status = PassStatus.ACTIVE
