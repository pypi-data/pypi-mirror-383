Feature: Stdout Capture Testing
    As a test reporter
    I want to capture all stdout output from tests
    So that I can see what happened during test execution

    Background:
        Given the stdout capture system is active
        And logging is configured properly

    @stdout @passed
    Scenario: Capture stdout from passing test
        Given I have a test that will pass
        When the test generates stdout output
        And the test generates log messages
        Then the stdout should be captured in the report
        And the logs should be captured in the report

    @stdout @failed
    Scenario: Capture stdout from failing test
        Given I have a test that will fail
        When the test generates stdout output before failing
        And the test generates error messages
        Then the stdout should be captured despite the failure
        And the error logs should be captured

    @stdout @complex
    Scenario: Capture complex output with formatting
        Given I have a test with complex output
        When the test generates formatted tables
        And the test generates unicode characters
        And the test generates multiple output types
        Then all output should be preserved in the report
        And the formatting should be maintained