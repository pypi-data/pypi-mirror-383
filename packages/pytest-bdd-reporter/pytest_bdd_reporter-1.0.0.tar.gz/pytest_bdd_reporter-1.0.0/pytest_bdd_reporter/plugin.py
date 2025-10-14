"""
Main plugin module for pytest-bdd-reporter
"""
import json
import time
import sys
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import redirect_stdout, redirect_stderr
import threading

import pytest
from pytest_bdd import given, when, then
from pytest_bdd.parser import Step

from .reporter import BDDReporter
from .hooks import BDDHooks
from .status_manager import TestStatusManager
from .suite_manager import suite_manager


class BDDReporterPlugin:
    """Main plugin class for pytest-bdd enhanced reporting"""
    
    def __init__(self):
        self.reporter = BDDReporter()
        self.hooks = BDDHooks()
        self.status_manager = TestStatusManager()
        self.test_results = []
        self.current_scenario = None
        self.start_time = None
        self.bdd_items = []
        self.log_capture = {}
        self.stdout_capture = {}
        self.stderr_capture = {}
        self.original_stdout = None
        self.original_stderr = None
        self.capture_lock = threading.Lock()
        
    def pytest_configure(self, config):
        """Configure the plugin"""
        self.config = config
        self.reporter.configure(config)
        
        # Configure suite manager
        suite_manager.load_suite_config()
        
        # Register custom markers
        config.addinivalue_line(
            "markers", "bdd_setup: mark function as BDD setup hook"
        )
        config.addinivalue_line(
            "markers", "bdd_teardown: mark function as BDD teardown hook"
        )
        
    def pytest_collection_modifyitems(self, config, items):
        """Modify collected items to identify BDD tests"""
        for item in items:
            # Check if this is a BDD test
            if self._is_bdd_test(item):
                self.bdd_items.append(item)
                
    def _is_bdd_test(self, item):
        """Check if a test item is a BDD test"""
        # Check for scenario attribute
        if hasattr(item, 'scenario'):
            return True
        if hasattr(item, 'function') and hasattr(item.function, 'scenario'):
            return True
        # Check for pytest-bdd markers or fixtures
        if hasattr(item, 'pytestmark'):
            for mark in item.pytestmark:
                if 'bdd' in str(mark):
                    return True
        # Check function name patterns
        if hasattr(item, 'function'):
            func_name = item.function.__name__
            if any(keyword in func_name.lower() for keyword in ['scenario', 'feature', 'given', 'when', 'then']):
                return True
        return False
        
    def pytest_sessionstart(self, session):
        """Called after the Session object has been created"""
        self.start_time = time.time()
        self.reporter.session_start(session)
        
    def pytest_sessionfinish(self, session, exitstatus):
        """Called after whole test run finished"""
        end_time = time.time()
        duration = end_time - self.start_time
        self.reporter.session_finish(session, exitstatus, duration)
        
    def pytest_runtest_setup(self, item):
        """Called to perform the setup phase for a test item"""
        # Extract BDD scenario information
        test_name = item.name
        feature_name = "Unknown Feature"
        scenario_name = test_name
        
        # Check if this is a pytest-bdd test
        if hasattr(item, 'scenario'):
            # Direct scenario access
            scenario_name = item.scenario.name
            feature_name = item.scenario.feature.name
        elif hasattr(item, 'function') and hasattr(item.function, 'scenario'):
            # Function-level scenario access
            scenario_name = item.function.scenario.name
            feature_name = item.function.scenario.feature.name
        elif hasattr(item, '_request') and hasattr(item._request, 'node'):
            # Request node scenario access
            node = item._request.node
            if hasattr(node, 'scenario'):
                scenario_name = node.scenario.name
                feature_name = node.scenario.feature.name
        else:
            # Fallback: extract from test name and file, or use suite name
            scenario_name = test_name.replace('test_', '').replace('_', ' ').title()
            
            # Try to get suite name from suite manager
            from .suite_manager import suite_manager
            suite_name = suite_manager.get_suite_by_test(test_name)
            
            if suite_name:
                feature_name = suite_name.replace('_', ' ').title()
            elif hasattr(item, 'fspath'):
                feature_name = item.fspath.basename.replace('test_', '').replace('.py', '').title()
            else:
                # Use session suite name if available
                if hasattr(self.config, 'option') and hasattr(self.config.option, 'suite') and self.config.option.suite:
                    selected_suites = self.config.option.suite
                    if ',' not in selected_suites:
                        feature_name = selected_suites.replace('_', ' ').title()
                    else:
                        feature_name = "Multiple Suites"
        
        # Extract tags from pytest markers and BDD scenario
        tags = []
        
        # Get tags from pytest markers
        if hasattr(item, 'pytestmark'):
            for mark in item.pytestmark:
                if mark.name not in ['parametrize', 'skip', 'skipif', 'xfail', 'filterwarnings']:
                    tags.append(mark.name)
        
        # Get tags from BDD scenario if available
        if hasattr(item, 'scenario') and hasattr(item.scenario, 'tags'):
            for tag in item.scenario.tags:
                if tag.name not in tags:
                    tags.append(tag.name)
        elif hasattr(item, 'function') and hasattr(item.function, 'scenario') and hasattr(item.function.scenario, 'tags'):
            for tag in item.function.scenario.tags:
                if tag.name not in tags:
                    tags.append(tag.name)
        
        self.current_scenario = {
            'name': scenario_name,
            'feature': feature_name,
            'steps': [],
            'status': 'running',
            'start_time': time.time(),
            'setup_time': None,
            'teardown_time': None,
            'error': None,
            'logs': [],
            'stdout': '',
            'stderr': '',
            'tags': tags,
            'documentation': getattr(item.function, '__doc__', '') or ''
        }
        
        # Setup log capture for this test
        self._setup_log_capture(item)
        
        # Setup stdout/stderr capture
        self._setup_output_capture(item)
        
        # Run BDD setup hooks
        self.hooks.run_setup_hooks(item)
            
    def pytest_runtest_teardown(self, item, nextitem):
        """Called to perform the teardown phase for a test item"""
        if self.current_scenario:
            # Run BDD teardown hooks
            self.hooks.run_teardown_hooks(item)
            self.current_scenario['teardown_time'] = time.time()
            
    def pytest_runtest_makereport(self, item, call):
        """Called to create a TestReport for each phase of a test item"""
        if call.when == "call" and self.current_scenario:
            self.current_scenario['end_time'] = time.time()
            self.current_scenario['duration'] = (
                self.current_scenario['end_time'] - self.current_scenario['start_time']
            )
            
            # Capture logs and output
            self._capture_test_output(item, call)
            
            if call.excinfo:
                self.current_scenario['status'] = 'failed'
                self.current_scenario['error'] = str(call.excinfo.value)
                # Add full traceback for failed tests
                if hasattr(call.excinfo, 'traceback'):
                    self.current_scenario['traceback'] = str(call.excinfo.traceback)
            else:
                self.current_scenario['status'] = 'passed'
            
            # Apply status overrides and bug tracking
            test_name = self.current_scenario['name']
            original_status = self.current_scenario['status']
            status_info = self.status_manager.get_effective_status(test_name, original_status)
            
            # Update scenario with effective status and additional info
            self.current_scenario.update({
                'original_status': original_status,
                'status': status_info['status'],
                'is_overridden': status_info['is_overridden'],
                'override_reason': status_info.get('override_reason'),
                'override_user': status_info.get('override_user'),
                'override_timestamp': status_info.get('override_timestamp'),
                'bug_info': status_info.get('bug_info')
            })
                
            self.reporter.add_scenario_result(self.current_scenario.copy())
            self.current_scenario = None
            
    def _setup_log_capture(self, item):
        """Setup log capture for a test item"""
        test_id = item.nodeid
        
        # Create a custom log handler to capture logs
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add handler to root logger and all existing loggers
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        
        # Also add to any existing loggers to ensure we capture everything
        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.addHandler(handler)
        
        self.log_capture[test_id] = {
            'handler': handler,
            'stream': log_stream
        }
        
    def _capture_test_output(self, item, call):
        """Capture test output including logs, stdout, and stderr"""
        test_id = item.nodeid
        
        # Capture logs
        if test_id in self.log_capture:
            log_content = self.log_capture[test_id]['stream'].getvalue()
            if log_content:
                self.current_scenario['logs'] = log_content.split('\n')
            
            # Clean up log handler from all loggers
            handler = self.log_capture[test_id]['handler']
            root_logger = logging.getLogger()
            root_logger.removeHandler(handler)
            
            # Remove from all existing loggers
            for logger_name in logging.Logger.manager.loggerDict:
                logger = logging.getLogger(logger_name)
                if handler in logger.handlers:
                    logger.removeHandler(handler)
            
            del self.log_capture[test_id]
        
        # Try multiple ways to capture stdout/stderr
        if hasattr(call, 'capstdout') and call.capstdout:
            self.current_scenario['stdout'] = call.capstdout
        if hasattr(call, 'capstderr') and call.capstderr:
            self.current_scenario['stderr'] = call.capstderr
            
        # Try to get captured output from pytest's capture manager
        if hasattr(item.config, '_capture_manager'):
            capture_manager = item.config._capture_manager
            if capture_manager and hasattr(capture_manager, 'read_global_capture'):
                try:
                    out, err = capture_manager.read_global_capture()
                    if out and not self.current_scenario['stdout']:
                        self.current_scenario['stdout'] = out
                    if err and not self.current_scenario['stderr']:
                        self.current_scenario['stderr'] = err
                except:
                    pass
                    
        # Try to get from pytest's capture fixture
        if hasattr(item, 'funcargs'):
            for name, value in item.funcargs.items():
                if name == 'capfd' and hasattr(value, 'readouterr'):
                    try:
                        captured = value.readouterr()
                        if captured.out and not self.current_scenario['stdout']:
                            self.current_scenario['stdout'] = captured.out
                        if captured.err and not self.current_scenario['stderr']:
                            self.current_scenario['stderr'] = captured.err
                    except:
                        pass
        
        # Try custom output capture
        self._capture_custom_output(item)
    
    def _setup_output_capture(self, item):
        """Setup stdout/stderr capture for a test item"""
        test_id = item.nodeid
        
        with self.capture_lock:
            # Create string buffers to capture output
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            self.stdout_capture[test_id] = {
                'buffer': stdout_buffer,
                'content': []
            }
            self.stderr_capture[test_id] = {
                'buffer': stderr_buffer,
                'content': []
            }
            
            # Store original stdout/stderr
            if not self.original_stdout:
                self.original_stdout = sys.stdout
                self.original_stderr = sys.stderr
    
    def _capture_custom_output(self, item):
        """Capture custom stdout/stderr output"""
        test_id = item.nodeid
        
        with self.capture_lock:
            if test_id in self.stdout_capture:
                capture_data = self.stdout_capture[test_id]
                stdout_content = capture_data['buffer'].getvalue()
                all_content = '\n'.join(capture_data['content'])
                if stdout_content.strip() or all_content.strip():
                    existing_stdout = self.current_scenario.get('stdout', '')
                    combined_content = existing_stdout + all_content + stdout_content
                    self.current_scenario['stdout'] = combined_content
                del self.stdout_capture[test_id]
                
            if test_id in self.stderr_capture:
                capture_data = self.stderr_capture[test_id]
                stderr_content = capture_data['buffer'].getvalue()
                all_content = '\n'.join(capture_data['content'])
                if stderr_content.strip() or all_content.strip():
                    existing_stderr = self.current_scenario.get('stderr', '')
                    combined_content = existing_stderr + all_content + stderr_content
                    self.current_scenario['stderr'] = combined_content
                del self.stderr_capture[test_id]


