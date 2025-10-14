"""
Smoke Test Suite Example
Critical functionality tests that must pass
"""
import pytest
import time
from pytest_bdd import scenarios, given, when, then
from pytest_bdd_reporter.suite_manager import (
    suite, suite_setup, suite_teardown, 
    test_setup, test_teardown, suite_manager
)

# Load scenarios from feature file
scenarios('features/smoke_tests.feature')

# Define the smoke test suite
@suite(
    name="smoke_tests",
    description="Critical functionality tests that must pass",
    tests=[
        "test_user_login",
        "test_basic_navigation", 
        "test_core_functionality"
    ],
    features=["features/smoke_tests.feature"],
    tags=["smoke", "critical", "fast"]
)
def smoke_suite_config():
    """Smoke test suite configuration"""
    pass

# Suite-level setup
@suite_setup("smoke_tests")
def setup_smoke_environment():
    """Setup environment for smoke tests"""
    print("🔧 Setting up smoke test environment")
    print("   • Initializing test database")
    print("   • Starting mock services")
    print("   • Configuring test users")
    time.sleep(0.1)  # Simulate setup time

# Suite-level teardown
@suite_teardown("smoke_tests")
def teardown_smoke_environment():
    """Cleanup after smoke tests"""
    print("🧹 Cleaning up smoke test environment")
    print("   • Stopping mock services")
    print("   • Clearing test data")
    print("   • Resetting configurations")
    time.sleep(0.1)  # Simulate cleanup time

# Test-level setup (runs before each test)
@test_setup("smoke_tests")
def setup_each_smoke_test():
    """Setup before each smoke test"""
    print("   🔧 Preparing individual test")
    print("      • Clearing browser cache")
    print("      • Resetting user session")

# Test-level teardown (runs after each test)
@test_teardown("smoke_tests")
def teardown_each_smoke_test():
    """Cleanup after each smoke test"""
    print("   🧹 Cleaning up individual test")
    print("      • Capturing screenshots")
    print("      • Logging test metrics")

# Test context for sharing data between steps
test_context = {
    'user': None,
    'session': None,
    'result': None
}

# BDD Steps
@given("I have a test user account")
def test_user_account():
    """Setup test user account"""
    test_context['user'] = {
        'username': 'test_user',
        'password': 'test_pass',
        'email': 'test@example.com'
    }
    print(f"👤 Test user created: {test_context['user']['username']}")

@given("the application is running")
def application_running():
    """Ensure application is running"""
    print("🚀 Application is running and accessible")
    test_context['app_status'] = 'running'

@when("I attempt to login")
def attempt_login():
    """Attempt user login"""
    user = test_context['user']
    print(f"🔐 Attempting login for: {user['username']}")
    
    # Simulate login process
    time.sleep(0.05)
    test_context['session'] = {
        'logged_in': True,
        'user_id': 'user_123',
        'session_token': 'token_abc123'
    }
    print("✅ Login successful")

@when("I navigate to the dashboard")
def navigate_dashboard():
    """Navigate to main dashboard"""
    print("🧭 Navigating to dashboard")
    time.sleep(0.05)
    test_context['current_page'] = 'dashboard'
    print("✅ Dashboard loaded successfully")

@when("I access core features")
def access_core_features():
    """Access core application features"""
    print("⚙️ Accessing core features")
    features = ['reports', 'settings', 'profile', 'help']
    
    for feature in features:
        print(f"   • Testing {feature}")
        time.sleep(0.02)
    
    test_context['features_tested'] = features
    print("✅ All core features accessible")

@then("I should be logged in successfully")
def verify_login():
    """Verify successful login"""
    session = test_context.get('session')
    assert session is not None, "No session found"
    assert session.get('logged_in'), "User not logged in"
    assert session.get('session_token'), "No session token"
    
    print("✅ Login verification passed")
    print(f"   • User ID: {session.get('user_id')}")
    print(f"   • Session: {session.get('session_token')[:10]}...")

@then("I should see the main dashboard")
def verify_dashboard():
    """Verify dashboard is displayed"""
    current_page = test_context.get('current_page')
    assert current_page == 'dashboard', f"Expected dashboard, got {current_page}"
    
    print("✅ Dashboard verification passed")
    print("   • Main navigation visible")
    print("   • User profile displayed")
    print("   • Quick actions available")

@then("all core functionality should be available")
def verify_core_functionality():
    """Verify core functionality is working"""
    features = test_context.get('features_tested', [])
    expected_features = ['reports', 'settings', 'profile', 'help']
    
    for feature in expected_features:
        assert feature in features, f"Feature {feature} not tested"
    
    print("✅ Core functionality verification passed")
    print(f"   • {len(features)} features tested")
    print("   • All critical paths working")

# Additional test functions (these would be called by the BDD scenarios)
def test_user_login():
    """Test user login functionality"""
    # This test is driven by BDD scenarios
    pass

def test_basic_navigation():
    """Test basic navigation functionality"""
    # This test is driven by BDD scenarios
    pass

def test_core_functionality():
    """Test core functionality"""
    # This test is driven by BDD scenarios
    pass