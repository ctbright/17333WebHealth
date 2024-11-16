# get_links_trackers.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def get_links_and_trackers(query):
    # Set up Chrome options


    # Path to ChromeDriver
    driver_path = '/usr/local/bin/chromedriver'  # Update if necessary
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

    # Open Google and perform search
    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    # Wait for search results
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a")))

    # Extract normal search results (top 3)
    normal_links = driver.find_elements(By.XPATH, "(//h3/ancestor::a)[position() <= 3]")
    normal_urls = [link.get_attribute("href") for link in normal_links]

    # Extract AI overview links
    ai_overview_section = None  # Initialize variable
    ai_urls = []
    try:
        # Main container for AI overview
        ai_overview_section = driver.find_element(By.XPATH, "//div[contains(@class, 'fx92l')]")
        # Extract visible links
        ai_overview_links = ai_overview_section.find_elements(By.XPATH, ".//a[@class='KEVENd']")
        ai_urls = [link.get_attribute("href") for link in ai_overview_links if link.is_displayed()]
    except Exception as e:
        print(f"Error locating AI overview links: {e}")

    # Debugging: Log elements if no links are found
    if not ai_urls and ai_overview_section:
        print("AI Overview Section HTML:")
        try:
            print(ai_overview_section.get_attribute("outerHTML"))
        except Exception as e:
            print(f"Could not fetch AI overview section HTML: {e}")

    driver.quit()
    return normal_urls, ai_urls


# Test the function
if __name__ == "__main__":
    test_query = "flu symptoms"
    normal_urls, ai_overview_urls = get_links_and_trackers(test_query)

    print("Normal Links:")
    for i, url in enumerate(normal_urls, 1):
        print(f"{i}: {url}")

    print("\nAI Overview Links:")
    for i, url in enumerate(ai_overview_urls, 1):
        print(f"{i}: {url}")