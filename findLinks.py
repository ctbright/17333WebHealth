# get_links_trackers.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def get_links_and_trackers(query):
    # Set up Chrome options and enable basic performance logging
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    # Path to ChromeDriver
    driver_path = '/usr/local/bin/chromedriver'  # Update if necessary
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get('https://www.google.com')
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    # Wait for search results
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//h3/ancestor::a")))
    normal_links = driver.find_elements(By.XPATH, "(//h3/ancestor::a)[position() <= 3]")
    ai_overview_elements = driver.find_elements(By.XPATH, "(//li[contains(@class, 'LLtSOc')]//a[contains(@class, 'KEVENd')])[position() <= 3]")
    
    normal_urls = [link.get_attribute('href') for link in normal_links]
    ai_overview_urls = [element.get_attribute('href') for element in ai_overview_elements]
    
    driver.quit()
    
    return normal_urls, ai_overview_urls
