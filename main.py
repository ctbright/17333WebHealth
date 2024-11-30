import csv
from get_links import get_links  
from get_tracker_info import analyze_trackers
from collections import defaultdict

def main():
    # List of search queries
    search_queries = ['anderson', 'anemia']
    
    # Define the output CSV file path
    output_csv = "tracker_summary_detailed.csv"

    # Start with base headers
    headers = ["Query", "URL", "Type", "Position", "Total Trackers"]
    queries_without_ai_links = []  # To keep track of queries without AI overview links

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
                
                # Add any new categories dynamically to the headers
                for category in tracker_entry.keys():
                    if category not in headers:
                        headers.append(category)
                        
                        # Reinitialize the CSV writer with updated headers
                        writer = csv.DictWriter(csvfile, fieldnames=headers)
                        csvfile.seek(0)  # Go back to the beginning of the file
                        writer.writeheader()  # Rewrite header row with new fields
                
                # Write the tracker entry to the file
                writer.writerow(tracker_entry)

    # Print queries without AI overview links
    if queries_without_ai_links:
        print("\nQueries without AI overview links:")
        for query in queries_without_ai_links:
            print(f"- {query}")

if __name__ == "__main__":
    main()
