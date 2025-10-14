Feature: User Login
    As a user
    I want to be able to login to the system
    So that I can access my account

    Background:
        Given the application is running
        And the database is clean

    Scenario: Successful login with valid credentials
        Given I am on the login page
        When I enter valid username "testuser"
        And I enter valid password "testpass"
        And I click the login button
        Then I should be redirected to the dashboard
        And I should see a welcome message

    Scenario: Failed login with invalid credentials
        Given I am on the login page
        When I enter invalid username "wronguser"
        And I enter invalid password "wrongpass"
        And I click the login button
        Then I should see an error message
        And I should remain on the login page