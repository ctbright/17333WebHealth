# get_tracker_info.py

import time
import json
from collections import defaultdict
from urllib.parse import urlparse
from whotracksme.data.loader import DataSource
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Initialize data source
data = DataSource()

def get_tracker_id_from_domain(domain):
    if domain.startswith("www."):
        domain = domain[4:]
    query = "SELECT tracker FROM tracker_domains WHERE domain LIKE ?"
    result = data.db.connection.execute(query, ('%' + domain + '%',)).fetchone()
    return result[0] if result else None

def get_tracker_info_from_data(domain):
    tracker_id = get_tracker_id_from_domain(domain)
    if tracker_id:
        tracker_info = data.trackers.get_tracker(tracker_id)
        if tracker_info:
            return tracker_info.get("category")
    return None

def analyze_trackers(normal_urls, ai_overview_urls):
    # Set up Chrome options and enable basic performance logging
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    # Path to ChromeDriver
    driver_path = '/usr/local/bin/chromedriver'  # Update if necessary
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    tracker_data = {
        "Normal": {"urls": normal_urls, "tracker_counts": defaultdict(int), "total_trackers": 0},
        "AI Overview": {"urls": ai_overview_urls, "tracker_counts": defaultdict(int), "total_trackers": 0}
    }

    for url_type, data in tracker_data.items():
        for url in data["urls"]:
            driver.get(url)
            time.sleep(3)
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

            for domain in third_party_domains:
                category = get_tracker_info_from_data(domain)
                if category:
                    data["tracker_counts"][category] += 1
                    data["total_trackers"] += 1
    
    driver.quit()
    return tracker_data

def print_summary(query, tracker_data):
    print(f"\nQuery: '{query}'")

    for url_type, data in tracker_data.items():
        print(f"\n{url_type} Results:")
        print(f"Number of {url_type} sites: {len(data['urls'])}")
        print("Tracker counts by category:")
        for category, count in data["tracker_counts"].items():
            print(f"  {category}: {count}")
        avg_trackers = data["total_trackers"] / len(data["urls"]) if data["urls"] else 0
        print(f"Average trackers per {url_type} site: {avg_trackers:.2f}")
