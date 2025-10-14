Feature: Regression Tests
    As a QA engineer
    I want to run comprehensive regression tests
    So that I can ensure existing functionality still works

    Background:
        Given I have test data loaded
        And all services are running

    @regression @comprehensive
    Scenario: User Management Operations
        When I perform user management operations
        Then all user operations should work correctly

    @regression @comprehensive
    Scenario: Data Processing
        When I process large datasets
        Then data processing should complete successfully

    @regression @comprehensive
    Scenario: Report Generation
        When I generate various reports
        Then reports should be generated correctly

    @regression @comprehensive
    Scenario: API Endpoint Testing
        When I test API endpoints
        Then all API endpoints should respond correctly