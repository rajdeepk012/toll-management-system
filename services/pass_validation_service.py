"""
Pass Validation Service - Handles pass validation logic.

This service encapsulates the rules for:
- Checking if a pass is valid (time + usage limits)
- Determining pass status (active/expired/exhausted)
- Validation result with detailed reasons
"""

from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass
from models import TollPass, PassStatus


@dataclass
class PassValidationResult:
    """
    Result of pass validation with detailed information.

    This is a Data Transfer Object (DTO) that encapsulates validation results.
    """
    is_valid: bool
    reason: Optional[str] = None
    is_time_valid: bool = False
    has_uses_remaining: bool = False
    is_first_use: bool = False


class PassValidationService:
    """
    Service for validating toll passes.

    This is a STATELESS service - it only performs validation logic,
    no data storage or modification.
    """

    def validate_pass(self, toll_pass: TollPass) -> PassValidationResult:
        """
        Validate if a pass can be used for passage.

        This method checks:
        1. If pass is being used for the first time (first_used_at is None)
        2. If pass is still within validity period (time check)
        3. If pass has uses remaining (usage check)

        Args:
            toll_pass: The TollPass to validate

        Returns:
            PassValidationResult with validation details

        Example:
            >>> service = PassValidationService()
            >>> result = service.validate_pass(my_pass)
            >>> if result.is_valid:
            >>>     print("Pass is valid!")
            >>> else:
            >>>     print(f"Pass invalid: {result.reason}")
        """
        current_time = datetime.now()

        # ============ CHECK 1: Is this the first use? ============
        is_first_use = toll_pass.first_used_at is None

        # If it's the first use, we can't validate time yet
        # (validity timer starts on first use - this is the BUG FIX!)
        if is_first_use:
            # First use is always valid (time-wise)
            # We still need to check if pass has uses remaining
            has_uses_remaining = toll_pass.uses_remaining > 0

            if not has_uses_remaining:
                # This shouldn't happen (new pass with 0 uses), but handle it
                return PassValidationResult(
                    is_valid=False,
                    reason="exhausted",
                    is_time_valid=True,  # N/A for first use
                    has_uses_remaining=False,
                    is_first_use=True
                )

            # First use is valid!
            return PassValidationResult(
                is_valid=True,
                reason=None,
                is_time_valid=True,  # N/A for first use
                has_uses_remaining=True,
                is_first_use=True
            )

        # ============ CHECK 2: Time validity ============
        is_time_valid = current_time < toll_pass.valid_until

        # ============ CHECK 3: Uses remaining ============
        has_uses_remaining = toll_pass.uses_remaining > 0

        # ============ DETERMINE VALIDITY ============
        if not is_time_valid:
            return PassValidationResult(
                is_valid=False,
                reason="expired",
                is_time_valid=False,
                has_uses_remaining=has_uses_remaining,
                is_first_use=False
            )

        if not has_uses_remaining:
            return PassValidationResult(
                is_valid=False,
                reason="exhausted",
                is_time_valid=True,
                has_uses_remaining=False,
                is_first_use=False
            )

        # Pass is valid!
        return PassValidationResult(
            is_valid=True,
            reason=None,
            is_time_valid=True,
            has_uses_remaining=True,
            is_first_use=False
        )

    def determine_pass_status(
        self,
        is_time_valid: bool,
        has_uses_remaining: bool
    ) -> PassStatus:
        """
        Determine the status of a pass based on validation checks.

        Args:
            is_time_valid: Whether the pass is within validity period
            has_uses_remaining: Whether the pass has uses left

        Returns:
            PassStatus (ACTIVE, EXPIRED, or EXHAUSTED)

        Example:
            >>> service = PassValidationService()
            >>> status = service.determine_pass_status(
            ...     is_time_valid=True,
            ...     has_uses_remaining=False
            ... )
            >>> print(status)  # PassStatus.EXHAUSTED
        """
        if not has_uses_remaining:
            return PassStatus.EXHAUSTED
        elif not is_time_valid:
            return PassStatus.EXPIRED
        else:
            return PassStatus.ACTIVE
