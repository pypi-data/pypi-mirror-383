"""
Simple Suite Demo - Working Example
Shows basic suite functionality without complex BDD scenarios
"""
import pytest
import time
from pytest_bdd_reporter.suite_manager import (
    suite, suite_setup, suite_teardown, 
    test_setup, test_teardown
)

# Define a simple test suite
@suite(
    name="demo_suite",
    description="Simple demonstration suite",
    tests=["test_addition", "test_subtraction", "test_multiplication"],
    tags=["demo", "math", "simple"]
)
def demo_suite_config():
    """Demo suite configuration"""
    pass

# Suite-level setup
@suite_setup("demo_suite")
def setup_demo_suite():
    """Setup for demo suite"""
    print("🔧 Setting up demo suite")
    print("   • Initializing calculator")
    print("   • Loading test data")
    time.sleep(0.1)

# Suite-level teardown
@suite_teardown("demo_suite")
def teardown_demo_suite():
    """Teardown for demo suite"""
    print("🧹 Cleaning up demo suite")
    print("   • Saving results")
    print("   • Clearing memory")
    time.sleep(0.1)

# Test-level setup
@test_setup("demo_suite")
def setup_each_test():
    """Setup before each test"""
    print("   🔧 Preparing test")

# Test-level teardown
@test_teardown("demo_suite")
def teardown_each_test():
    """Cleanup after each test"""
    print("   🧹 Cleaning up test")

# Simple test functions
def test_addition():
    """Test addition operation"""
    print("➕ Testing addition: 2 + 3")
    result = 2 + 3
    assert result == 5
    print(f"   Result: {result} ✅")

def test_subtraction():
    """Test subtraction operation"""
    print("➖ Testing subtraction: 10 - 4")
    result = 10 - 4
    assert result == 6
    print(f"   Result: {result} ✅")

def test_multiplication():
    """Test multiplication operation"""
    print("✖️ Testing multiplication: 3 * 4")
    result = 3 * 4
    assert result == 12
    print(f"   Result: {result} ✅")

# Additional suite for comparison
@suite(
    name="advanced_suite",
    description="Advanced mathematical operations",
    tests=["test_division", "test_power", "test_square_root"],
    tags=["advanced", "math", "complex"]
)
def advanced_suite_config():
    """Advanced suite configuration"""
    pass

@suite_setup("advanced_suite")
def setup_advanced_suite():
    """Setup for advanced suite"""
    print("🔧 Setting up advanced suite")
    print("   • Loading advanced math library")
    print("   • Configuring precision settings")
    time.sleep(0.1)

@suite_teardown("advanced_suite")
def teardown_advanced_suite():
    """Teardown for advanced suite"""
    print("🧹 Cleaning up advanced suite")
    print("   • Unloading libraries")
    print("   • Resetting configurations")
    time.sleep(0.1)

def test_division():
    """Test division operation"""
    print("➗ Testing division: 15 / 3")
    result = 15 / 3
    assert result == 5.0
    print(f"   Result: {result} ✅")

def test_power():
    """Test power operation"""
    print("🔢 Testing power: 2 ** 3")
    result = 2 ** 3
    assert result == 8
    print(f"   Result: {result} ✅")

def test_square_root():
    """Test square root operation"""
    print("√ Testing square root: √16")
    import math
    result = math.sqrt(16)
    assert result == 4.0
    print(f"   Result: {result} ✅")