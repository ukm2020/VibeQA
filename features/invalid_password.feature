@auth @negative @password-validation
Feature: Invalid Password Message Display
  Verify that an invalid password message is presented to the user when incorrect credentials are entered.

  Background:
    Given the application is running at "https://example.com"

  Scenario: Invalid Password Message Display
    Given I navigate to "https://example.com/login"
    When I wait 10 seconds for element "[data-test=login-form]" to appear
    When I type "testuser" into "[data-test=username-input]"
    When I type "wrongpassword" into "[data-test=password-input]"
    When I click on "[data-test=login-button]"
    When I wait 5 seconds for element "[data-test=error-message]" to appear
    Then the element "[data-test=error-message]" should contain text "Invalid password"
    Then I should remain on the current page