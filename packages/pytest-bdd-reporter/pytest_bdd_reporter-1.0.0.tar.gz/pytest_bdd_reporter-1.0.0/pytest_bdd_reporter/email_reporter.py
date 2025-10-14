"""
Email Report Generator for creating email-friendly HTML reports
"""
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class EmailReporter:
    """Generates email-friendly HTML reports"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
    
    def generate_email_report(self, session_data: Dict, scenarios: List[Dict], 
                            summary: Dict, features: List[Dict]) -> str:
        """Generate an email-friendly HTML report"""
        
        # Calculate additional statistics
        total_duration = session_data.get('duration', 0)
        pass_rate = summary.get('pass_rate', 0)
        
        # Categorize tests
        critical_failures = []
        known_issues = []
        passed_tests = []
        
        for scenario in scenarios:
            if scenario.get('status') == 'failed':
                if scenario.get('bug_info'):
                    known_issues.append(scenario)
                else:
                    critical_failures.append(scenario)
            elif scenario.get('status') == 'passed' or scenario.get('is_overridden'):
                passed_tests.append(scenario)
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .summary {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #007bff;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .stat-box {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .pass {{ color: #28a745; }}
        .fail {{ color: #dc3545; }}
        .skip {{ color: #ffc107; }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}
        .section h3 {{
            margin-top: 0;
            color: #495057;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 8px;
        }}
        .test-item {{
            padding: 10px;
            margin: 8px 0;
            border-radius: 4px;
            border-left: 4px solid #dee2e6;
        }}
        .test-item.passed {{
            background: #d4edda;
            border-left-color: #28a745;
        }}
        .test-item.failed {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        .test-item.known-issue {{
            background: #fff3cd;
            border-left-color: #ffc107;
        }}
        .test-name {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .test-details {{
            font-size: 12px;
            color: #666;
        }}
        .bug-info {{
            background: #e2e3e5;
            padding: 8px;
            border-radius: 4px;
            margin-top: 8px;
            font-size: 12px;
        }}
        .override-info {{
            background: #cce5ff;
            padding: 8px;
            border-radius: 4px;
            margin-top: 8px;
            font-size: 12px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #dee2e6;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }}
        .action-required {{
            background: #f8d7da;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #dc3545;
            margin: 15px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        th {{
            background: #f8f9fa;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 BDD Test Execution Report</h1>
        <p>Generated on {session_data.get('end_time', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Executive Summary</h2>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-value">{summary['total']}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-box">
                <div class="stat-value pass">{summary['passed']}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value fail">{summary['failed']}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{pass_rate:.1f}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_duration:.1f}s</div>
                <div class="stat-label">Duration</div>
            </div>
        </div>
        
        {"<div class='action-required'><strong>⚠️ Action Required:</strong> " + str(len(critical_failures)) + " critical test failures need immediate attention.</div>" if critical_failures else ""}
        {"<div class='highlight'><strong>📋 Note:</strong> " + str(len(known_issues)) + " known issues are being tracked.</div>" if known_issues else ""}
    </div>
"""

        # Critical Failures Section
        if critical_failures:
            html_content += """
    <div class="section">
        <h3>🚨 Critical Failures (Immediate Action Required)</h3>
"""
            for test in critical_failures:
                error_msg = test.get('error', '').split('\n')[0][:100]
                html_content += f"""
        <div class="test-item failed">
            <div class="test-name">{test['name']}</div>
            <div class="test-details">
                Feature: {test['feature']} | Duration: {test['duration']:.3f}s
                {f"<br>Error: {error_msg}..." if error_msg else ""}
            </div>
        </div>"""
            html_content += "\n    </div>"

        # Known Issues Section
        if known_issues:
            html_content += """
    <div class="section">
        <h3>📋 Known Issues (Being Tracked)</h3>
"""
            for test in known_issues:
                bug_info = test.get('bug_info', {})
                html_content += f"""
        <div class="test-item known-issue">
            <div class="test-name">{test['name']}</div>
            <div class="test-details">
                Feature: {test['feature']} | Duration: {test['duration']:.3f}s
            </div>
            {f'<div class="bug-info"><strong>Bug ID:</strong> {bug_info.get("bug_id", "N/A")} | <strong>Priority:</strong> {bug_info.get("priority", "Medium")} | <strong>Status:</strong> {bug_info.get("status", "Open")}<br>{bug_info.get("description", "")}</div>' if bug_info else ""}
        </div>"""
            html_content += "\n    </div>"

        # Passed Tests Section (Summary)
        if passed_tests:
            html_content += f"""
    <div class="section">
        <h3>✅ Passed Tests ({len(passed_tests)} tests)</h3>
        <p>All tests in this category executed successfully.</p>
"""
            # Show overridden tests separately
            overridden_tests = [t for t in passed_tests if t.get('is_overridden')]
            if overridden_tests:
                html_content += "<h4>Status Overrides:</h4>"
                for test in overridden_tests:
                    html_content += f"""
        <div class="test-item passed">
            <div class="test-name">{test['name']}</div>
            <div class="test-details">Feature: {test['feature']}</div>
            <div class="override-info">
                <strong>Override:</strong> {test.get('override_reason', 'No reason provided')}
            </div>
        </div>"""
            html_content += "\n    </div>"

        # Feature Summary Table
        if features:
            html_content += """
    <div class="section">
        <h3>📈 Feature Summary</h3>
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th>Total</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Pass Rate</th>
                </tr>
            </thead>
            <tbody>
"""
            for feature in features:
                total = feature['passed'] + feature['failed'] + feature.get('skipped', 0)
                pass_rate = (feature['passed'] / total * 100) if total > 0 else 0
                html_content += f"""
                <tr>
                    <td>{feature['name']}</td>
                    <td>{total}</td>
                    <td class="pass">{feature['passed']}</td>
                    <td class="fail">{feature['failed']}</td>
                    <td>{pass_rate:.1f}%</td>
                </tr>"""
            html_content += """
            </tbody>
        </table>
    </div>
"""

        # Recommendations Section
        html_content += """
    <div class="section">
        <h3>💡 Recommendations</h3>
        <ul>
"""
        if critical_failures:
            html_content += f"<li><strong>Priority 1:</strong> Investigate and fix {len(critical_failures)} critical test failures</li>"
        if known_issues:
            html_content += f"<li><strong>Priority 2:</strong> Review status of {len(known_issues)} tracked bugs</li>"
        if pass_rate < 80:
            html_content += "<li><strong>Quality Gate:</strong> Pass rate below 80% - consider blocking deployment</li>"
        elif pass_rate < 95:
            html_content += "<li><strong>Quality Improvement:</strong> Pass rate could be improved - review test stability</li>"
        else:
            html_content += "<li><strong>Excellent:</strong> High pass rate indicates good code quality</li>"
        
        html_content += """
        </ul>
    </div>
    
    <div class="footer">
        <p>📧 This report was generated by pytest-bdd-reporter</p>
        <p>For detailed logs and interactive features, view the full HTML reports</p>
    </div>
</body>
</html>
"""
        return html_content
    
    def generate_plain_text_summary(self, session_data: Dict, scenarios: List[Dict], 
                                   summary: Dict) -> str:
        """Generate a plain text summary for email body"""
        
        critical_failures = [s for s in scenarios if s.get('status') == 'failed' and not s.get('bug_info')]
        known_issues = [s for s in scenarios if s.get('bug_info')]
        
        text = f"""
BDD Test Execution Summary
==========================

📊 Results Overview:
• Total Tests: {summary['total']}
• Passed: {summary['passed']} ({summary['pass_rate']:.1f}%)
• Failed: {summary['failed']}
• Duration: {session_data.get('duration', 0):.1f}s

🚨 Critical Issues: {len(critical_failures)}
📋 Known Issues: {len(known_issues)}

{"⚠️  ATTENTION REQUIRED: Critical test failures detected!" if critical_failures else "✅ All critical tests passing"}

For detailed analysis, please see the attached HTML report.
"""
        return text.strip()