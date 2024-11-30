import csv
from get_links import get_links
from get_tracker_info import analyze_trackers
from collections import defaultdict

def main():
    # List of search queries
    search_queries = ['anderson', 'anemia', 'flu symptoms']
    
    # Define the output CSV file path
    output_csv = "tracker_summary_detailed.csv"

    # Start with base headers
    headers = ["Query", "URL", "Type", "Position", "Total Trackers"]
    queries_without_ai_links = []  # To keep track of queries without AI overview links

    # Extend headers with category names from CATEGORY_MAPPING
    from get_tracker_info import CATEGORY_MAPPING
    headers.extend(CATEGORY_MAPPING.values())

    # Open the CSV file for writing
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

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
            
            # Write each link's data to the CSV
            for tracker_entry in detailed_tracker_data:
                tracker_entry["Query"] = query  # Add the query to each entry
                writer.writerow({k: tracker_entry.get(k, 0) for k in headers})

    # Print queries without AI overview links
    if queries_without_ai_links:
        print("\nQueries without AI overview links:")
        for query in queries_without_ai_links:
            print(f"- {query}")

if __name__ == "__main__":
    main()
