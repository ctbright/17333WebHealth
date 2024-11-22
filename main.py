import csv
from get_links import get_links  
from get_tracker_info import analyze_trackers, summarize_tracker_data
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from collections import defaultdict

def main():
    # List of search queries
    search_queries = ["flu symptoms"]#, "cancer symptoms", "stroke symptoms"]

    # Define tracker categories for the CSV columns
    tracker_categories = [
        "Advertising", "Site Analytics", "Consent Management", "Essential",
        "Hosting", "Customer Interaction", "Audio/Video Player", "Extensions",
        "Adult Advertising", "Social Media", "Miscellaneous", "Uncategorized"
    ]

    # Define the output CSV file path
    output_csv = "tracker_summary.csv"

    # Set up a single WebDriver instance
    driver_path = '/usr/local/bin/chromedriver'
    service = Service(driver_path)
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--headless")  # Use headless mode if you don't need the browser window
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Prepare CSV file with headers
        headers = ["Query"]
        for url_type in ["Normal", "AI Overview"]:
            headers.append(f"{url_type}_Average")
            headers.extend([f"{url_type}_{category}" for category in tracker_categories])

        with open(output_csv, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            # Initialize data structure for calculating averages
            aggregate_data = defaultdict(float)
            num_queries = 0

            # Process each query and write results to CSV
            for query in search_queries:
                print(f"Processing query: {query}")
                
                # Get URLs
                normal_urls, ai_overview_urls = get_links(query)
                
                # Analyze trackers
                tracker_data = analyze_trackers(normal_urls, ai_overview_urls)
                
                # Summarize tracker data for the query
                summary = summarize_tracker_data(query, tracker_data, tracker_categories)
                
                # Accumulate data for averages
                num_queries += 1
                for key, value in summary.items():
                    if key != "Query":  # Exclude the "Query" column
                        aggregate_data[key] += value

                # Write the summarized data to the CSV file
                writer.writerow(summary)

            # Calculate averages and write the final row
            average_row = {"Query": "Average"}
            for key in headers:
                if key != "Query":  # Exclude the "Query" column
                    average_row[key] = aggregate_data[key] / num_queries if num_queries > 0 else 0

            writer.writerow(average_row)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
