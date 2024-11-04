from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# Set up Chrome options and add a User-Agent string
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

# Path to chromedriver
driver_path = '/usr/local/bin/chromedriver'  # Ensure this path is correct
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

search_queries = ["flu symptoms", "cancer symptoms", "stroke symptoms"]

for query in search_queries:
    driver.get('https://www.google.com')

    # Input the search query and submit
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    # Wait for search results to load
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//h3/ancestor::a")))

    # Collect the first 3 normal search result links in the order they appear
    normal_links = driver.find_elements(By.XPATH, "(//h3/ancestor::a)[position() <= 3]")
    normal_urls = [link.get_attribute('href') for link in normal_links]

    # Collect the first 3 AI overview links if present
    try:
        ai_overview_elements = driver.find_elements(By.XPATH, "(//li[contains(@class, 'LLtSOc')]//a[contains(@class, 'KEVENd')])[position() <= 3]")
        ai_overview_urls = [element.get_attribute('href') for element in ai_overview_elements]
    except:
        ai_overview_urls = []

    # Print results
    print(f"\nSearch results for '{query}':")
    print("Normal Links:")
    for i, url in enumerate(normal_urls, 1):
        print(f"{i}: {url}")

    print("AI Overview Links:")
    for i, url in enumerate(ai_overview_urls, 1):
        print(f"{i}: {url}")

# Close the driver
driver.quit()
