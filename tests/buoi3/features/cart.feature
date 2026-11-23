
Feature: Shopping cart

  As a shopper
  I want to add products to my cart with a chosen quantity
  So that I can see the correct product price and cart total

  Background:
    Given I am on the home page

  Scenario Outline: Cart total reflects product quantity
    When I open the product "<product>"
    And I add it to the cart with quantity <quantity>
    Then the cart line price should equal the unit price multiplied by <quantity>
    And the cart total should equal the sum of line prices

    Examples:
      | product            | quantity |
      | Combination Pliers | 1        |
      | Claw Hammer        | 3        |
