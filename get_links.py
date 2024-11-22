# get_link.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def get_links(query):
    """
    Fetch normal URLs and AI Overview URLs from a Google search using a self-contained WebDriver.

    :param query: Search query string.
    :return: A tuple of two lists: (normal_urls, ai_urls).
    """
    # Set up ChromeDriver
    driver_path = '/usr/local/bin/chromedriver'  # Update if necessary
    service = Service(driver_path)
    options = Options()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Open Google and perform search
        driver.get("https://www.google.com")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a")))

        # Extract normal search results (top 3)
        normal_links = driver.find_elements(By.XPATH, "(//h3/ancestor::a)[position() <= 3]")
        normal_urls = [link.get_attribute("href") for link in normal_links]

        # Extract AI overview links
        ai_urls = []
        try:
            # Main container for AI overview
            ai_overview_section = driver.find_element(By.XPATH, "//div[contains(@class, 'fx92l')]")
            # Extract visible links
            ai_overview_links = ai_overview_section.find_elements(By.XPATH, ".//a[@class='KEVENd']")
            ai_urls = [link.get_attribute("href") for link in ai_overview_links if link.is_displayed()]
        except Exception as e:
            print(f"Error locating AI overview links: {e}")

    finally:
        # Always quit the driver to release resources
        driver.quit()

    return normal_urls, ai_urls


# Test the function
if __name__ == "__main__":
    test_query = "stroke symptoms"
    normal_urls, ai_overview_urls = get_links(test_query)

    print("Normal Links:")
    for i, url in enumerate(normal_urls, 1):
        print(f"{i}: {url}")

    print("\nAI Overview Links:")
    for i, url in enumerate(ai_overview_urls, 1):
        print(f"{i}: {url}")
