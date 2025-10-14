# 📊 pytest-bdd-reporter

**Enterprise-grade BDD test reporting with interactive dashboards, suite management, and comprehensive email integration.**

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![pytest](https://img.shields.io/badge/pytest-6.0+-green.svg)](https://pytest.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 **Key Features**

- **📊 Interactive Dashboards** - Professional Robot Framework-style reports
- **📧 Universal Email Integration** - Text-based reports for all email providers
- **📦 Suite Management** - Organize and run tests by logical suites
- **🎛️ Status Management** - Override test results with interactive UI
- **📱 Mobile Responsive** - Works perfectly on all devices
- **🔍 Advanced Filtering** - Search, filter, and analyze test results
- **📋 Comprehensive Logging** - Capture and display detailed execution logs
- **🎨 Professional Design** - Corporate-grade appearance for stakeholders

## 🚀 **Quick Start**

### **Installation**

```bash
pip install pytest-bdd-reporter
```

### **Basic Usage**

```bash
# Run tests with BDD reporting
pytest --bdd-report-dir=reports

# Run specific test suite
pytest --suite=smoke_tests --bdd-report-dir=reports

# Generate email-friendly reports
pytest --bdd-email-report --bdd-report-dir=reports
```

### **Generated Reports**

After running tests, you'll find these reports in your output directory:

- **`bdd_report.html`** - Interactive main dashboard
- **`text_email_report.html`** - Text-based email report
- **`bdd_log.html`** - Detailed execution logs
- **`bdd_report.json`** - Machine-readable data

## 📊 **Report Features**

### **Interactive Dashboard**

```html
<!-- Enhanced 8-column test table -->
| Test Name | Status | Duration | Suite | Tags | Start Time | Logs | Actions |
|-----------|--------|----------|-------|------|------------|------|---------|
| test_login | PASSED | 0.123s | smoke_tests | auth,critical | 14:30:15 | 📋 Logs | 📄 Details |
```

**Features:**
- **Real-time search** across all columns
- **Status filtering** (Pass/Fail/Skip)
- **Performance indicators** (FAST/SLOW)
- **Interactive actions** (Copy error, View logs)
- **Suite statistics** with logs column

### **Text Email Reports**

Perfect for stakeholder communication with universal email compatibility:

```
📧 SUBJECT: smoke_tests Report : 2025:10:13: Total : 10 ; Pass : 9: Fail : 1 ; PassWExcep: 0

📊 EXECUTIVE SUMMARY
------------------------------
Suite Name      : smoke_tests
Test Date       : 2025-10-13
Total Tests     : 10
Passed Tests    : 9
Failed Tests    : 1
Pass Rate       : 90.0%

📋 COMPLETE TEST RESULTS
------------------------------
| # | Test Name                    | Status  | Duration | Suite           | Tags        |
|---|------------------------------|---------|----------|-----------------|-------------|
|  1 | test_user_login              | PASSED  |    0.123s | smoke_tests     | auth        |
|  2 | test_navigation              | FAILED  |    2.456s | smoke_tests     | ui          |
```

## 📦 **Suite Management**

Organize tests into logical suites with setup/teardown support:

### **Define Test Suites**

```python
from pytest_bdd_reporter.suite_manager import suite, suite_setup, suite_teardown

@suite(
    name="smoke_tests",
    description="Critical functionality tests",
    tests=["test_login", "test_navigation"],
    tags=["smoke", "critical"]
)
def smoke_suite_config():
    pass

@suite_setup("smoke_tests")
def setup_smoke_environment():
    print("🔧 Setting up smoke test environment")
    # Initialize test data, start services, etc.

@suite_teardown("smoke_tests")
def cleanup_smoke_environment():
    print("🧹 Cleaning up smoke test environment")
    # Stop services, clean data, etc.
```

### **Run Specific Suites**

```bash
# List available suites
pytest --list-suites

# Run smoke tests only
pytest --suite=smoke_tests

# Run multiple suites
pytest --suite=smoke_tests,regression_tests

# Run with custom report directory
pytest --suite=smoke_tests --bdd-report-dir=smoke_reports
```

## 🎛️ **Interactive Status Management**

Override test results with the built-in status management panel:

```javascript
// Available in the web interface
- Override test status (Pass/Fail/Skip)
- Add bug tracking information
- Provide override reasons
- Export updated results
```

**Features:**
- **Visual status override** with dropdown selection
- **Bug ID assignment** with priority levels
- **Reason tracking** for audit trails
- **Real-time updates** reflected in reports

## 📧 **Email Integration**

### **Multiple Email Formats**

1. **Text-based (Recommended)** - Universal compatibility
2. **HTML format** - Rich formatting for modern clients
3. **Executive summary** - Key metrics only

### **Email Features**

```python
# Email subject format (automatically generated)
"suite_name Report : YYYY:MM:DD: Total : X ; Pass : Y: Fail : Z ; PassWExcep: W"

# Example
"smoke_tests Report : 2025:10:13: Total : 10 ; Pass : 9: Fail : 1 ; PassWExcep: 0"
```

**Copy Options:**
- **📧 Copy Subject** - Email subject line only
- **📝 Copy Complete Report** - Full text report
- **✉️ Open Email Client** - Direct email integration
- **📊 Copy Summary** - Executive summary only

## 🔧 **Configuration**

### **Command Line Options**

```bash
# Basic reporting
pytest --bdd-report-dir=reports

# Email reports
pytest --bdd-email-report

# Suite selection
pytest --suite=suite1,suite2

# List available suites
pytest --list-suites

# Override test status
pytest --bdd-override-status="test_name:passed:Business approved"
```

### **Suite Configuration File**

Create `suite_config.json` for persistent suite definitions:

```json
{
  "smoke_tests": {
    "name": "smoke_tests",
    "description": "Critical functionality tests",
    "tests": ["test_login", "test_navigation"],
    "tags": ["smoke", "critical"],
    "enabled": true,
    "priority": 1
  },
  "regression_tests": {
    "name": "regression_tests",
    "description": "Comprehensive regression testing",
    "tests": ["test_*"],
    "tags": ["regression"],
    "enabled": true,
    "priority": 2
  }
}
```

## 📱 **Mobile & Responsive Design**

All reports are fully responsive and work perfectly on:

- **Desktop browsers** (Chrome, Firefox, Safari, Edge)
- **Tablet devices** (iPad, Android tablets)
- **Mobile phones** (iOS, Android)
- **Print media** (PDF generation, printing)

## 🎨 **Customization**

### **Report Styling**

The reports use professional styling with:
- **Corporate color scheme** (Blue, green, red indicators)
- **Clean typography** (Arial font family)
- **Responsive layout** (CSS Grid and Flexbox)
- **Print-friendly** design

### **Custom Templates**

You can customize report templates by modifying:
- `templates/report.html` - Main dashboard
- `templates/text_email_report.html` - Email reports
- `templates/log.html` - Detailed logs

## 🧪 **Examples**

### **Basic BDD Test**

```python
import pytest
from pytest_bdd import scenarios, given, when, then

scenarios('features/login.feature')

@given("I have a user account")
def user_account():
    return {"username": "test_user", "password": "test_pass"}

@when("I attempt to login")
def attempt_login(user_account):
    # Login logic here
    return login(user_account["username"], user_account["password"])

@then("I should be logged in successfully")
def verify_login(attempt_login):
    assert attempt_login.success
    assert attempt_login.user_id is not None
```

### **Suite-based Testing**

```python
from pytest_bdd_reporter.suite_manager import suite, suite_setup

@suite(
    name="api_tests",
    description="API endpoint testing",
    tests=["test_get_users", "test_create_user", "test_update_user"],
    tags=["api", "integration"]
)
def api_suite():
    pass

@suite_setup("api_tests")
def setup_api_tests():
    # Start test server, initialize database, etc.
    pass

def test_get_users():
    # Test implementation
    pass
```

## 📊 **Report Structure**

### **Main Dashboard Sections**

1. **Report Summary** - Key metrics and suite information
2. **Test Statistics** - Pass/fail counts and percentages
3. **Suite Statistics** - Breakdown by test suites
4. **Test Details** - 8-column detailed test table
5. **Suite Details** - Expandable suite information

### **Email Report Sections**

1. **Executive Summary** - Key metrics for stakeholders
2. **Failed Tests** - Detailed failure information (when applicable)
3. **Complete Test Results** - Table format with all tests
4. **Suite Breakdown** - Statistics by suite (for multiple suites)
5. **Key Metrics** - Performance and success indicators

## 🔍 **Advanced Features**

### **Search and Filtering**

- **Real-time search** across test names, suites, and tags
- **Status filtering** (All, Pass, Fail, Skip)
- **Suite filtering** for focused views
- **Performance filtering** (Fast, Slow tests)

### **Performance Analysis**

- **Duration tracking** with FAST/SLOW indicators
- **Performance metrics** (Average, fastest, slowest tests)
- **Trend analysis** across test runs
- **Resource usage** monitoring

### **Integration Support**

- **CI/CD pipelines** (Jenkins, GitHub Actions, GitLab CI)
- **Bug tracking** (Jira, Azure DevOps, GitHub Issues)
- **Notification systems** (Slack, Teams, Email)
- **Test management** tools integration

## 🛠️ **Development**

### **Requirements**

- Python 3.7+
- pytest 6.0+
- pytest-bdd (for BDD scenarios)

### **Installation for Development**

```bash
git clone https://github.com/your-repo/pytest-bdd-reporter.git
cd pytest-bdd-reporter
pip install -e .
```

### **Running Tests**

```bash
# Run the test suite
pytest examples/

# Run with reporting
pytest examples/ --bdd-report-dir=test_reports

# Run specific suite
pytest examples/ --suite=demo_suite
```

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 **Support**

For questions, issues, or feature requests, please open an issue on GitHub.

---

**pytest-bdd-reporter** - Professional BDD test reporting for enterprise teams. 🚀