def pytest_addoption(parser):
    """Add command line options"""
    group = parser.getgroup("bdd-reporter")
    group.addoption(
        "--bdd-report-dir",
        action="store",
        default="bdd_reports",
        help="Directory to store BDD reports (default: bdd_reports)"
    )
    group.addoption(
        "--bdd-capture-logs",
        action="store_true",
        default=True,
        help="Capture logs in BDD reports (default: True)"
    )
    group.addoption(
        "--bdd-email-report",
        action="store_true",
        default=False,
        help="Generate email-friendly report (default: False)"
    )
    group.addoption(
        "--bdd-override-status",
        action="store",
        help="Override test status: test_name:new_status:reason"
    )
    group.addoption(
        "--suite",
        action="store",
        default=None,
        help="Run specific test suites (comma-separated)"
    )
    group.addoption(
        "--list-suites",
        action="store_true",
        default=False,
        help="List all available test suites"
    )
    group.addoption(
        "--bdd-assign-bug",
        action="store",
        help="Assign bug ID: test_name:bug_id:description"
    )


# Global plugin instance
_plugin_instance = None


def pytest_configure(config):
    """Register the plugin"""
    global _plugin_instance
    if _plugin_instance is None:
        _plugin_instance = BDDReporterPlugin()
        _plugin_instance.pytest_configure(config)


