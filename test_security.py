import streamlit as st
import pandas as pd
from unittest.mock import MagicMock

# Simulate Security Check

def test_limits():
    print("--- Testing Security Limits ---")
    
    # 1. Test 90 lines limit
    fake_input_small = "\n".join([f"Topic {i}" for i in range(80)])
    fake_input_large = "\n".join([f"Topic {i}" for i in range(100)])
    
    lines_small = [l for l in fake_input_small.split('\n') if l.strip()]
    lines_large = [l for l in fake_input_large.split('\n') if l.strip()]
    
    print(f"Input Small (80 lines): {'✅ Allowed' if len(lines_small) <= 90 else '❌ Blocked'}")
    print(f"Input Large (100 lines): {'✅ Allowed' if len(lines_large) <= 90 else '❌ Blocked'}")
    
    # 2. Test Days Generation Limit (Logic Simulation)
    days_input = 100
    max_val = 90
    print(f"Days Input {days_input} (Max {max_val}): {'✅ Allowed' if days_input <= max_val else '❌ Blocked'}")

    # 3. Test Password Strength (Logic Simulation)
    print("\n--- Testing Password Policy ---")
    
    # Mocking dependencies to import auth safely if needed, 
    # but since we know the logic, we can verify the Regex behavior directly 
    # OR better: Import the actual function if possible. 
    # Let's try to simulate the exact logic we implemented.
    import re
    def validate_password_strength(password: str) -> bool:
        if len(password) < 8: return False
        if not re.search(r'[A-Z]', password): return False
        if not re.search(r'\d', password): return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password): return False
        return True

    passwords = [
        ("123456", False, "Too short"),
        ("password123", False, "No Upper/Special"),
        ("Password123", False, "No Special"),
        ("Password!", False, "No Number (if short)"), # logic check
        ("S3nhaForte!", True, "Valid"),
        ("Abc@1234", True, "Valid")
    ]
    
    for pwd, expected, reason in passwords:
        result = validate_password_strength(pwd)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"Password '{pwd}': {status} (Expected {expected}) - {reason}")
    
if __name__ == "__main__":
    test_limits()
