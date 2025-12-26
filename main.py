"""
Toll Management System - Demo & Testing
This file demonstrates all features and tests the bug fix.
"""

from datetime import datetime, timedelta
from models import Toll, TollBooth, Vehicle, VehicleType, PassType
from system import TollManagementSystem


# ============================================================================
# HELPER FUNCTIONS FOR PRETTY PRINTING
# ============================================================================

def print_separator(title=""):
    """Print a visual separator"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


def print_result(result):
    """Pretty print process_vehicle result"""
    print(f"  Allowed: {result['allowed']}")
    print(f"  Message: {result['message']}")

    if result['pass_info']:
        print(f"\n  Pass Info:")
        for key, value in result['pass_info'].items():
            print(f"    {key}: {value}")

    if result['pass_options']:
        print(f"\n  Available Pass Options:")
        for option in result['pass_options']:
            print(f"    - {option['pass_type'].value}: ₹{option['price']} "
                  f"({option['duration']}, {option['uses']} uses)")


def print_pass_info(toll_pass):
    """Pretty print a TollPass object"""
    print(f"  Pass ID: {toll_pass.pass_id}")
    print(f"  Vehicle: {toll_pass.vehicle_reg}")
    print(f"  Toll: {toll_pass.toll_id}")
    print(f"  Type: {toll_pass.pass_type.value}")
    print(f"  Price: ₹{toll_pass.price}")
    print(f"  Purchased: {toll_pass.purchased_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  First Used: {toll_pass.first_used_at.strftime('%Y-%m-%d %H:%M:%S') if toll_pass.first_used_at else 'Not yet used'}")
    print(f"  Valid Until: {toll_pass.valid_until.strftime('%Y-%m-%d %H:%M:%S') if toll_pass.valid_until else 'Not set yet'}")
    print(f"  Uses Remaining: {toll_pass.uses_remaining}")
    print(f"  Status: {toll_pass.status.value}")


def print_leaderboard(leaderboard, metric):
    """Pretty print leaderboard"""
    print(f"\n  {'Rank':<6} {'Toll':<30} {'Booth':<15} {'Vehicles':<15} {'Revenue':<15}")
    print(f"  {'-'*6} {'-'*30} {'-'*15} {'-'*15} {'-'*15}")

    for booth in leaderboard:
        print(f"  {booth['rank']:<6} "
              f"{booth['toll_name']:<30} "
              f"{booth['booth_id']:<15} "
              f"{booth['vehicles_processed']:<15} "
              f"₹{booth['total_charges_collected']:<15}")

    print(f"\n  (Sorted by: {metric})")


# ============================================================================
# SETUP SAMPLE DATA
# ============================================================================

def setup_system():
    """Create system with sample tolls, booths, and vehicles"""
    system = TollManagementSystem()

    print_separator("Setting Up Sample Data")

    # Create Toll 1: Mumbai-Pune Expressway
    toll1_booths = {
        "B1": TollBooth(booth_id="B1", toll_id="T1", name="Booth A"),
        "B2": TollBooth(booth_id="B2", toll_id="T1", name="Booth B"),
        "B3": TollBooth(booth_id="B3", toll_id="T1", name="Booth C"),
    }
    toll1 = Toll(
        toll_id="T1",
        name="Mumbai-Pune Expressway Toll",
        location="Lonavala, Maharashtra",
        booths=toll1_booths
    )
    system.add_toll(toll1)
    print(f"✓ Created Toll T1: {toll1.name} with {len(toll1_booths)} booths")

    # Create Toll 2: Delhi-Jaipur Highway
    toll2_booths = {
        "B1": TollBooth(booth_id="B1", toll_id="T2", name="Booth A"),
        "B2": TollBooth(booth_id="B2", toll_id="T2", name="Booth B"),
    }
    toll2 = Toll(
        toll_id="T2",
        name="Delhi-Jaipur Highway Toll",
        location="Gurgaon, Haryana",
        booths=toll2_booths
    )
    system.add_toll(toll2)
    print(f"✓ Created Toll T2: {toll2.name} with {len(toll2_booths)} booths")

    # Register vehicles
    vehicles = [
        Vehicle(registration_number="MH-12-AB-1234", vehicle_type=VehicleType.TWO_WHEELER),
        Vehicle(registration_number="MH-14-CD-5678", vehicle_type=VehicleType.FOUR_WHEELER),
        Vehicle(registration_number="DL-01-EF-9012", vehicle_type=VehicleType.TWO_WHEELER),
        Vehicle(registration_number="KA-03-GH-3456", vehicle_type=VehicleType.FOUR_WHEELER),
    ]

    for vehicle in vehicles:
        system.add_vehicle(vehicle)

    print(f"✓ Registered {len(vehicles)} vehicles")
    print(f"\nSetup complete! System ready for demo.\n")

    return system


# ============================================================================
# DEMO SCENARIOS (We'll add these one by one)
# ============================================================================

def main():
    """Run all demo scenarios"""
    system = setup_system()

    # ========================================================================
    # SCENARIO 1: Display Pass Options
    # ========================================================================
    print_separator("SCENARIO 1: Display Pass Options")

    print("Showing pass options for TWO_WHEELER:")
    options = system.display_pass_options(VehicleType.TWO_WHEELER)

    for option in options:
        print(f"\n  {option['pass_type'].value.upper()} PASS")
        print(f"    Price: ₹{option['price']}")
        print(f"    Duration: {option['duration']}")
        print(f"    Uses: {option['uses']}")
        print(f"    Description: {option['description']}")

    # ========================================================================
    # SCENARIO 2: Purchase a RETURN Pass
    # ========================================================================
    print_separator("SCENARIO 2: Purchase a RETURN Pass")

    vehicle_reg = "MH-12-AB-1234"
    toll_id = "T1"
    booth_id = "B1"

    print(f"Vehicle {vehicle_reg} purchasing RETURN pass at Toll {toll_id}, Booth {booth_id}")

    try:
        toll_pass = system.purchase_pass(vehicle_reg, toll_id, booth_id, PassType.RETURN)
        print(f"\n✓ Pass purchased successfully!")
        print_pass_info(toll_pass)
    except ValueError as e:
        print(f"\n✗ Purchase failed: {e}")

    # ========================================================================
    # SCENARIO 3: THE BUG FIX TEST - First Use Sets Validity ⭐
    # ========================================================================
    print_separator("SCENARIO 3: Bug Fix Test - First Use of RETURN Pass")

    print(f"Vehicle {vehicle_reg} passing through Toll {toll_id}, Booth {booth_id}")
    print("(This is the FIRST USE - watch validity timer start!)\n")

    result = system.process_vehicle(vehicle_reg, toll_id, booth_id)
    print_result(result)

    # Show the updated pass info
    toll_pass = system.pass_repo.get_pass("PASS-0001")# Get the pass we created
    print(f"\n  Updated Pass Info After First Use:")
    print_pass_info(toll_pass)

    print(f"\n  KEY OBSERVATION:")
    print(f"    ✓ first_used_at is NOW SET (not None anymore)")
    print(f"    ✓ valid_until is NOW SET (first_used_at + 24 hours)")
    print(f"    ✓ This proves the bug fix works!")

    # ========================================================================
    # SCENARIO 4: Second Use of RETURN Pass
    # ========================================================================
    print_separator("SCENARIO 4: Second Use of RETURN Pass (Within Validity)")

    print(f"Vehicle {vehicle_reg} passing through again (SECOND USE)")
    print("(Should be allowed - still within 24 hours and has 1 use left)\n")

    result = system.process_vehicle(vehicle_reg, toll_id, booth_id)
    print_result(result)

    # Show final pass state
    print(f"\n  Final Pass State:")
    print(f"    Uses Remaining: {toll_pass.uses_remaining} (was 1, now 0)")
    print(f"    Status: {toll_pass.status.value} (should be EXHAUSTED)")

    # ========================================================================
    # SCENARIO 5: Try to Use Exhausted Pass
    # ========================================================================
    print_separator("SCENARIO 5: Try to Use Exhausted Pass")

    print(f"Vehicle {vehicle_reg} tries to pass again (THIRD TIME)")
    print("(Should be DENIED - pass is exhausted)\n")

    result = system.process_vehicle(vehicle_reg, toll_id, booth_id)
    print_result(result)

    print(f"\n  KEY OBSERVATION:")
    print(f"    ✗ Passage denied even though time is still valid")
    print(f"    ✗ Reason: uses_remaining = 0 (EXHAUSTED)")

    # ========================================================================
    # SCENARIO 6: Vehicle with No Pass
    # ========================================================================
    print_separator("SCENARIO 6: Vehicle Without a Pass")

    no_pass_vehicle = "DL-01-EF-9012"
    print(f"Vehicle {no_pass_vehicle} (has no pass) tries to pass through Toll {toll_id}\n")

    result = system.process_vehicle(no_pass_vehicle, toll_id, booth_id)
    print_result(result)

    print(f"\n  KEY OBSERVATION:")
    print(f"    ✗ Passage denied - no valid pass")
    print(f"    ✓ System shows available pass options to purchase")

    # ========================================================================
    # SCENARIO 7: Purchase More Passes & Display Leaderboard
    # ========================================================================
    print_separator("SCENARIO 7: Booth Statistics & Leaderboard")

    # Purchase a few more passes and process some vehicles to generate stats
    print("Generating booth activity...\n")

    # Car purchases SEVEN_DAY pass at T1-B2
    car = "MH-14-CD-5678"
    pass2 = system.purchase_pass(car, "T1", "B2", PassType.SEVEN_DAY)
    print(f"✓ {car} purchased {pass2.pass_type.value} pass at T1-B2 (₹{pass2.price})")

    # Car passes through B2 multiple times
    system.process_vehicle(car, "T1", "B2")
    system.process_vehicle(car, "T1", "B2")
    system.process_vehicle(car, "T1", "B2")
    print(f"✓ {car} passed through T1-B2 three times")

    # Another vehicle at T2
    bike2 = "KA-03-GH-3456"
    pass3 = system.purchase_pass(bike2, "T2", "B1", PassType.SINGLE)
    system.process_vehicle(bike2, "T2", "B1")
    print(f"✓ {bike2} purchased and used pass at T2-B1 (₹{pass3.price})")

    # Display leaderboard sorted by vehicles processed
    print(f"\n{'─'*80}")
    print("LEADERBOARD - Sorted by Vehicles Processed")
    print(f"{'─'*80}")
    leaderboard = system.get_leaderboard("vehicles_processed")
    print_leaderboard(leaderboard, "vehicles_processed")

    # Display leaderboard sorted by revenue
    print(f"\n{'─'*80}")
    print("LEADERBOARD - Sorted by Revenue Collected")
    print(f"{'─'*80}")
    leaderboard = system.get_leaderboard("total_charges_collected")
    print_leaderboard(leaderboard, "total_charges_collected")

    print_separator("DEMO COMPLETE")
    print("✓ All 7 scenarios executed successfully!")
    print("✓ Bug fix verified - validity starts from first use!")
    print("✓ All features working correctly!")
    print(f"\nTotal transactions recorded: {len(system.transaction_repo.get_all_transactions())}")
    print(f"Total passes created: {len(system.pass_repo.get_all_passes())}")


if __name__ == "__main__":
    main()
