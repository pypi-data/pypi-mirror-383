"""
Manual test for gap detection functionality.

This script:
1. Traces only __main__ functions (default include pattern)
2. Calls json.dumps and other stdlib functions (not traced - creates gaps)
3. Properly shuts down to flush data
4. Then query with: breadcrumb query --gaps
"""

import breadcrumb
import json
import os

# Initialize with default config (only traces __main__)
breadcrumb.init()

def format_receipt(items, total):
    """Format a receipt - calls json.dumps (untraced, creates gap)."""
    receipt_data = {
        'items': items,
        'total': total
    }
    # This json.dumps call won't be traced (creates gap)
    receipt_json = json.dumps(receipt_data, indent=2)
    return receipt_json

def calculate_total(items):
    """Calculate total price."""
    total = sum(item['price'] * item['quantity'] for item in items)
    return total

def main():
    print("🍞 Testing Gap Detection\n")

    # Create some test data
    items = [
        {'name': 'Coffee', 'price': 3.50, 'quantity': 2},
        {'name': 'Sandwich', 'price': 8.00, 'quantity': 1},
    ]

    print("1. Calculating total...")
    total = calculate_total(items)
    print(f"   Total: ${total:.2f}\n")

    print("2. Formatting receipt (calls json.dumps - untraced)...")
    receipt = format_receipt(items, total)
    print(f"   Receipt generated ({len(receipt)} chars)\n")

    print("3. Getting current directory (calls os.getcwd - untraced)...")
    current_dir = os.getcwd()
    print(f"   Directory: {current_dir}\n")

    print("✅ Execution complete!")
    print("\n💡 Now run: breadcrumb query --gaps")
    print("   You should see gaps for json.dumps and other stdlib calls\n")

if __name__ == "__main__":
    try:
        main()
    finally:
        # Properly shutdown to flush trace data
        print("🔄 Shutting down breadcrumb...")
        breadcrumb.shutdown()
        print("✅ Shutdown complete\n")
