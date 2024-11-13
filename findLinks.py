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

def get_tracker_id_from_domain(domain):
    """
    Retrieve the tracker ID associated with a given domain.
    """
    if domain.startswith("www."):
        domain = domain[4:]

    # Query using LIKE for partial matching
    query = "SELECT tracker FROM tracker_domains WHERE domain LIKE ?"
    result = data.db.connection.execute(query, ('%' + domain + '%',)).fetchone()

    return result[0] if result else None

def get_tracker_info_from_data(domain):
    """
    Fetch tracker information from WhoTracks.Me dataset for a given domain.
    """
    tracker_id = get_tracker_id_from_domain(domain)
    if tracker_id:
        tracker_info = data.trackers.get_tracker(tracker_id)
        if tracker_info:
            return tracker_info.get("category")
    return None

# Set up Chrome options and enable basic performance logging
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Path to ChromeDriver
driver_path = '/usr/local/bin/chromedriver'  # Update if necessary
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Sample search query
search_queries = ["flu symptoms", "cancer symptoms", "stroke symptoms"]

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

    # Initialize dictionaries for storing tracker data
    tracker_counts_by_category_normal = defaultdict(int)
    tracker_counts_by_category_ai = defaultdict(int)
    total_trackers_normal = 0
    total_trackers_ai = 0

    # Analyze trackers for each URL type
    url_types = {
        "Normal": (normal_urls, tracker_counts_by_category_normal, total_trackers_normal),
        "AI Overview": (ai_overview_urls, tracker_counts_by_category_ai, total_trackers_ai)
    }

    for url_type, (urls, tracker_counts_by_category, total_trackers) in url_types.items():
        for url in urls:
            driver.get(url)
            time.sleep(3)  # Allow time for loading
            
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
                category = get_tracker_info_from_data(domain)
                if category:
                    tracker_counts_by_category[category] += 1
                    total_trackers += 1

        # Store the total tracker count
        if url_type == "Normal":
            total_trackers_normal = total_trackers
        else:
            total_trackers_ai = total_trackers

    # Print summary
    print(f"\nQuery: '{query}'")
    print("AI Overview:")
    print(f"Number of AI Overview sites: {len(ai_overview_urls)}")
    print("Tracker counts by category:")
    for category, count in tracker_counts_by_category_ai.items():
        print(f"  {category}: {count}")
    avg_trackers_ai = total_trackers_ai / len(ai_overview_urls) if ai_overview_urls else 0
    print(f"Average trackers per AI Overview site: {avg_trackers_ai:.2f}")

    print("\nNormal Results:")
    print(f"Number of Normal sites: {len(normal_urls)}")
    print("Tracker counts by category:")
    for category, count in tracker_counts_by_category_normal.items():
        print(f"  {category}: {count}")
    avg_trackers_normal = total_trackers_normal / len(normal_urls) if normal_urls else 0
    print(f"Average trackers per Normal site: {avg_trackers_normal:.2f}")

# Close the driver
driver.quit()
