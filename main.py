# main.py

from get_links_trackers import get_links_and_trackers
from get_tracker_info import analyze_trackers, print_summary

def main():
    # Sample search queries
    search_queries = ["flu symptoms", "cancer symptoms", "stroke symptoms"]
    
    for query in search_queries:
        normal_urls, ai_overview_urls = get_links_and_trackers(query)
        tracker_data = analyze_trackers(normal_urls, ai_overview_urls)
        print_summary(query, tracker_data)

if __name__ == "__main__":
    main()
