#get_tracker_info.py
import time
import json
from collections import defaultdict
from urllib.parse import urlparse
from whotracksme.data.loader import DataSource
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from whotracksme.data.loader import DataSource
# Initialize data source for the WhoTracksMe dataset
data = DataSource()

def get_tracker_id_from_domain(domain):
    """
    Retrieve the tracker ID associated with a given domain from the WhoTracksMe database.
    
    :param domain: Domain name to query.
    :return: Tracker ID if found, otherwise None.
    """
    if domain.startswith("www."):
        domain = domain[4:]
    query = "SELECT tracker FROM tracker_domains WHERE domain LIKE ?"
    result = data.db.connection.execute(query, ('%' + domain + '%',)).fetchone()
    return result[0] if result else None

def get_tracker_info_from_data(domain):
    """
    Get tracker information, such as its category, using the WhoTracksMe dataset.
    
    :param domain: Domain name to look up.
    :return: Tracker category if found, otherwise None.
    """
    tracker_id = get_tracker_id_from_domain(domain)
    if tracker_id:
        tracker_info = data.trackers.get_tracker(tracker_id)
        if tracker_info:
            return tracker_info.get("category")
    return None

def scroll_to_bottom(driver):
    """
    Scrolls to the bottom of the page to ensure all content is loaded.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Allow time for content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def analyze_trackers(normal_urls, ai_overview_urls):
    """
    Analyze third-party trackers on websites.

    :param normal_urls: List of URLs from standard search results.
    :param ai_overview_urls: List of URLs from AI Overview sections.
    :return: Detailed list of tracker data for each URL.
    """
    # Set up ChromeDriver with performance logging enabled
    driver_path = '/usr/local/bin/chromedriver'  # Update if necessary
    service = Service(driver_path)
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(service=service, options=chrome_options)

    tracker_details = []  # Store detailed data for each URL

    try:
        for url_type, urls in [("Normal", normal_urls), ("AI Overview", ai_overview_urls)]:
            for position, url in enumerate(urls, start=1):
                tracker_data = {
                    "Type": url_type,
                    "Position": position,
                    "URL": url,
                    "Total Trackers": 0,
                    "Tracker Names": []  # List of tracker names for detailed CSV
                }
                for formatted_category in CATEGORY_MAPPING.values():
                    tracker_data[formatted_category] = 0  # Initialize all categories to 0

                try:
                    driver.get(url)  # Navigate to the URL
                    scroll_to_bottom(driver)  # Ensure all content is loaded

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

                    tracker_data["Total Trackers"] = len(third_party_domains)
                    tracker_data["Tracker Names"] = list(third_party_domains)  # Populate tracker names

                    # Count trackers by category using CATEGORY_MAPPING
                    for domain in third_party_domains:
                        category = get_tracker_info_from_data(domain)
                        if category and category in CATEGORY_MAPPING:
                            formatted_category = CATEGORY_MAPPING[category]
                            tracker_data[formatted_category] += 1

                except Exception as e:
                    tracker_data["Error"] = str(e)

                tracker_details.append(tracker_data)

    finally:
        driver.quit()

    return tracker_details






# Mapping from raw tracker category names to formatted CSV column names
CATEGORY_MAPPING = {
    "advertising": "Advertising",
    "site_analytics": "Site Analytics",
    "consent": "Consent Management",
    "essential": "Essential",
    "hosting": "Hosting",
    "customer_interaction": "Customer Interaction",
    "audio_video_player": "Audio/Video Player",
    "extensions": "Extensions",
    "adult_advertising": "Adult Advertising",
    "social_media": "Social Media",
    "misc": "Miscellaneous",
    "uncategorized": "Uncategorized"
}

def summarize_tracker_data(query, tracker_data, tracker_categories):
    """
    Summarize tracker data for a single query into a structured dictionary for CSV output.

    :param query: Search query string.
    :param tracker_data: Dictionary containing tracker analysis results.
    :param tracker_categories: List of tracker categories to include in the summary.
    :return: Dictionary containing summary data for the query.
    """
    summary = {"Query": query}

    for url_type, data in tracker_data.items():
        avg_trackers = data["total_trackers"] / len(data["urls"]) if data["urls"] else 0
        summary[f"{url_type}_Average"] = avg_trackers

        # Map and summarize tracker counts
        for raw_category, formatted_category in CATEGORY_MAPPING.items():
            tracker_count = data["tracker_counts"].get(raw_category, 0)
            summary[f"{url_type}_{formatted_category}"] = tracker_count / len(data["urls"]) if data["urls"] else 0

    return summary

def print_summary(query, tracker_data):
    """
    Print a summary of the tracker analysis results for a given query.
    
    :param query: Search query string.
    :param tracker_data: Dictionary containing tracker analysis results.
    """
    print(f"\nQuery: '{query}'")

    # Iterate through results for both Normal and AI Overview URLs
    for url_type, data in tracker_data.items():
        print(f"\n{url_type} Results:")
        print(f"Number of {url_type} sites: {len(data['urls'])}")
        print("Tracker counts by category:")
        for category, count in data["tracker_counts"].items():
            print(f"  {category}: {count}")
        avg_trackers = data["total_trackers"] / len(data["urls"]) if data["urls"] else 0
        print(f"Average trackers per {url_type} site: {avg_trackers:.2f}")