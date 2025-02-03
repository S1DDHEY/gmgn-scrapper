import pyautogui
import time
import webbrowser

# --- Configuration ---
URL = "https://gmgn.ai/new-pair?chain=sol"
# File names for the reference images (make sure these files exist)
IMAGES = {
    "close": "./images/close_button.png",
    "raydium": "./images/raydium.png",
    "pump": "./images/pump.png",
    "moonshot": "./images/moonshot.png",
    "socials": "./images/socials.png"
}
# Confidence level for image matching (requires OpenCV)
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
    location = None
    while time.time() - start_time < timeout:
        location = pyautogui.locateOnScreen(image_file, confidence=CONFIDENCE)
        if location:
            center = pyautogui.center(location)
            pyautogui.moveTo(center.x, center.y, duration=0.25)
            pyautogui.click()
            print(f"Clicked on {description}.")
            return True
        time.sleep(5)
    print(f"Timeout: Could not find {description}.")
    return False

def main():
    # Open the URL in your default web browser.
    webbrowser.open(URL)
    
    # Allow time for the browser and page to load.
    print("Opening the website. Please do not use the mouse during automation.")
    time.sleep(7)  # Adjust as necessary
    
    # --- Step 1: Close the pop-up ---
    if not wait_and_click(IMAGES["close"], "pop-up close button"):
        print("Error: Unable to close the pop-up. Exiting script.")
        return
    
    time.sleep(5)  # Wait briefly after closing the pop-up
    
    # --- Step 2: Click on the Raydium filter ---
    if not wait_and_click(IMAGES["raydium"], "Raydium filter"):
        print("Error: Unable to click the Raydium filter.")
    
    time.sleep(5)
    
    # --- Step 3: Deselect the Pump filter ---
    if not wait_and_click(IMAGES["pump"], "Pump filter (to deselect)"):
        print("Warning: Could not find Pump filter. It might already be deselected.")
    
    time.sleep(5)
    
    # --- Step 4: Deselect the Moonshot filter ---
    if not wait_and_click(IMAGES["moonshot"], "Moonshot filter (to deselect)"):
        print("Warning: Could not find Moonshot filter. It might already be deselected.")
    
    time.sleep(5)
    
    # --- Step 5: Click on the 'with at least 1 socials' filter under New Pool ---
    if not wait_and_click(IMAGES["socials"], "'with at least 1 socials' filter"):
        print("Error: Unable to click the 'with at least 1 socials' filter.")
    
    # Optionally, keep the browser open for observation.
    print("Automation steps completed.")
    time.sleep(10)

if __name__ == "__main__":
    main()
