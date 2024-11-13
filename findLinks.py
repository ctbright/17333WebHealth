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
from collections import defaultdict

# Initialize data source
data = DataSource()

def get_tracker_id_from_url(url):
    """
    Retrieve the tracker ID associated with a given URL's domain.
    """
    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]  # Remove 'www.' for matching
    
    query = "SELECT tracker FROM tracker_domains WHERE domain LIKE ?"
    result = data.db.connection.execute(query, ('%' + domain + '%',)).fetchone()
    
    return result[0] if result else None

def get_tracker_info_from_data(domain):
    """
    Fetch tracker information from WhoTracks.Me dataset for a given domain.
    """
    tracker_id = get_tracker_id_from_url(domain)
    if tracker_id:
        tracker_info = data.trackers.get_tracker(tracker_id)
        if tracker_info:
            return {
                "name": tracker_info.get("name"),
                "category": tracker_info.get("category"),
            }
    return None

# Set up Chrome options and enable basic performance logging
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})  # Enable network logging

# Path to ChromeDriver
driver_path = '/usr/local/bin/chromedriver'  # Update if necessary
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Dictionary to hold tracker counts by category for each URL type
tracker_counts_total = defaultdict(int)

# Sample search query
search_queries = ["cancer symptoms"]

for query in search_queries:
    driver.get('https://www.google.com')

    # Input the search query and submit
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    # Wait for search results to load
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//h3/ancestor::a")))

    # Collect normal and AI overview links
    normal_links = driver.find_elements(By.XPATH, "(//h3/ancestor::a)[position() <= 3]")
    ai_overview_elements = driver.find_elements(By.XPATH, "(//li[contains(@class, 'LLtSOc')]//a[contains(@class, 'KEVENd')])[position() <= 3]")
    normal_urls = [link.get_attribute('href') for link in normal_links]
    ai_overview_urls = [element.get_attribute('href') for element in ai_overview_elements]

    # Print out categories
    print(f"\nSearch results for '{query}':")
    print("Normal Links:")
    for i, url in enumerate(normal_urls, 1):
        print(f"{i}: {url}")
        
    print("AI Overview Links:")
    for i, url in enumerate(ai_overview_urls, 1):
        print(f"{i}: {url}")

    # Analyze trackers for each URL
    url_types = {
        "Normal": normal_urls,
        "AI Overview": ai_overview_urls
    }

    for url_type, urls in url_types.items():
        print(f"\nAnalyzing {url_type} URLs for trackers:\n")
        
        for url in urls:
            print(f"\nNow Analyzing URL: {url}")
            driver.get(url)
            time.sleep(3)  # Allow time for loading
            
            # Dictionary to hold tracker counts by category for the current URL
            tracker_counts = defaultdict(int)

            # Collect performance logs and filter third-party requests
            logs = driver.get_log("performance")
            third_party_domains = set()
            excluded_extensions = (".png", ".jpg", ".jpeg", ".gif", ".css", ".svg", ".woff", ".woff2", ".ttf")
            tracking_resource_types = ["Script", "XHR", "Fetch"]

            for entry in logs:
                log = json.loads(entry["message"])["message"]
                if log["method"] == "Network.requestWillBeSent":
                    request_url = log["params"]["request"]["url"]
                    resource_type = log["params"].get("type", "Unknown")

                    if (request_url and url not in request_url and
                        not request_url.lower().endswith(excluded_extensions) and
                        resource_type in tracking_resource_types):
                        domain = urlparse(request_url).netloc
                        simplified_domain = '.'.join(domain.split('.')[-2:])
                        third_party_domains.add(simplified_domain)

            # Process each tracker domain and update counts
            for domain in third_party_domains:
                tracker_info = get_tracker_info_from_data(domain)
                if tracker_info:
                    category = tracker_info["category"]
                    tracker_counts[category] += 1
                    tracker_counts_total[category] += 1  # Also add to total counts across all URLs

            # Print the tracker count for each category for the current URL
            print(f"\nTracker Categories for URL {url}:")
            for category, count in tracker_counts.items():
                print(f"{category}: {count}")

# Print total tracker counts across all URLs
print("\nTotal Tracker Counts Across All URLs:")
for category, count in tracker_counts_total.items():
    print(f"{category}: {count}")

# Close the driver
driver.quit()
