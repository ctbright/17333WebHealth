from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse
import time
import json
from whotracksme.data.loader import DataSource


data = DataSource(data_root=data_path)

def get_tracker_info_from_data(domain):
    """
    Fetch tracker information from local WhoTracks.Me dataset for a given domain.
    """
    tracker_info = data.trackers.get(domain)
    if tracker_info:
        return {
            "name": tracker_info.get("name"),
            "owner": tracker_info.get("owner", {}).get("name"),
            "category": tracker_info.get("category"),
            "prevalence": tracker_info.get("prevalence")
        }
    else:
        print(f"No data found for tracker: {domain}")
        return None

# Set up Chrome options and enable basic performance logging
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})  # Enable network logging

# Path to ChromeDriver
driver_path = '/usr/local/bin/chromedriver'  # Update if necessary
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

search_queries = ["cancer symptoms"]

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

    # Print results
    print(f"\nSearch results for '{query}':")
    print("Normal Links:")
    for i, url in enumerate(normal_urls, 1):
        print(f"{i}: {url}")

    # Visit each URL and capture tracking requests
    for url in normal_urls[:1]:  # Limit to first URL for testing
        print(f"\nNow Analyzing URL for trackers: {url}")
        driver.get(url)

        # Wait for a few seconds to allow page loading and tracker requests
        time.sleep(3)

        # Collect performance logs and filter third-party requests
        logs = driver.get_log("performance")
        third_party_domains = set()

        # Define non-tracking resource types and patterns to filter out
        excluded_extensions = (".png", ".jpg", ".jpeg", ".gif", ".css", ".svg", ".woff", ".woff2", ".ttf")
        tracking_resource_types = ["Script", "XHR", "Fetch"]

        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if log["method"] == "Network.requestWillBeSent":
                request_url = log["params"]["request"]["url"]
                resource_type = log["params"].get("type", "Unknown")

                # Filter based on URL and resource type
                if (request_url and url not in request_url and  # Third-party request
                    not request_url.lower().endswith(excluded_extensions) and  # Exclude images/styles
                    resource_type in tracking_resource_types):  # Only tracking resource types

                    # Extract the domain name from the URL
                    domain = urlparse(request_url).netloc
                    # Simplify the domain to only the last two segments (e.g., googleapis.com)
                    simplified_domain = '.'.join(domain.split('.')[-2:])
                    third_party_domains.add(simplified_domain)

        # Print detailed information for the first identified tracker
        if third_party_domains:
            first_tracker = list(third_party_domains)[0]
            print(f"\nFirst Tracker Domain: {first_tracker}")
            tracker_info = get_tracker_info_from_data(first_tracker)
            if tracker_info:
                print("Tracker Information:")
                print(f"Name: {tracker_info['name']}")
                print(f"Company: {tracker_info['owner']}")
                print(f"Category: {tracker_info['category']}")
                print(f"Prevalence: {tracker_info['prevalence']}")
        else:
            print("No third-party trackers found on this page.")

# Close the driver
driver.quit()
