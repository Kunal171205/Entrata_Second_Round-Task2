import pytest
import os
from playwright.sync_api import Page, expect

# Construct the absolute file URL to index.html
# Using os.path.abspath ensures it works no matter where pytest is run from.
HTML_FILE_PATH = f"file:///{os.path.abspath('index.html').replace(chr(92), '/')}"

def test_original_bug_scenario_resolved(page: Page):
    """
    Test Case 1: Verifies the original bug is fixed.
    Input: Bill=$10.03, Tip=15%, People=3
    Expected:
    - Grand Total should be exactly $11.53 (tip applied exactly once, not twice).
    - Shares should be $3.85, $3.84, $3.84.
    - Sum Check should be Exact Match.
    """
    page.goto(HTML_FILE_PATH)
    
    # 1. Fill inputs
    page.fill("#bill", "10.03")
    page.fill("#people", "3")
    
    # Click 15% pill (using the value directly or simulating typing)
    page.click("button[data-val='15']")
    
    # Wait a moment for JS to compute (though it's synchronous)
    page.wait_for_selector("#val-total")

    # 2. Assert Grand Total is $11.53, not $13.27
    expect(page.locator("#val-total")).to_have_text("$11.53")
    
    # 3. Verify exactly 3 rows in the table
    rows = page.locator("#breakdown-body tr")
    expect(rows).to_have_count(3)
    
    # 4. Verify Individual Shares
    # Person 1 gets the remainder cent ($3.85)
    expect(rows.nth(0).locator("td.share")).to_have_text("$3.85")
    # Person 2 & 3 get the base share ($3.84)
    expect(rows.nth(1).locator("td.share")).to_have_text("$3.84")
    expect(rows.nth(2).locator("td.share")).to_have_text("$3.84")
    
    # 5. Verify the Sum Check confirms an exact mathematical match
    expect(page.locator("#sum-val")).to_have_text("$11.53")
    expect(page.locator("#sum-icon")).to_contain_text("Exact Match")


def test_even_split_no_remainder(page: Page):
    """
    Test Case 2: Even division.
    Input: Bill=$30.00, Tip=0%, People=3
    Expected:
    - Grand Total is $30.00
    - Each share is exactly $10.00
    - No remainder notes are shown.
    """
    page.goto(HTML_FILE_PATH)
    
    page.fill("#bill", "30.00")
    page.fill("#people", "3")
    page.fill("#tip", "0") # Override pills
    # Trigger input event manually since we used fill on a number input
    page.locator("#tip").press("Enter")
    
    expect(page.locator("#val-total")).to_have_text("$30.00")
    
    rows = page.locator("#breakdown-body tr")
    expect(rows).to_have_count(3)
    
    for i in range(3):
        expect(rows.nth(i).locator("td.share")).to_have_text("$10.00")
        
    expect(page.locator("#sum-icon")).to_contain_text("Exact Match")


def test_large_party_remainder_distribution(page: Page):
    """
    Test Case 3: Large party with uneven remainder.
    Input: Bill=$10.02, Tip=0%, People=5
    Expected:
    - Base share is $2.00, remainder is 2 cents.
    - Person 1 & 2 pay $2.01, Person 3, 4, & 5 pay $2.00.
    """
    page.goto(HTML_FILE_PATH)
    
    page.fill("#bill", "10.02")
    page.fill("#people", "5")
    page.fill("#tip", "0")
    page.locator("#tip").press("Enter")
    
    rows = page.locator("#breakdown-body tr")
    expect(rows).to_have_count(5)
    
    # First 2 people
    expect(rows.nth(0).locator("td.share")).to_have_text("$2.01")
    expect(rows.nth(1).locator("td.share")).to_have_text("$2.01")
    
    # Last 3 people
    expect(rows.nth(2).locator("td.share")).to_have_text("$2.00")
    expect(rows.nth(3).locator("td.share")).to_have_text("$2.00")
    expect(rows.nth(4).locator("td.share")).to_have_text("$2.00")


def test_invalid_input_hides_results(page: Page):
    """
    Test Case 4: Invalid inputs should hide the results section.
    """
    page.goto(HTML_FILE_PATH)
    
    # Initially hidden because inputs are empty
    expect(page.locator("#results-section")).not_to_be_visible()
    
    # Enter valid inputs, should become visible
    page.fill("#bill", "10.00")
    expect(page.locator("#results-section")).to_be_visible()
    
    # Clear the bill amount, should hide again
    page.fill("#bill", "")
    expect(page.locator("#results-section")).not_to_be_visible()