def pytest_unconfigure(config):
    """Unregister the plugin"""
    global _plugin_instance
    _plugin_instance = None


def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    if _plugin_instance:
        _plugin_instance.pytest_sessionstart(session)


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    if _plugin_instance:
        _plugin_instance.pytest_sessionfinish(session, exitstatus)


def pytest_runtest_setup(item):
    """Called to perform the setup phase for a test item"""
    if _plugin_instance:
        _plugin_instance.pytest_runtest_setup(item)


def pytest_runtest_teardown(item, nextitem):
    """Called to perform the teardown phase for a test item"""
    if _plugin_instance:
        _plugin_instance.pytest_runtest_teardown(item, nextitem)


def pytest_runtest_makereport(item, call):
    """Called to create a TestReport for each phase of a test item"""
    if _plugin_instance:
        _plugin_instance.pytest_runtest_makereport(item, call)


def pytest_runtest_logreport(report):
    """Called when a test report is created"""
    if _plugin_instance and _plugin_instance.current_scenario:
        # Capture for all phases (setup, call, teardown) to get complete output
        if hasattr(report, 'capstdout') and report.capstdout:
            existing_stdout = _plugin_instance.current_scenario.get('stdout', '')
            _plugin_instance.current_scenario['stdout'] = existing_stdout + report.capstdout
        if hasattr(report, 'capstderr') and report.capstderr:
            existing_stderr = _plugin_instance.current_scenario.get('stderr', '')
            _plugin_instance.current_scenario['stderr'] = existing_stderr + report.capstderr
        if hasattr(report, 'caplog') and report.caplog:
            existing_logs = _plugin_instance.current_scenario.get('logs', [])
            new_logs = [line for line in report.caplog.split('\n') if line.strip()]
            _plugin_instance.current_scenario['logs'] = existing_logs + new_logs
        
        # Try to get sections from the report - this is the most reliable way for ALL tests
        if hasattr(report, 'sections'):
            for section_name, section_content in report.sections:
                if 'stdout' in section_name.lower() and section_content.strip():
                    existing_stdout = _plugin_instance.current_scenario.get('stdout', '')
                    _plugin_instance.current_scenario['stdout'] = existing_stdout + '\n' + section_content
                elif 'stderr' in section_name.lower() and section_content.strip():
                    existing_stderr = _plugin_instance.current_scenario.get('stderr', '')
                    _plugin_instance.current_scenario['stderr'] = existing_stderr + '\n' + section_content
                elif 'log' in section_name.lower() and section_content.strip():
                    existing_logs = _plugin_instance.current_scenario.get('logs', [])
                    new_logs = [line for line in section_content.split('\n') if line.strip()]
                    _plugin_instance.current_scenario['logs'] = existing_logs + new_logs





def pytest_collection_modifyitems(config, items):
    """Modify collected items to identify BDD tests"""
    if _plugin_instance:
        _plugin_instance.pytest_collection_modifyitems(config, items)