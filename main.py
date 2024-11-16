# main.py

from findLinks import get_links_and_trackers
from get_tracker_info import analyze_trackers, print_summary
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def main():
    search_queries = ["flu symptoms", "cancer symptoms", "stroke symptoms"]

    # Set up a single WebDriver instance
    driver_path = '/usr/local/bin/chromedriver'
    service = Service(driver_path)
    options = Options()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        for query in search_queries:
            print(f"Processing query: {query}")
            
            # Get URLs
            normal_urls, ai_overview_urls = get_links_and_trackers(query, driver)
            
            # Analyze trackers
            tracker_data = analyze_trackers(normal_urls, ai_overview_urls)
            
            # Print results
            print_summary(query, tracker_data)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()