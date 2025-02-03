from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service  # Import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup the Chrome driver using the Service class
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open the target URL
driver.get("https://gmgn.ai/new-pair?chain=sol")

# Wait for the page to load (adjust timeout as needed)
wait = WebDriverWait(driver, 15)

try:
    # -------------------------------
    # 1. Select only "Raydium"
    # -------------------------------
    # Wait for the Raydium filter element to be clickable.
    raydium_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[contains(text(), 'Raydium')]")
    ))
    raydium_button.click()
    print("Clicked Raydium filter.")

    # -------------------------------
    # 2. Deselect "pump" and "moonshot" filters if they are selected.
    # -------------------------------
    # Find the pump filter element (adjust XPath as needed)
    pump_filter = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[contains(text(), 'pump')]")
    ))
    pump_filter.click()
    print("Deselected pump filter.")

    # Find the moonshot filter element (adjust XPath as needed)
    moonshot_filter = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[contains(text(), 'moonshot')]")
    ))
    moonshot_filter.click()
    print("Deselected moonshot filter.")

    # -------------------------------
    # 3. Under the New Pool section, select the filter "with at least 1 socials"
    # -------------------------------
    socials_filter = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[contains(text(), 'with at least 1 socials')]")
    ))
    socials_filter.click()
    print("Selected 'with at least 1 socials' filter.")

    # Pause to observe changes (adjust as necessary)
    time.sleep(10)

except Exception as e:
    print("An error occurred:", e)
finally:
    # Close the browser
    driver.quit()
