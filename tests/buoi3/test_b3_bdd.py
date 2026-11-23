
"""
Buoi 3 - BDD with pytest-bdd.

Step definitions only call Page Objects.
No new locators are created in this file.

Run: pytest tests/buoi3 -v

Each Examples row becomes its own pytest test.
"""

import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.home_page import HomePage
from pages.cart_page import CartPage


pytestmark = [pytest.mark.bdd, pytest.mark.ui]


# ============================================================
# REGISTER FEATURE FILES
# ============================================================

scenarios("search.feature")
scenarios("cart.feature")


# ============================================================
# B3.1 - GIVEN: OPEN HOME PAGE
# ============================================================

@given("I am on the home page", target_fixture="home")
def home(page):
    home = HomePage(page).open()

    expect(home.product_names.first).to_be_visible()

    return home


# ============================================================
# WHEN: SEARCH PRODUCTS
# ============================================================

@when(parsers.parse('I search for "{keyword}"'))
def search(home, keyword):
    home.search(keyword)


# ============================================================
# B3.2 - THEN: CHECK SEARCH RESULTS
# ============================================================

@then(parsers.parse('every product name contains "{keyword}"'))
def names_contain(home, keyword):
    expect(home.search_completed).to_be_visible()

    names = home.product_names.all_inner_texts()

    assert names and all(
        keyword.lower() in name.lower()
        for name in names
    ), names


@then(parsers.parse('the search caption mentions "{keyword}"'))
def search_caption_mentions(home, keyword):
    expect(home.search_completed).to_be_visible()

    expect(home.search_caption).to_contain_text(keyword)


@then(parsers.parse('I see the message "{message}"'))
def see_message(home, message):
    expect(home.no_results).to_be_visible()

    expect(home.no_results).to_contain_text(message)


# ============================================================
# B3.4 - WHEN: OPEN PRODUCT
# ============================================================

@when(
    parsers.parse('I open the product "{product}"'),
    target_fixture="product_page"
)
def open_product(home, product):
    return home.open_product(product)


# ============================================================
# B3.4 - WHEN: ADD PRODUCT TO CART
# ============================================================

@when(
    parsers.parse(
        "I add it to the cart with quantity {quantity:d}"
    ),
    target_fixture="unit_price"
)
def add_to_cart(product_page, quantity):

    # Read unit price BEFORE adding the product to cart
    unit_price = product_page.price()

    # Add product with the requested quantity
    product_page.add_to_cart(quantity)

    # Wait for successful add-to-cart notification
    expect(product_page.toast).to_contain_text(
        "Product added to shopping cart"
    )

    # Verify cart quantity has been updated
    expect(product_page.cart_quantity).to_have_text(
        str(quantity)
    )

    # Navigate to cart using the Page Object method
    product_page.go_to_cart()

    return unit_price


# ============================================================
# B3.4 - THEN: CHECK CART LINE PRICE
# ============================================================

@then(
    parsers.parse(
        "the cart line price should equal "
        "the unit price multiplied by {quantity:d}"
    )
)
def check_line_price(page, unit_price, quantity):

    cart = CartPage(page)

    # Wait until the cart line price is visible
    expect(cart.line_prices.first).to_be_visible()

    # Calculate expected line price
    expected_price = unit_price * quantity

    # Get actual line prices
    actual_prices = cart.line_totals()

    assert actual_prices, "Cart has no product line"

    # Compare actual and expected price
    assert actual_prices[-1] == pytest.approx(
        expected_price,
        abs=0.01
    )


# ============================================================
# B3.4 - THEN: CHECK CART TOTAL
# ============================================================

@then("the cart total should equal the sum of line prices")
def check_cart_total(page):

    cart = CartPage(page)

    # Wait until cart total is visible
    expect(cart.total).to_be_visible()

    # Calculate expected cart total
    line_prices = cart.line_totals()

    expected_total = sum(line_prices)

    # Get actual cart total
    actual_total = cart.total_value()

    # Compare actual and expected total
    assert actual_total == pytest.approx(
        expected_total,
        abs=0.01
    )
