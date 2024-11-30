import csv
from get_links import get_links
from get_tracker_info import analyze_trackers
from collections import defaultdict

def main():
    # List of search queries
    search_queries = ['anderson', 'anemia']
    
    # Define the output CSV file paths
    output_summary_csv = "tracker_summary_detailed.csv"
    output_trackers_csv = "tracker_names.csv"

    # Start with base headers for the detailed summary
    headers = ["Query", "URL", "Type", "Position", "Total Trackers"]
    queries_without_ai_links = []  # To keep track of queries without AI overview links

    # Extend headers with category names from CATEGORY_MAPPING
    from get_tracker_info import CATEGORY_MAPPING
    headers.extend(CATEGORY_MAPPING.values())

    # Open the summary and trackers CSV files for writing
    with open(output_summary_csv, "w", newline="") as summary_csv, open(output_trackers_csv, "w", newline="") as trackers_csv:
        summary_writer = csv.DictWriter(summary_csv, fieldnames=headers)
        trackers_writer = csv.writer(trackers_csv)

        # Write headers for both CSVs
        summary_writer.writeheader()
        trackers_writer.writerow(["Query", "Type", "URL", "Tracker Name"])

        # Process each query
        for query in search_queries:
            print(f"Processing query: {query}")
            
            # Get URLs
            normal_urls, ai_overview_urls = get_links(query)
            
            if not ai_overview_urls:
                # Skip analysis if no AI overview links are found
                print(f"No AI overview links found for query: {query}")
                queries_without_ai_links.append(query)
                continue
            
            # Analyze trackers
            detailed_tracker_data = analyze_trackers(normal_urls, ai_overview_urls)
            
            # Write detailed summary data to the summary CSV
            for tracker_entry in detailed_tracker_data:
                tracker_entry["Query"] = query  # Add the query to each entry
                summary_writer.writerow({k: tracker_entry.get(k, 0) for k in headers})

                # Extract tracker names and write them to the trackers CSV
                if "Tracker Names" in tracker_entry:
                    for tracker_name in tracker_entry["Tracker Names"]:
                        trackers_writer.writerow([
                            query,
                            tracker_entry["Type"],  # Add Type (Normal/AI Overview)
                            tracker_entry["URL"],
                            tracker_name
                        ])

    # Print queries without AI overview links
    if queries_without_ai_links:
        print("\nQueries without AI overview links:")
        for query in queries_without_ai_links:
            print(f"- {query}")

if __name__ == "__main__":
    main()
