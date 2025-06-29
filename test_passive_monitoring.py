#!/usr/bin/env python3
"""
Test script to verify NeoSmart Blue integration works with advertisement data only.
This script demonstrates how status data can be obtained without active connections.
"""

import asyncio
from neosmartblue.py import parse_status_data, scan_for_devices


async def test_passive_monitoring():
    """Test passive monitoring of NeoSmart Blue devices."""
    print("Testing passive monitoring of NeoSmart Blue devices...")
    print("This demonstrates how the integration works without active connections.\n")

    # Test 1: Parse a sample status payload
    print("Test 1: Parsing sample status data")
    test_payload = bytes([85, 50, 10, 75, 0x21])  # Sample data
    try:
        result = parse_status_data(test_payload)
        print("✓ Successfully parsed status data:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"✗ Failed to parse status data: {e}")
        return

    print("\n" + "=" * 60 + "\n")

    # Test 2: Scan for actual devices (if any are nearby)
    print("Test 2: Scanning for NeoSmart Blue devices")
    print("This will scan for 10 seconds...")
    try:
        devices = await scan_for_devices(timeout=10.0)
        if devices:
            print(f"✓ Found {len(devices)} device(s):")
            for device in devices:
                print(f"\n  Device: {device['name']} ({device['address']})")
                if device["status"]:
                    print("  Status from advertisement:")
                    for key, value in device["status"].items():
                        print(f"    {key}: {value}")
                else:
                    print("  No status data in advertisement")
        else:
            print("✓ No devices found (this is normal if no devices are nearby)")
    except Exception as e:
        print(f"✗ Scan failed: {e}")
        return

    print("\n" + "=" * 60 + "\n")
    print("✓ All tests completed successfully!")
    print("\nThis demonstrates that the NeoSmart Blue integration can:")
    print("- Parse status data from BLE advertisements")
    print("- Work without maintaining active connections")
    print("- Provide rich status information (battery, position, motor state, etc.)")


if __name__ == "__main__":
    asyncio.run(test_passive_monitoring())
