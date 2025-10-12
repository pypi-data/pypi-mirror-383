"""Test script for AI-first workflow."""
import json

def calculate_sum(numbers):
    return sum(numbers)

def format_result(result):
    # This calls json.dumps which won't be traced (gap!)
    return json.dumps({"result": result})

def main():
    numbers = [1, 2, 3, 4, 5]
    total = calculate_sum(numbers)
    output = format_result(total)
    print(output)

if __name__ == "__main__":
    main()
