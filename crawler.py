import asyncio
import time
import subprocess
import os
import sys
import pyautogui
import pandas as pd

# =============================================================================
# Configuration for the separate Chrome instance
# =============================================================================
# Path to your Chrome executable (adjust as needed).
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Use a temporary folder for this browser instance's user data.
temp_user_data_dir = r"C:\temp\my_temp_chrome_profile"
os.makedirs(temp_user_data_dir, exist_ok=True)

# Use a dedicated remote debugging port (different from your default, if any).
remote_debugging_port = 9223

# The target URL to open.
URL = "https://gmgn.ai/new-pair?chain=sol"

# =============================================================================
# Part 1: Launch a separate Chrome instance and perform PyAutoGUI automation
# =============================================================================

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

def launch_separate_browser():
    """
    Launches an entirely separate Chrome instance using the specified
    executable, temporary user data directory, remote debugging port, and target URL.
    """
    args = [
        chrome_path,
        f"--remote-debugging-port={remote_debugging_port}",
        f"--user-data-dir={temp_user_data_dir}",
        URL  # Open the target URL immediately.
    ]
    # Launch Chrome without waiting for it to exit.
    subprocess.Popen(args)
    print(f"Launched separate Chrome instance with remote debugging on port {remote_debugging_port}.")

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
    Perform a series of PyAutoGUI actions on the opened browser window.
    The original commented-out steps are retained.
    """
    print("Opening the website. Please do not use the mouse during automation.")
    # Allow time for the browser and page to load.
    time.sleep(5)

    # --- Step 1: Close the pop-up ---
    if not wait_and_click(IMAGES["close"], "pop-up close button"):
        print("Error: Unable to close the pop-up. Exiting automation.")
        return False

    time.sleep(0.2)
    
    # The following steps are commented out but kept for reference.
    # # --- Step 2: Deselect the Pump filter ---
    # if not wait_and_click(IMAGES["pump"], "Pump filter (to deselect)"):
    #     print("Warning: Could not find Pump filter. It might already be deselected.")
    # time.sleep(0.2)
    # 
    # # --- Step 3: Deselect the Moonshot filter ---
    # if not wait_and_click(IMAGES["moonshot"], "Moonshot filter (to deselect)"):
    #     print("Warning: Could not find Moonshot filter. It might already be deselected.")
    # time.sleep(0.2)
    # 
    # # --- Step 4: Click the filter button on the left beside the New Pool ---
    # if not wait_and_click(IMAGES["filter"], "Filter button on the left"):
    #     print("Error: Unable to click the filter button.")
    #     return False
    # time.sleep(0.5)
    # 
    # # --- Step 5: Select the 'with only 1 socials' filter option ---
    # if not wait_and_click(IMAGES["socials"], "'with only 1 socials' filter option"):
    #     print("Error: Unable to select the 'with only 1 socials' filter option.")
    #     return False
    # time.sleep(0.2)
    # 
    # # --- Step 6: Click the Apply button ---
    # if not wait_and_click(IMAGES["apply"], "Apply button"):
    #     print("Error: Unable to click the Apply button.")
    #     return False

    print("PyAutoGUI automation steps completed.")
    time.sleep(1)  # Keep the browser open for observation (adjust if needed)
    return True

# =============================================================================
# Part 2: Asynchronous Web Crawler Using Playwright (After PyAutoGUI actions)
# =============================================================================

# In this part, we connect to the separate Chrome instance using the specified remote debugging port.
SCRAPE_URL = URL  # Use the same target URL.

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
    Connect to the separate Chrome instance (with remote debugging enabled)
    and reuse the already open page.
    """
    from playwright.async_api import async_playwright

    p = await async_playwright().start()
    try:
        # Connect to Chrome running with remote debugging on our dedicated port.
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{remote_debugging_port}")
    except Exception as e:
        print("Error connecting via CDP. Make sure Chrome is running with remote debugging enabled on the specified port.")
        await p.stop()
        return

    # Use the existing browser context.
    context = browser.contexts[0] if browser.contexts else None
    if not context:
        print("No browser context found. Exiting.")
        await p.stop()
        return

    # Poll for up to 30 seconds to find an open page.
    page = None
    timeout = 30  # seconds
    start = time.time()
    while time.time() - start < timeout:
        pages = context.pages
        if pages:
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
        try:
            await page.goto(SCRAPE_URL, wait_until="networkidle")
        except Exception as nav_err:
            print(f"Navigation error: {nav_err}")
            try:
                await page.reload(wait_until="networkidle")
            except Exception as reload_err:
                print(f"Reload error: {reload_err}")
                await p.stop()
                return
        print("Navigation complete.")

    print("Starting to scrape from the target page...")
    # Repeatedly scrape the content from the page every 5 seconds.
    while True:
        try:
            text = await page.inner_text("body")
            display_box({"Page Content": text})
        except Exception as scrape_err:
            print(f"Scraping error: {scrape_err}")
        await asyncio.sleep(5)

    await p.stop()

# =============================================================================
# Stdout Tee Setup: Redirect prints to both terminal and file
# =============================================================================

class Tee:
    """
    A simple class to redirect stdout to multiple file-like objects.
    """
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

def setup_stdout_tee(log_file_path):
    # Ensure the directory for the log file exists.
    log_dir = os.path.dirname(log_file_path)
    os.makedirs(log_dir, exist_ok=True)
    # Open the log file in append mode.
    log_file = open(log_file_path, "a", encoding="utf-8")
    # Create a tee for stdout.
    sys.stdout = Tee(sys.stdout, log_file)

# =============================================================================
# Main Integration
# =============================================================================

def main():
    # Setup stdout tee to print to terminal and continuously update the file.
    setup_stdout_tee("./data/data.txt")
    
    # Step 1: Launch a separate Chrome instance.
    launch_separate_browser()
    
    # Step 2: Run the PyAutoGUI automation to interact with the browser.
    if not run_pyautogui_automation():
        print("Automation did not complete successfully. Exiting.")
        return

    # Step 3: Start the asynchronous web crawler.
    print("Starting asynchronous scraping...")
    try:
        asyncio.run(fetch_scrape_data())
    except Exception as e:
        print(f"An error occurred during asynchronous scraping: {e}")

if __name__ == "__main__":
    main()
