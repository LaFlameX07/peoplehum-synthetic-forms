# tests/test_global_demo_forms.py

import datetime
import csv
import pathlib
import re

import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://www.peoplehum.com"
LOG_PATH = pathlib.Path("logs/demo_runs.csv")

# Test data (same everywhere)
TEST_NAME = "Amit M Test"
TEST_EMAIL = "amit@test.com"
TEST_COMPANY = "peopleHum"
TEST_PHONE = "9876543210"


def log_run(origin_name: str, page_url: str, email: str, success: bool, message: str):
    """Append one row to the CSV log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    is_new = not LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(
                ["timestamp_utc", "origin", "page_url", "email", "success", "message"]
            )
        writer.writerow(
            [
                datetime.datetime.utcnow().isoformat(),
                origin_name,
                page_url,
                email,
                "OK" if success else "FAIL",
                message,
            ]
        )


# ---------- helpers for different flows ----------

def fill_and_submit_demo_page_form(page, dial_code: str):
    """Main /demo page (Webflow-style form with #demoName, etc.)."""
    page.wait_for_selector("#demoName", state="visible")

    page.locator("#demoName").click()
    page.locator("#demoName").fill(TEST_NAME)

    page.locator("#demoEmail").click()
    page.locator("#demoEmail").fill(TEST_EMAIL)

    page.locator("#demoCompanyName").click()
    page.locator("#demoCompanyName").fill(TEST_COMPANY)

    page.locator("#demoCountryCode").click()
    page.locator("#demoCountryCode").fill(dial_code)

    page.locator("#demoPhoneNumber").click()
    page.locator("#demoPhoneNumber").fill(TEST_PHONE)

    page.get_by_role("button", name="Schedule a demo").click()

    success_locator = page.get_by_text(
        "Thank you for scheduling a demo with us. Please check your email for further"
    )
    expect(success_locator).to_be_visible(timeout=15000)


def fill_and_submit_geo_hero_form(page):
    """Hero form on /global/<country> pages."""
    name_box = page.get_by_role("textbox", name="Name*", exact=True)
    expect(name_box).to_be_visible()

    name_box.click()
    name_box.fill(TEST_NAME)

    page.get_by_role("textbox", name="Work Email*").click()
    page.get_by_role("textbox", name="Work Email*").fill(TEST_EMAIL)

    page.get_by_role("textbox", name="Company Name*").click()
    page.get_by_role("textbox", name="Company Name*").fill(TEST_COMPANY)

    page.get_by_role("textbox", name="Contact Number").click()
    page.get_by_role("textbox", name="Contact Number").fill(TEST_PHONE)

    page.get_by_role("button", name="Schedule a demo").click()

    thank_you = page.get_by_role(
        "heading", name=re.compile(r"Thank you", re.I)
    )
    expect(thank_you).to_be_visible(timeout=15000)


def fill_and_submit_webinars_form(page, dial_code: str):
    """Webinars registration form (/webinars)."""
    page.wait_for_selector("#webinar_name", state="visible")

    page.locator("#webinar_name").click()
    page.locator("#webinar_name").fill(TEST_NAME)

    page.locator("#webinar_email").click()
    page.locator("#webinar_email").fill(TEST_EMAIL)

    page.locator("#webinar_countryCode").click()
    page.locator("#webinar_countryCode").fill(dial_code)

    page.locator("#webinar_phoneNumber").click()
    page.locator("#webinar_phoneNumber").fill(TEST_PHONE)

    page.get_by_role("button", name="Register now").click()

    success = page.get_by_role(
        "heading",
        name=re.compile(r"You.?re Registered", re.I),  # matches "You're Registered! You'll"
    )
    expect(success).to_be_visible(timeout=15000)


def fill_and_submit_phia_form(page, dial_code: str):
    """
    Phia / HR chatbot page (/hr-chatbot).
    Clicks the hero demo button, then fills the popup form.
    Logs origin as 'phia'.
    """
    # Open the popup form
    page.wait_for_selector("#demo-button-hero", state="visible")
    page.locator("#demo-button-hero").click()

    # Name / email / company use role-based selectors
    name_box = page.get_by_role("textbox", name="Name*", exact=True)
    expect(name_box).to_be_visible()

    name_box.click()
    name_box.fill(TEST_NAME)

    page.get_by_role("textbox", name="Work Email*").click()
    page.get_by_role("textbox", name="Work Email*").fill(TEST_EMAIL)

    page.get_by_role("textbox", name="Company Name*").click()
    page.get_by_role("textbox", name="Company Name*").fill(TEST_COMPANY)

    page.locator("#p_demoCountryCode").click()
    page.locator("#p_demoCountryCode").fill(dial_code)

    page.get_by_role("textbox", name="Contact Number").click()
    page.get_by_role("textbox", name="Contact Number").fill(TEST_PHONE)

    page.get_by_role("button", name="Submit").click()

    # ✅ success area uses aria-label "peopleHum_demo_request success"
    success_container = page.get_by_label("peopleHum_demo_request success")
    success_text = success_container.get_by_text(
        re.compile(r"Thank you for scheduling", re.I)
    )
    expect(success_text).to_be_visible(timeout=15000)

def fill_and_submit_partners_form(page, dial_code: str):
    """
    Partners page (/partners).
    Clicks 'Join our network', fills the partner form, asserts success.
    """
    # Start on /partners; if you're not sure, you can just call page.goto(...) here too
    page.wait_for_selector("a:has-text('Join our network')", state="visible")
    page.get_by_role("link", name="Join our network").click()

    # Form fields
    name_box = page.get_by_role("textbox", name="Name*", exact=True)
    expect(name_box).to_be_visible()

    name_box.click()
    name_box.fill(TEST_NAME)

    page.get_by_role("textbox", name="Work Email*").click()
    page.get_by_role("textbox", name="Work Email*").fill(TEST_EMAIL)

    page.get_by_role("textbox", name="Company Name*").click()
    page.get_by_role("textbox", name="Company Name*").fill(TEST_COMPANY)

    page.get_by_role("textbox", name="Comments").click()
    page.get_by_role("textbox", name="Comments").fill(
        "This is a Dummy Trial, Kindly Ignore."
    )

    page.locator("#p_partnerCountryCode").click()
    page.locator("#p_partnerCountryCode").fill(dial_code)

    page.get_by_role("textbox", name="Contact Number").click()
    page.get_by_role("textbox", name="Contact Number").fill(TEST_PHONE)

    page.get_by_role("button", name="Submit").click()

    # Success block: aria-label "ph_partner_signup success"
    success_container = page.get_by_label("ph_partner_signup success")
    success_text = success_container.get_by_text(
        re.compile(r"Thank you! Your submission", re.I)
    )
    expect(success_text).to_be_visible(timeout=15000)

def fill_and_submit_contact_form(page, dial_code: str):
    """
    Contact Us flow from the homepage:
    1) Open the About Us section
    2) Click the Contact Us tile
    3) Fill the contact form
    4) Assert the success message
    """

    # 0. Dismiss cookie banner if it appears
    try:
        page.get_by_text("ACCEPT", exact=True).click(timeout=3000)
    except Exception:
        pass

    # 1. Open the About Us section (the row with Our story / Customers / Careers / Contact Us)
    #    On most viewports, hovering OR clicking About Us in the nav reveals this.
    about_trigger = page.get_by_text("About Us", exact=False).first
    about_trigger.hover()
    page.wait_for_timeout(800)  # small delay for the section to animate in

    # 2. Click the Contact Us tile in that row
    contact_tile = page.get_by_text("Contact Us", exact=False).first
    contact_tile.click()

    # 3. Wait for the contact form to be ready (using the country code field as an anchor)
    page.wait_for_selector("#p_contactCountryCode", timeout=15000)

    # 4. Fill form fields – use the same locators as your working codegen snippet
    name_box = page.get_by_role("textbox", name="Full Name*")
    name_box.click()
    name_box.fill(TEST_NAME)

    page.get_by_role("textbox", name="Work Email*").click()
    page.get_by_role("textbox", name="Work Email*").fill(TEST_EMAIL)

    page.get_by_role("textbox", name="Message").click()
    page.get_by_role("textbox", name="Message").fill(
        "This is test run. Kindly ignore."
    )

    page.locator("#p_contactCountryCode").click()
    page.locator("#p_contactCountryCode").fill(dial_code)

    page.get_by_role("textbox", name="Contact Number").click()
    page.get_by_role("textbox", name="Contact Number").fill(TEST_PHONE)

    page.get_by_role("button", name="Submit").click()

    # 5. Verify success – matches your codegen:
    #    aria-label="peopleHum_contact_form success" + "Thank you! Your submission..."
    success_root = page.get_by_label("peopleHum_contact_form success")
    success_text = success_root.get_by_text(
        re.compile(r"Thank you! Your submission", re.I)
    )
    expect(success_text).to_be_visible(timeout=15000)

def fill_and_submit_ebook_form(page):
    """
    Ebook download page (sample: /ph-ebook/engineering-speed-in-human-work).
    """
    # Wait until the Name field is visible
    name_box = page.get_by_role("textbox", name="Name*")
    expect(name_box).to_be_visible()

    name_box.click()
    name_box.fill(TEST_NAME)

    page.get_by_role("textbox", name="Email*").click()
    page.get_by_role("textbox", name="Email*").fill(TEST_EMAIL)

    # Consent checkbox
    page.get_by_role("checkbox", name=re.compile(r"By submitting this", re.I)).check()

    # Submit
    page.get_by_role("button", name="Get it now").click()

    # Success: "Thanks for downloading!" + "Open the email from peopleHum"
    thank_you = page.get_by_role("heading", name="Thanks for downloading!")
    expect(thank_you).to_be_visible(timeout=15000)

    subtext = page.get_by_text("Open the email from peopleHum")
    expect(subtext).to_be_visible(timeout=15000)


def fill_and_submit_toolkit_form(page):
    """
    HR toolkit download page (sample: /hr-toolkit/candidate-assessment-matrix).
    """
    # Wait until Name is visible
    name_box = page.get_by_role("textbox", name="Name")
    expect(name_box).to_be_visible()

    name_box.click()
    name_box.fill(TEST_NAME)

    page.get_by_role("textbox", name="Company").click()
    page.get_by_role("textbox", name="Company").fill(TEST_COMPANY)

    page.get_by_role("textbox", name="Email Address").click()
    page.get_by_role("textbox", name="Email Address").fill(TEST_EMAIL)

    page.get_by_role("button", name="Get it now").click()

    thank_you = page.get_by_role("heading", name="Thanks for downloading!")
    expect(thank_you).to_be_visible(timeout=15000)

    subtext = page.get_by_text("Open the email from peopleHum")
    expect(subtext).to_be_visible(timeout=15000)

def fill_and_submit_pricing_form(page, dial_code: str):
    """
    Pricing page (/pricing).
    Clicks the hero demo button, fills the popup demo form, asserts success.
    """
    page.wait_for_selector("#demo-button-hero", state="visible")
    page.locator("#demo-button-hero").click()

    name_box = page.get_by_role("textbox", name="Name*", exact=True)
    expect(name_box).to_be_visible()

    name_box.click()
    name_box.fill(TEST_NAME)

    page.get_by_role("textbox", name="Work Email*").click()
    page.get_by_role("textbox", name="Work Email*").fill(TEST_EMAIL)

    page.get_by_role("textbox", name="Company Name*").click()
    page.get_by_role("textbox", name="Company Name*").fill(TEST_COMPANY)

    page.locator("#p_demoCountryCode").click()
    page.locator("#p_demoCountryCode").fill(dial_code)

    page.get_by_role("textbox", name="Contact Number").click()
    page.get_by_role("textbox", name="Contact Number").fill(TEST_PHONE)

    page.get_by_role("button", name="Submit").click()

    # success text: "Thank you for scheduling a..."
    success_text = page.get_by_text(
        re.compile(r"Thank you for scheduling a", re.I)
    )
    expect(success_text).to_be_visible(timeout=15000)

# ---------- list of all paths to test ----------

PAGES = [
    # main demo page
    {"name": "demo-main", "url": f"{BASE_URL}/demo", "dial_code": "+61", "form_type": "demo"},

    # global country hero pages
    {"name": "australia", "url": f"{BASE_URL}/global/australia", "dial_code": "+61", "form_type": "hero"},
    {"name": "bangladesh", "url": f"{BASE_URL}/global/bangladesh", "dial_code": "+880", "form_type": "hero"},
    {"name": "brazil", "url": f"{BASE_URL}/global/brazil", "dial_code": "+55", "form_type": "hero"},
    {"name": "brunei", "url": f"{BASE_URL}/global/brunei", "dial_code": "+673", "form_type": "hero"},

    {"name": "egypt", "url": f"{BASE_URL}/global/egypt", "dial_code": "+20", "form_type": "hero"},
    {"name": "fiji", "url": f"{BASE_URL}/global/fiji", "dial_code": "+679", "form_type": "hero"},
    {"name": "ghana", "url": f"{BASE_URL}/global/ghana", "dial_code": "+233", "form_type": "hero"},
    {"name": "india", "url": f"{BASE_URL}/global/india", "dial_code": "+91", "form_type": "hero"},

    {"name": "indonesia", "url": f"{BASE_URL}/global/indonesia", "dial_code": "+62", "form_type": "hero"},
    {"name": "kenya", "url": f"{BASE_URL}/global/kenya", "dial_code": "+254", "form_type": "hero"},
    {"name": "lebanon", "url": f"{BASE_URL}/global/lebanon", "dial_code": "+961", "form_type": "hero"},
    {"name": "libya", "url": f"{BASE_URL}/global/libya", "dial_code": "+218", "form_type": "hero"},

    {"name": "malaysia", "url": f"{BASE_URL}/global/malaysia", "dial_code": "+60", "form_type": "hero"},
    {"name": "maldives", "url": f"{BASE_URL}/global/maldives", "dial_code": "+960", "form_type": "hero"},
    {"name": "mexico", "url": f"{BASE_URL}/global/mexico", "dial_code": "+52", "form_type": "hero"},
    {"name": "nigeria", "url": f"{BASE_URL}/global/nigeria", "dial_code": "+234", "form_type": "hero"},

    {"name": "philippines", "url": f"{BASE_URL}/global/philippines", "dial_code": "+63", "form_type": "hero"},
    {"name": "saudi-arabia", "url": f"{BASE_URL}/global/saudi-arabia", "dial_code": "+966", "form_type": "hero"},
    {"name": "singapore", "url": f"{BASE_URL}/global/singapore", "dial_code": "+65", "form_type": "hero"},
    {"name": "south-africa", "url": f"{BASE_URL}/global/south-africa", "dial_code": "+27", "form_type": "hero"},

    {"name": "sri-lanka", "url": f"{BASE_URL}/global/sri-lanka", "dial_code": "+94", "form_type": "hero"},
    {"name": "thailand", "url": f"{BASE_URL}/global/thailand", "dial_code": "+66", "form_type": "hero"},
    {"name": "turkey", "url": f"{BASE_URL}/global/turkey", "dial_code": "+90", "form_type": "hero"},
    {"name": "uae", "url": f"{BASE_URL}/global/uae", "dial_code": "+971", "form_type": "hero"},

    {"name": "usa", "url": f"{BASE_URL}/global/usa", "dial_code": "+1", "form_type": "hero"},
    {"name": "united-kingdom", "url": f"{BASE_URL}/global/united-kingdom", "dial_code": "+44", "form_type": "hero"},
    {"name": "zambia", "url": f"{BASE_URL}/global/zambia", "dial_code": "+260", "form_type": "hero"},
    {"name": "zimbabwe", "url": f"{BASE_URL}/global/zimbabwe", "dial_code": "+263", "form_type": "hero"},

    # webinars flow (logs as "webinars")
    {"name": "webinars", "url": f"{BASE_URL}/webinars", "dial_code": "+975", "form_type": "webinars"},
    # Partners
    {"name": "partners", "url": f"{BASE_URL}/partners", "dial_code": "+994", "form_type": "partners"},

    # Contact – start from homepage, then click Contact link inside helper
    {"name": "contact", "url": f"{BASE_URL}/#", "dial_code": "+1-264", "form_type": "contact"},
    
    {
        "name": "ebook-engineering-speed",
        "url": f"{BASE_URL}/ph-ebook/engineering-speed-in-human-work",
        "dial_code": "",
        "form_type": "ebook",
    },

    # HR Toolkit sample
    {
        "name": "toolkit-candidate-assessment",
        "url": f"{BASE_URL}/hr-toolkit/candidate-assessment-matrix",
        "dial_code": "",
        "form_type": "toolkit",
    },
    {
        "name": "pricing",
        "url": f"{BASE_URL}/pricing",
        "dial_code": "+673",
        "form_type": "pricing",
    },
    # Phia / HR chatbot flow (logs as "phia")
    {"name": "phia", "url": f"{BASE_URL}/hr-chatbot", "dial_code": "+374", "form_type": "phia"},
]

@pytest.mark.parametrize("cfg", PAGES, ids=lambda c: c["name"])
def test_all_key_forms(cfg):
    """Run synthetic form checks for demo, global geos, webinars, and Phia."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(60000)

        page.goto(cfg["url"])

        try:
            if cfg["form_type"] == "demo":
                fill_and_submit_demo_page_form(page, cfg["dial_code"])
            elif cfg["form_type"] == "hero":
                fill_and_submit_geo_hero_form(page)
            elif cfg["form_type"] == "webinars":
                fill_and_submit_webinars_form(page, cfg["dial_code"])
            elif cfg["form_type"] == "phia":
                fill_and_submit_phia_form(page, cfg["dial_code"])
            elif cfg["form_type"] == "partners":
                fill_and_submit_partners_form(page, cfg["dial_code"])
            elif cfg["form_type"] == "contact":
                fill_and_submit_contact_form(page, cfg["dial_code"])
            elif cfg["form_type"] == "ebook":
                fill_and_submit_ebook_form(page)
            elif cfg["form_type"] == "toolkit":
                fill_and_submit_toolkit_form(page)
            elif cfg["form_type"] == "pricing":
                fill_and_submit_pricing_form(page, cfg["dial_code"])
            else:
                raise ValueError(f"Unknown form_type: {cfg['form_type']}")

            log_run(cfg["name"], cfg["url"], TEST_EMAIL, True, "Success message displayed")
        except Exception as e:
            log_run(cfg["name"], cfg["url"], TEST_EMAIL, False, repr(e))
            raise
        finally:
            context.close()
            browser.close()