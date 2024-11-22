# get_links_trackers.py
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys




def get_links_and_trackers(query, driver):
    """
    Fetch normal URLs and AI Overview URLs from a Google search using the provided WebDriver.
    Scrolls to the bottom of each URL to ensure full content is loaded.

    :param query: Search query string.
    :param driver: Selenium WebDriver instance to use for the search.
    :return: A tuple of two lists: (normal_urls, ai_urls).
    """
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
    ai_overview_section = None
    ai_urls = []
    try:
        ai_overview_section = driver.find_element(By.XPATH, "//div[contains(@class, 'fx92l')]")
        ai_overview_links = ai_overview_section.find_elements(By.XPATH, ".//a[@class='KEVENd']")
        ai_urls = [link.get_attribute("href") for link in ai_overview_links if link.is_displayed()]
    except Exception as e:
        print(f"Error locating AI overview links: {e}")

    # Scroll to the bottom of each URL to ensure all content loads
    for url_list in [normal_urls, ai_urls]:
        for url in url_list:
            try:
                driver.get(url)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Allow time for content to load
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
            except Exception as e:
                print(f"Error scrolling URL {url}: {e}")

    return normal_urls, ai_urls

# Test the function
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # Set up ChromeDriver
    driver_path = '/usr/local/bin/chromedriver'  # Update if necessary
    service = Service(driver_path)
    options = Options()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        test_query = "stroke symptoms"
        normal_urls, ai_overview_urls = get_links_and_trackers(test_query, driver)

        print("Normal Links:")
        for i, url in enumerate(normal_urls, 1):
            print(f"{i}: {url}")

        print("\nAI Overview Links:")
        for i, url in enumerate(ai_overview_urls, 1):
            print(f"{i}: {url}")
    finally:
        driver.quit()