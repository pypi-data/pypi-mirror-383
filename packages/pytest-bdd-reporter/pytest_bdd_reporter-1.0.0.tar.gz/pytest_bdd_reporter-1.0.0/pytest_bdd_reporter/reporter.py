"""
BDD Reporter for generating detailed HTML reports
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from .email_reporter import EmailReporter


class BDDReporter:
    """Generates detailed BDD reports similar to Robot Framework"""
    
    def __init__(self):
        self.test_results = []
        self.session_data = {}
        self.template_dir = Path(__file__).parent / "templates"
        self.static_dir = Path(__file__).parent / "static"
        self.email_reporter = EmailReporter()
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.jinja_env.filters['timestamp_to_time'] = self._timestamp_to_time
        self.jinja_env.filters['timestamp_to_datetime'] = self._timestamp_to_datetime
        
    def configure(self, config):
        """Configure reporter with pytest config"""
        self.config = config
        self.output_dir = Path(config.getoption("--bdd-report-dir", default="bdd_reports"))
        self.output_dir.mkdir(exist_ok=True)
        
    def session_start(self, session):
        """Called when test session starts"""
        # Extract suite name from session or config
        try:
            # Check if specific suites are selected
            if hasattr(session.config, 'option') and hasattr(session.config.option, 'suite') and session.config.option.suite:
                selected_suites = session.config.option.suite
                if ',' in selected_suites:
                    suite_name = f"Multiple Suites ({selected_suites})"
                else:
                    suite_name = selected_suites
            else:
                rootdir = getattr(session.config, 'rootdir', None)
                if rootdir:
                    suite_name = str(rootdir).split('/')[-1] if hasattr(rootdir, 'basename') else Path(str(rootdir)).name
                else:
                    suite_name = Path.cwd().name
        except:
            suite_name = "Test Suite"
            
        if hasattr(session.config, 'option') and hasattr(session.config.option, 'bdd_suite_name'):
            suite_name = session.config.option.bdd_suite_name
        
        self.session_data = {
            'start_time': datetime.now(),
            'suite_name': suite_name,
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'features': {},
            'scenarios': []
        }
        
    def session_finish(self, session, exitstatus, duration):
        """Called when test session finishes"""
        self.session_data.update({
            'end_time': datetime.now(),
            'duration': duration,
            'exit_status': exitstatus
        })
        
        # Calculate tag statistics
        self._calculate_tag_statistics()
        
        # Generate reports
        self._generate_html_report()
        self._generate_json_report()
        
        # Generate email report if requested
        if self.config.getoption("--bdd-email-report", default=False):
            self._generate_email_report()
        
    def add_scenario_result(self, scenario_data):
        """Add scenario result to the report"""
        self.test_results.append(scenario_data)
        
        # Update session statistics
        self.session_data['total_tests'] += 1
        if scenario_data['status'] == 'passed':
            self.session_data['passed'] += 1
        elif scenario_data['status'] == 'failed':
            self.session_data['failed'] += 1
        else:
            self.session_data['skipped'] += 1
            
        # Group by feature
        feature_name = scenario_data['feature']
        if feature_name not in self.session_data['features']:
            self.session_data['features'][feature_name] = {
                'name': feature_name,
                'scenarios': [],
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
            
        self.session_data['features'][feature_name]['scenarios'].append(scenario_data)
        self.session_data['features'][feature_name][scenario_data['status']] += 1
        
    def _generate_html_report(self):
        """Generate HTML reports (both summary and detailed log)"""
        summary = self._calculate_summary()
        
        # Load status management JavaScript
        status_js_file = self.template_dir / "status_management.js"
        status_management_js = ""
        if status_js_file.exists():
            with open(status_js_file, 'r') as f:
                status_management_js = f.read()
        
        # Generate main report (summary view)
        report_template = self.jinja_env.get_template('report.html')
        report_content = report_template.render(
            session=self.session_data,
            summary=summary,
            features=self.session_data['features'].values(),
            scenarios=self.test_results,
            status_management_js=status_management_js
        )
        
        report_file = self.output_dir / "bdd_report.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        # Generate detailed log (execution view)
        log_template = self.jinja_env.get_template('log.html')
        log_content = log_template.render(
            session=self.session_data,
            summary=summary,
            features=self.session_data['features'].values(),
            scenarios=self.test_results
        )
        
        log_file = self.output_dir / "bdd_log.html"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
            
        # Generate email summary page (simple version)
        email_template = self.jinja_env.get_template('email_summary.html')
        email_content = email_template.render(
            session=self.session_data,
            summary=summary,
            features=self.session_data['features'].values(),
            scenarios=self.test_results,
            report_url=f"file://{report_file.absolute()}"
        )
        
        email_file = self.output_dir / "email_summary.html"
        with open(email_file, 'w', encoding='utf-8') as f:
            f.write(email_content)
            
        # Generate comprehensive email report (full dashboard-like)
        email_report_template = self.jinja_env.get_template('email_report.html')
        email_report_content = email_report_template.render(
            session=self.session_data,
            summary=summary,
            features=self.session_data['features'].values(),
            scenarios=self.test_results,
            report_url=f"file://{report_file.absolute()}"
        )
        
        email_report_file = self.output_dir / "email_report.html"
        with open(email_report_file, 'w', encoding='utf-8') as f:
            f.write(email_report_content)
            
        # Generate text-based email report (universal compatibility)
        text_email_template = self.jinja_env.get_template('text_email_report.html')
        text_email_content = text_email_template.render(
            session=self.session_data,
            summary=summary,
            features=self.session_data['features'].values(),
            scenarios=self.test_results,
            report_url=f"file://{report_file.absolute()}"
        )
        
        text_email_file = self.output_dir / "text_email_report.html"
        with open(text_email_file, 'w', encoding='utf-8') as f:
            f.write(text_email_content)
            
        print(f"BDD Report generated: {report_file}")
        print(f"BDD Log generated: {log_file}")
        print(f"Email Summary generated: {email_file}")
        print(f"Email Report generated: {email_report_file}")
        print(f"Text Email Report generated: {text_email_file}")
        
    def _generate_json_report(self):
        """Generate JSON report for programmatic access"""
        report_data = {
            'session': self.session_data,
            'scenarios': self.test_results,
            'summary': self._calculate_summary()
        }
        
        # Convert datetime objects to strings for JSON serialization
        report_data = self._serialize_datetime(report_data)
        
        report_file = self.output_dir / "bdd_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
    def _calculate_summary(self):
        """Calculate summary statistics"""
        total = self.session_data['total_tests']
        passed = self.session_data['passed']
        failed = self.session_data['failed']
        skipped = self.session_data['skipped']
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'pass_rate': round(pass_rate, 2),
            'total_features': len(self.session_data['features'])
        }
        
    def _calculate_tag_statistics(self):
        """Calculate statistics by tags"""
        tag_stats = {}
        
        for scenario in self.test_results:
            for tag in scenario.get('tags', []):
                if tag not in tag_stats:
                    tag_stats[tag] = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
                
                tag_stats[tag]['total'] += 1
                tag_stats[tag][scenario['status']] += 1
        
        self.session_data['tag_statistics'] = tag_stats
    
    def _serialize_datetime(self, obj):
        """Convert datetime objects to strings for JSON serialization"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._serialize_datetime(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        else:
            return obj
            
    def _timestamp_to_time(self, timestamp):
        """Convert timestamp to formatted time string"""
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
        return str(timestamp)
        
    def _timestamp_to_datetime(self, timestamp):
        """Convert timestamp to formatted datetime string"""
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return str(timestamp)
    
    def _generate_email_report(self):
        """Generate email-friendly HTML report"""
        summary = self._calculate_summary()
        
        # Generate email HTML
        email_html = self.email_reporter.generate_email_report(
            self.session_data,
            self.test_results,
            summary,
            list(self.session_data['features'].values())
        )
        
        # Generate plain text summary
        email_text = self.email_reporter.generate_plain_text_summary(
            self.session_data,
            self.test_results,
            summary
        )
        
        # Save email report
        email_file = self.output_dir / "email_report.html"
        with open(email_file, 'w', encoding='utf-8') as f:
            f.write(email_html)
        
        # Save text summary
        text_file = self.output_dir / "email_summary.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(email_text)
            
        print(f"Email Report generated: {email_file}")
        print(f"Email Summary generated: {text_file}")