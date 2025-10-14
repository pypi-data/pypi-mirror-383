"""
Status Manager for handling test status overrides and bug tracking
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class TestStatusManager:
    """Manages test status overrides and bug tracking"""
    
    def __init__(self, config_dir: str = ".bdd_status"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.overrides_file = self.config_dir / "status_overrides.json"
        self.bug_tracking_file = self.config_dir / "bug_tracking.json"
        
        self.status_overrides = self._load_status_overrides()
        self.bug_tracking = self._load_bug_tracking()
    
    def _load_status_overrides(self) -> Dict:
        """Load status overrides from file"""
        if self.overrides_file.exists():
            try:
                with open(self.overrides_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _load_bug_tracking(self) -> Dict:
        """Load bug tracking data from file"""
        if self.bug_tracking_file.exists():
            try:
                with open(self.bug_tracking_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_status_overrides(self):
        """Save status overrides to file"""
        with open(self.overrides_file, 'w') as f:
            json.dump(self.status_overrides, f, indent=2)
    
    def _save_bug_tracking(self):
        """Save bug tracking data to file"""
        with open(self.bug_tracking_file, 'w') as f:
            json.dump(self.bug_tracking, f, indent=2)
    
    def override_test_status(self, test_name: str, original_status: str, 
                           new_status: str, reason: str, user: str = "Unknown"):
        """Override a test status with reason"""
        test_key = self._normalize_test_name(test_name)
        
        self.status_overrides[test_key] = {
            'original_status': original_status,
            'new_status': new_status,
            'reason': reason,
            'user': user,
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name
        }
        
        self._save_status_overrides()
    
    def assign_bug_id(self, test_name: str, bug_id: str, description: str = "", 
                     priority: str = "Medium", user: str = "Unknown"):
        """Assign a bug ID to a failed test"""
        test_key = self._normalize_test_name(test_name)
        
        self.bug_tracking[test_key] = {
            'bug_id': bug_id,
            'description': description,
            'priority': priority,
            'user': user,
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'status': 'Open'
        }
        
        self._save_bug_tracking()
    
    def get_effective_status(self, test_name: str, original_status: str) -> Dict:
        """Get the effective status for a test (considering overrides)"""
        test_key = self._normalize_test_name(test_name)
        
        result = {
            'status': original_status,
            'is_overridden': False,
            'override_reason': None,
            'bug_info': None
        }
        
        # Check for status override
        if test_key in self.status_overrides:
            override = self.status_overrides[test_key]
            result.update({
                'status': override['new_status'],
                'is_overridden': True,
                'override_reason': override['reason'],
                'override_user': override['user'],
                'override_timestamp': override['timestamp']
            })
        
        # Check for bug tracking
        if test_key in self.bug_tracking:
            bug = self.bug_tracking[test_key]
            result['bug_info'] = {
                'bug_id': bug['bug_id'],
                'description': bug['description'],
                'priority': bug['priority'],
                'user': bug['user'],
                'timestamp': bug['timestamp'],
                'status': bug['status']
            }
        
        return result
    
    def _normalize_test_name(self, test_name: str) -> str:
        """Normalize test name for consistent key generation"""
        return test_name.lower().replace(' ', '_').replace('-', '_')
    
    def get_all_overrides(self) -> Dict:
        """Get all status overrides"""
        return self.status_overrides.copy()
    
    def get_all_bugs(self) -> Dict:
        """Get all bug tracking entries"""
        return self.bug_tracking.copy()
    
    def remove_override(self, test_name: str):
        """Remove a status override"""
        test_key = self._normalize_test_name(test_name)
        if test_key in self.status_overrides:
            del self.status_overrides[test_key]
            self._save_status_overrides()
    
    def remove_bug(self, test_name: str):
        """Remove a bug tracking entry"""
        test_key = self._normalize_test_name(test_name)
        if test_key in self.bug_tracking:
            del self.bug_tracking[test_key]
            self._save_bug_tracking()
    
    def update_bug_status(self, test_name: str, status: str):
        """Update bug status (Open, In Progress, Fixed, Closed)"""
        test_key = self._normalize_test_name(test_name)
        if test_key in self.bug_tracking:
            self.bug_tracking[test_key]['status'] = status
            self.bug_tracking[test_key]['updated'] = datetime.now().isoformat()
            self._save_bug_tracking()