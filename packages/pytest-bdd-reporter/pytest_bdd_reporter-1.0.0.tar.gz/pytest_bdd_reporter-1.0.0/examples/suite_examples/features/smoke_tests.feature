Feature: Smoke Tests
    As a QA engineer
    I want to run critical smoke tests
    So that I can verify basic functionality works

    Background:
        Given the application is running

    @smoke @critical
    Scenario: User Login
        Given I have a test user account
        When I attempt to login
        Then I should be logged in successfully

    @smoke @critical
    Scenario: Basic Navigation
        Given I have a test user account
        And I attempt to login
        When I navigate to the dashboard
        Then I should see the main dashboard

    @smoke @critical
    Scenario: Core Functionality Access
        Given I have a test user account
        And I attempt to login
        When I access core features
        Then all core functionality should be available