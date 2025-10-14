Feature: Shopping Cart Management
    As a customer
    I want to manage items in my shopping cart
    So that I can purchase products online

    Background:
        Given the online store is available
        And I am logged in as a customer

    @smoke @cart
    Scenario: Add single item to cart
        Given I am viewing a product "Laptop"
        When I click "Add to Cart"
        Then the item should be added to my cart
        And the cart count should show 1
        And the cart total should be updated

    @regression @cart
    Scenario: Add multiple items to cart
        Given I am viewing a product "Laptop"
        When I click "Add to Cart"
        And I navigate to product "Mouse"
        And I click "Add to Cart"
        Then the cart count should show 2
        And the cart total should include both items

    @cart @negative
    Scenario: Remove item from cart
        Given I have a "Laptop" in my cart
        When I remove the item from cart
        Then the cart should be empty
        And the cart total should be zero

    @cart @edge-case
    Scenario: Add out of stock item
        Given I am viewing an out of stock product "Limited Edition Phone"
        When I try to add it to cart
        Then I should see an out of stock message
        And the item should not be added to cart