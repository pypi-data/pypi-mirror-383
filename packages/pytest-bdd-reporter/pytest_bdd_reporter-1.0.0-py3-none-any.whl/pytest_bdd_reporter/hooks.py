"""
BDD Hooks for setup and teardown functionality
"""
import inspect
from typing import List, Callable, Any

import pytest


class BDDHooks:
    """Manages BDD setup and teardown hooks"""
    
    def __init__(self):
        self.setup_hooks = []
        self.teardown_hooks = []
        self.feature_setup_hooks = {}
        self.feature_teardown_hooks = {}
        
    def register_setup_hook(self, func: Callable, feature: str = None):
        """Register a setup hook function"""
        if feature:
            if feature not in self.feature_setup_hooks:
                self.feature_setup_hooks[feature] = []
            self.feature_setup_hooks[feature].append(func)
        else:
            self.setup_hooks.append(func)
            
    def register_teardown_hook(self, func: Callable, feature: str = None):
        """Register a teardown hook function"""
        if feature:
            if feature not in self.feature_teardown_hooks:
                self.feature_teardown_hooks[feature] = []
            self.feature_teardown_hooks[feature].append(func)
        else:
            self.teardown_hooks.append(func)
            
    def run_setup_hooks(self, item):
        """Run setup hooks for a test item"""
        # Run global setup hooks
        for hook in self.setup_hooks:
            try:
                self._call_hook(hook, item)
            except Exception as e:
                pytest.fail(f"Setup hook failed: {e}")
                
        # Run feature-specific setup hooks
        if hasattr(item, 'scenario'):
            feature_name = item.scenario.feature.name
            if feature_name in self.feature_setup_hooks:
                for hook in self.feature_setup_hooks[feature_name]:
                    try:
                        self._call_hook(hook, item)
                    except Exception as e:
                        pytest.fail(f"Feature setup hook failed: {e}")
                        
    def run_teardown_hooks(self, item):
        """Run teardown hooks for a test item"""
        # Run feature-specific teardown hooks
        if hasattr(item, 'scenario'):
            feature_name = item.scenario.feature.name
            if feature_name in self.feature_teardown_hooks:
                for hook in self.feature_teardown_hooks[feature_name]:
                    try:
                        self._call_hook(hook, item)
                    except Exception as e:
                        # Log teardown errors but don't fail the test
                        print(f"Warning: Feature teardown hook failed: {e}")
                        
        # Run global teardown hooks
        for hook in self.teardown_hooks:
            try:
                self._call_hook(hook, item)
            except Exception as e:
                # Log teardown errors but don't fail the test
                print(f"Warning: Teardown hook failed: {e}")
                
    def _call_hook(self, hook: Callable, item):
        """Call a hook function with appropriate parameters"""
        sig = inspect.signature(hook)
        params = {}
        
        # Check what parameters the hook expects
        for param_name, param in sig.parameters.items():
            if param_name == 'item':
                params['item'] = item
            elif param_name == 'scenario' and hasattr(item, 'scenario'):
                params['scenario'] = item.scenario
            elif param_name == 'feature' and hasattr(item, 'scenario'):
                params['feature'] = item.scenario.feature
            elif param_name == 'request':
                params['request'] = item._request if hasattr(item, '_request') else None
                
        # Call the hook with the appropriate parameters
        hook(**params)


# Decorators for marking setup and teardown functions
def bdd_setup(feature: str = None):
    """Decorator to mark a function as a BDD setup hook"""
    def decorator(func):
        func._bdd_setup = True
        func._bdd_feature = feature
        return func
    return decorator


def bdd_teardown(feature: str = None):
    """Decorator to mark a function as a BDD teardown hook"""
    def decorator(func):
        func._bdd_teardown = True
        func._bdd_feature = feature
        return func
    return decorator


def pytest_configure(config):
    """Auto-discover and register BDD hooks"""
    # This will be called by pytest to discover hooks
    pass


def pytest_collection_modifyitems(config, items):
    """Discover and register BDD hooks from collected items"""
    hooks = BDDHooks()
    
    # Look for hook functions in the collected modules
    for item in items:
        module = item.module
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj):
                if hasattr(obj, '_bdd_setup'):
                    feature = getattr(obj, '_bdd_feature', None)
                    hooks.register_setup_hook(obj, feature)
                elif hasattr(obj, '_bdd_teardown'):
                    feature = getattr(obj, '_bdd_feature', None)
                    hooks.register_teardown_hook(obj, feature)
                    
    # Store hooks in config for later use
    config._bdd_hooks = hooks