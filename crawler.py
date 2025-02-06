import asyncio
import time
import webbrowser
import pyautogui
import pandas as pd

# =============================================================================
# Part 1: PyAutoGUI Automation to Open and Manipulate the Page
# =============================================================================

# --- Configuration for PyAutoGUI ---
URL = "https://gmgn.ai/new-pair?chain=sol"  # Target URL to open in your browser

# File names for the reference images (ensure these files exist at the given path)
IMAGES = {
    "close": "./images/close_button.png",
    "pump": "./images/pump.png",
    "moonshot": "./images/moonshot.png",
    "filter": "./images/filter_button.png",
    "socials": "./images/socials.png",  # represents "with only 1 socials" option
    "apply": "./images/apply.png"
}

# Confidence level for image matching (requires OpenCV installed)
CONFIDENCE = 0.8

def wait_and_click(image_file, description, timeout=30):
    """
    Wait until an image appears on the screen, then click its center.
    :param image_file: Filename of the image to locate.
    :param description: Text description (for logging).
    :param timeout: Maximum time (in seconds) to wait.
    :return: True if clicked successfully, False if timed out.
    """
    print(f"Waiting for {description}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        location = pyautogui.locateOnScreen(image_file, confidence=CONFIDENCE)
        if location:
            center = pyautogui.center(location)
            pyautogui.moveTo(center.x, center.y, duration=0.25)
            pyautogui.click()
            print(f"Clicked on {description}.")
            return True
        time.sleep(1)
    print(f"Timeout: Could not find {description}.")
    return False

def run_pyautogui_automation():
    """
    Open the target URL in the default web browser and run a series of clicks
    to adjust the filters as needed.
    """
    # Open the URL in your default web browser.
    webbrowser.open(URL)
    print("Opening the website. Please do not use the mouse during automation.")
    time.sleep(3)  # Allow time for the browser and page to load

    # --- Step 1: Close the pop-up ---
    if not wait_and_click(IMAGES["close"], "pop-up close button"):
        print("Error: Unable to close the pop-up. Exiting automation.")
        return False

    # (Optional additional steps are commented out.)
    # time.sleep(0.1)
    # if not wait_and_click(IMAGES["pump"], "Pump filter (to deselect)"):
    #     print("Warning: Could not find Pump filter. It might already be deselected.")
    # time.sleep(0.1)
    # if not wait_and_click(IMAGES["moonshot"], "Moonshot filter (to deselect)"):
    #     print("Warning: Could not find Moonshot filter. It might already be deselected.")
    # time.sleep(0.1)
    # if not wait_and_click(IMAGES["filter"], "Filter button on the left"):
    #     print("Error: Unable to click the filter button.")
    #     return False
    # time.sleep(0.1)
    # if not wait_and_click(IMAGES["socials"], "'with only 1 socials' filter option"):
    #     print("Error: Unable to select the 'with only 1 socials' filter option.")
    #     return False
    # time.sleep(0.1)
    # if not wait_and_click(IMAGES["apply"], "Apply button"):
    #     print("Error: Unable to click the Apply button.")
    #     return False

    print("PyAutoGUI automation steps completed.")
    time.sleep(1)  # Keep the browser open for observation (adjust if needed)
    return True

# =============================================================================
# Part 2: Asynchronous Scraping Using Playwright via CDP (Reusing the Opened Page)
# =============================================================================

# The target URL we expect to scrape.
SCRAPE_URL = "https://gmgn.ai/new-pair?chain=sol"

def display_box(data):
    """Display the provided data inside a decorative box."""
    box_width = max(len(f"{k}: {v}") for k, v in data.items()) + 4
    print("\n" + "═" * box_width)
    print(f"║ 📊 Scraped Data ║")
    print("═" * box_width)
    for key, value in data.items():
        line = f"║ {key}: {value} "
        print(line.ljust(box_width - 1) + "║")
    print("═" * box_width + "\n")

async def fetch_scrape_data():
    """
    Connect to the already running Chrome instance (with remote debugging enabled)
    and reuse the page that was opened by PyAutoGUI. If the page's URL is not our target,
    force it to navigate to the target URL.
    """
    from playwright.async_api import async_playwright

    p = await async_playwright().start()
    try:
        # Connect to Chrome running with remote debugging on port 9222.
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
    except Exception as e:
        print("Error connecting via CDP. Make sure Chrome is running with remote debugging enabled on port 9222.")
        await p.stop()
        return

    # Use the existing browser context.
    context = browser.contexts[0] if browser.contexts else None
    if not context:
        print("No browser context found. Exiting.")
        await p.stop()
        return

    # Poll for up to 30 seconds to find any open page.
    page = None
    timeout = 30  # seconds
    start = time.time()
    while time.time() - start < timeout:
        pages = context.pages
        if pages:
            # Debug: print the URLs of all pages.
            for pg in pages:
                print("Found page URL:", pg.url)
            # Try to find a page with the target URL.
            for pg in pages:
                if SCRAPE_URL in pg.url:
                    page = pg
                    break
            # If none of the pages match, use the first available page.
            if not page:
                page = pages[0]
                print("Using the first available page, which is not the target URL.")
            break
        print("No pages found yet; waiting for a page to open...")
        await asyncio.sleep(1)

    if not page:
        print("No page was found in the browser context. Exiting.")
        await p.stop()
        return

    # If the found page does not have the target URL, force navigation.
    if SCRAPE_URL not in page.url:
        print(f"Current page URL is '{page.url}'. Navigating to the target URL...")
        await page.goto(SCRAPE_URL)
        await page.wait_for_load_state("networkidle")
        print("Navigation complete.")

    print("Starting to scrape from the target page...")
    # Repeatedly scrape the content from the (now correct) page.
    while True:
        # Get the inner text of the page body.
        text = await page.inner_text("body")
        # Display the scraped content in a decorative box.
        display_box({"Page Content": text})
        await asyncio.sleep(0.25)  # Adjust the interval as desired

    # Cleanup (unreachable because of the infinite loop)
    await p.stop()

# =============================================================================
# Main Integration
# =============================================================================

def main():
    # Step 1: Run the PyAutoGUI automation to open the page.
    # Make sure that Chrome is launched with remote debugging enabled.
    automation_success = run_pyautogui_automation()
    if not automation_success:
        print("Automation did not complete successfully. Exiting.")
        return

    # Step 2: Start the asynchronous scraping process, reusing the open Chrome tab.
    print("Starting asynchronous scraping...")
    try:
        asyncio.run(fetch_scrape_data())
    except Exception as e:
        print(f"An error occurred during asynchronous scraping: {e}")

if __name__ == "__main__":
    main()
