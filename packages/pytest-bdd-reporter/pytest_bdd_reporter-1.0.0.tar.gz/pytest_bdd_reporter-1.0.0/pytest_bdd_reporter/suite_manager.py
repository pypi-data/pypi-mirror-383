"""
Suite Management for pytest-bdd-reporter
Provides suite-based test organization with setup/teardown support
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import pytest
from pytest_bdd import given, when, then


@dataclass
class SuiteConfig:
    """Configuration for a test suite"""
    name: str
    description: str = ""
    tests: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    setup_hooks: List[Callable] = field(default_factory=list)
    teardown_hooks: List[Callable] = field(default_factory=list)
    test_setup_hooks: List[Callable] = field(default_factory=list)
    test_teardown_hooks: List[Callable] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0


class SuiteManager:
    """Manages test suites and their execution"""
    
    def __init__(self):
        self.suites: Dict[str, SuiteConfig] = {}
        self.current_suite: Optional[str] = None
        self.suite_results: Dict[str, Dict] = {}
        self.active_suites: List[str] = []
        
    def register_suite(self, suite_config: SuiteConfig):
        """Register a new test suite"""
        self.suites[suite_config.name] = suite_config
        print(f"📦 Registered suite: {suite_config.name}")
        
    def create_suite(self, name: str, **kwargs) -> SuiteConfig:
        """Create and register a new suite"""
        suite = SuiteConfig(name=name, **kwargs)
        self.register_suite(suite)
        return suite
        
    def add_suite_setup(self, suite_name: str, setup_func: Callable):
        """Add setup function to suite"""
        if suite_name in self.suites:
            self.suites[suite_name].setup_hooks.append(setup_func)
            
    def add_suite_teardown(self, suite_name: str, teardown_func: Callable):
        """Add teardown function to suite"""
        if suite_name in self.suites:
            self.suites[suite_name].teardown_hooks.append(teardown_func)
            
    def add_test_setup(self, suite_name: str, setup_func: Callable):
        """Add test-level setup function to suite"""
        if suite_name in self.suites:
            self.suites[suite_name].test_setup_hooks.append(setup_func)
            
    def add_test_teardown(self, suite_name: str, teardown_func: Callable):
        """Add test-level teardown function to suite"""
        if suite_name in self.suites:
            self.suites[suite_name].test_teardown_hooks.append(teardown_func)
    
    def get_suite_by_test(self, test_name: str) -> Optional[str]:
        """Find which suite a test belongs to"""
        for suite_name, suite in self.suites.items():
            # Check exact match or prefix match
            if test_name in suite.tests or any(test_name.startswith(t) for t in suite.tests):
                return suite_name
            # Check if test name contains suite name (for BDD scenarios)
            if suite_name in test_name.lower():
                return suite_name
        return None
        
    def should_run_test(self, test_name: str, selected_suites: List[str] = None) -> bool:
        """Check if a test should run based on suite selection"""
        if not selected_suites:
            return True
            
        suite_name = self.get_suite_by_test(test_name)
        return suite_name in selected_suites if suite_name else False
        
    def execute_suite_setup(self, suite_name: str):
        """Execute all setup hooks for a suite"""
        if suite_name not in self.suites:
            return
            
        suite = self.suites[suite_name]
        print(f"🔧 Setting up suite: {suite_name}")
        
        for setup_hook in suite.setup_hooks:
            try:
                setup_hook()
                print(f"   ✅ Setup hook executed: {setup_hook.__name__}")
            except Exception as e:
                print(f"   ❌ Setup hook failed: {setup_hook.__name__} - {e}")
                raise
                
    def execute_suite_teardown(self, suite_name: str):
        """Execute all teardown hooks for a suite"""
        if suite_name not in self.suites:
            return
            
        suite = self.suites[suite_name]
        print(f"🧹 Tearing down suite: {suite_name}")
        
        for teardown_hook in suite.teardown_hooks:
            try:
                teardown_hook()
                print(f"   ✅ Teardown hook executed: {teardown_hook.__name__}")
            except Exception as e:
                print(f"   ⚠️ Teardown hook failed: {teardown_hook.__name__} - {e}")
                # Continue with other teardown hooks even if one fails
                
    def execute_test_setup(self, suite_name: str, test_name: str):
        """Execute test-level setup hooks for a suite"""
        if suite_name not in self.suites:
            return
            
        suite = self.suites[suite_name]
        
        for setup_hook in suite.test_setup_hooks:
            try:
                setup_hook()
            except Exception as e:
                print(f"   ❌ Test setup failed: {setup_hook.__name__} - {e}")
                raise
                
    def execute_test_teardown(self, suite_name: str, test_name: str):
        """Execute test-level teardown hooks for a suite"""
        if suite_name not in self.suites:
            return
            
        suite = self.suites[suite_name]
        
        for teardown_hook in suite.test_teardown_hooks:
            try:
                teardown_hook()
            except Exception as e:
                print(f"   ⚠️ Test teardown failed: {teardown_hook.__name__} - {e}")
                
    def get_suite_info(self, suite_name: str) -> Dict[str, Any]:
        """Get information about a suite"""
        if suite_name not in self.suites:
            return {}
            
        suite = self.suites[suite_name]
        return {
            'name': suite.name,
            'description': suite.description,
            'tests': suite.tests,
            'features': suite.features,
            'tags': suite.tags,
            'enabled': suite.enabled,
            'priority': suite.priority,
            'setup_hooks': len(suite.setup_hooks),
            'teardown_hooks': len(suite.teardown_hooks),
            'test_setup_hooks': len(suite.test_setup_hooks),
            'test_teardown_hooks': len(suite.test_teardown_hooks)
        }
        
    def list_suites(self) -> List[str]:
        """List all registered suites"""
        return list(self.suites.keys())
        
    def save_suite_config(self, config_file: str = "suite_config.json"):
        """Save suite configuration to file"""
        config_data = {}
        for name, suite in self.suites.items():
            config_data[name] = {
                'name': suite.name,
                'description': suite.description,
                'tests': suite.tests,
                'features': suite.features,
                'tags': suite.tags,
                'enabled': suite.enabled,
                'priority': suite.priority
            }
            
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
            
    def load_suite_config(self, config_file: str = "suite_config.json"):
        """Load suite configuration from file"""
        if not Path(config_file).exists():
            return
            
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            
        for name, data in config_data.items():
            suite = SuiteConfig(**data)
            self.register_suite(suite)


# Global suite manager instance
suite_manager = SuiteManager()


# Decorators for easy suite management
def suite(name: str, description: str = "", tests: List[str] = None, 
          features: List[str] = None, tags: List[str] = None, **kwargs):
    """Decorator to define a test suite"""
    def decorator(func):
        suite_config = SuiteConfig(
            name=name,
            description=description,
            tests=tests or [],
            features=features or [],
            tags=tags or [],
            **kwargs
        )
        suite_manager.register_suite(suite_config)
        return func
    return decorator


def suite_setup(suite_name: str):
    """Decorator for suite-level setup functions"""
    def decorator(func):
        suite_manager.add_suite_setup(suite_name, func)
        return func
    return decorator


def suite_teardown(suite_name: str):
    """Decorator for suite-level teardown functions"""
    def decorator(func):
        suite_manager.add_suite_teardown(suite_name, func)
        return func
    return decorator


def test_setup(suite_name: str):
    """Decorator for test-level setup functions"""
    def decorator(func):
        suite_manager.add_test_setup(suite_name, func)
        return func
    return decorator


def test_teardown(suite_name: str):
    """Decorator for test-level teardown functions"""
    def decorator(func):
        suite_manager.add_test_teardown(suite_name, func)
        return func
    return decorator


# BDD step decorators with suite support
def suite_given(suite_name: str, step_text: str):
    """Given step with suite context"""
    def decorator(func):
        @given(step_text)
        def wrapper(*args, **kwargs):
            # Execute test setup if needed
            suite_manager.execute_test_setup(suite_name, func.__name__)
            try:
                return func(*args, **kwargs)
            finally:
                # Note: teardown will be handled by pytest fixtures
                pass
        return wrapper
    return decorator


def suite_when(suite_name: str, step_text: str):
    """When step with suite context"""
    def decorator(func):
        @when(step_text)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def suite_then(suite_name: str, step_text: str):
    """Then step with suite context"""
    def decorator(func):
        @then(step_text)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Execute test teardown
            suite_manager.execute_test_teardown(suite_name, func.__name__)
            return result
        return wrapper
    return decorator


# Pytest hooks for suite management
def pytest_configure(config):
    """Configure suite manager with pytest"""
    # Load suite configuration if exists
    suite_manager.load_suite_config()
    
    # Add suite selection option
    if hasattr(config.option, 'suite') and config.option.suite:
        selected_suites = config.option.suite.split(',')
        suite_manager.active_suites = selected_suites
        print(f"🎯 Running suites: {', '.join(selected_suites)}")


def pytest_collection_modifyitems(config, items):
    """Filter tests based on suite selection"""
    # Get selected suites from config
    selected_suites = []
    if hasattr(config.option, 'suite') and config.option.suite:
        selected_suites = config.option.suite.split(',')
        suite_manager.active_suites = selected_suites
    
    if not selected_suites:
        return
        
    selected_items = []
    for item in items:
        test_name = item.name
        # Check if test belongs to any selected suite
        test_suite = suite_manager.get_suite_by_test(test_name)
        if test_suite and test_suite in selected_suites:
            selected_items.append(item)
        # Also check by file path for BDD scenarios
        elif any(suite_name in str(item.fspath) for suite_name in selected_suites):
            selected_items.append(item)
            
    items[:] = selected_items
    if selected_items:
        print(f"📊 Filtered to {len(selected_items)} tests from suites: {', '.join(selected_suites)}")
    else:
        print(f"⚠️ No tests found for suites: {', '.join(selected_suites)}")


def pytest_runtest_setup(item):
    """Execute suite and test setup before each test"""
    test_name = item.name
    suite_name = suite_manager.get_suite_by_test(test_name)
    
    if suite_name:
        # Execute suite setup if this is the first test in the suite
        if suite_name not in getattr(pytest, '_suite_setup_done', set()):
            suite_manager.execute_suite_setup(suite_name)
            if not hasattr(pytest, '_suite_setup_done'):
                pytest._suite_setup_done = set()
            pytest._suite_setup_done.add(suite_name)
            
        # Execute test setup
        suite_manager.execute_test_setup(suite_name, test_name)


def pytest_runtest_teardown(item):
    """Execute test teardown after each test"""
    test_name = item.name
    suite_name = suite_manager.get_suite_by_test(test_name)
    
    if suite_name:
        suite_manager.execute_test_teardown(suite_name, test_name)


def pytest_sessionfinish(session, exitstatus):
    """Execute suite teardown for all used suites"""
    if hasattr(pytest, '_suite_setup_done'):
        for suite_name in pytest._suite_setup_done:
            suite_manager.execute_suite_teardown(suite_name)


# Command line option for suite selection
def pytest_addoption(parser):
    """Add command line options for suite management"""
    parser.addoption(
        "--suite",
        action="store",
        default=None,
        help="Run specific test suites (comma-separated)"
    )
    parser.addoption(
        "--list-suites",
        action="store_true",
        default=False,
        help="List all available test suites"
    )


def pytest_cmdline_main(config):
    """Handle suite listing command"""
    if hasattr(config.option, 'list_suites') and config.option.list_suites:
        suite_manager.load_suite_config()
        suites = suite_manager.list_suites()
        
        if not suites:
            print("No test suites found.")
            print("💡 Create suites using @suite decorator or suite_config.json")
            return 0
            
        print("📦 Available Test Suites:")
        print("=" * 40)
        
        for suite_name in sorted(suites):
            info = suite_manager.get_suite_info(suite_name)
            print(f"\n🎯 {suite_name}")
            if info.get('description'):
                print(f"   Description: {info['description']}")
            print(f"   Tests: {len(info.get('tests', []))}")
            print(f"   Features: {len(info.get('features', []))}")
            print(f"   Tags: {info.get('tags', [])}")
            print(f"   Setup/Teardown: {info.get('setup_hooks', 0)}/{info.get('teardown_hooks', 0)}")
            print(f"   Enabled: {'✅' if info.get('enabled', True) else '❌'}")
            
        print(f"\n💡 Usage: pytest --suite=suite1,suite2")
        return 0