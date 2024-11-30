# get_queries.py

import pandas as pd

def get_top_queries_from_csv(file_path, top_n=25):
    """
    Extract the top queries from a CSV file.

    :param file_path: Path to the CSV file containing the queries.
    :param top_n: Number of top queries to extract.
    :return: List of top queries.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, header=None, names=["query", "value"])
        
        # Clean and sort the data
        df['value'] = pd.to_numeric(df['value'], errors='coerce')  # Convert 'value' to numeric
        df = df.dropna(subset=['value'])  # Remove rows with non-numeric 'value'
        df = df.sort_values(by='value', ascending=False)  # Sort by value
        
        # Get the top queries
        top_queries = df['query'].head(top_n).tolist()
        return top_queries

    except Exception as e:
        print(f"Error processing file: {e}")
        return []

# Test Case
if __name__ == "__main__":
    # Example usage
    file_path1 = "/Users/chloebright/Downloads/Queries/GeneticDisordersQueries.csv"
    file_path2 = "/Users/chloebright/Downloads/Queries/Drug&AlcoholTreatmentQueries.csv"
    file_path3 = "/Users/chloebright/Downloads/Queries/MentalHealthQueries.csv"
    file_path4 = "/Users/chloebright/Downloads/Queries/ReproductiveHealthQueries.csv"
    file_path5 = "/Users/chloebright/Downloads/Queries/Aging&Geriatrics.csv"
    file_path6 = "/Users/chloebright/Downloads/Queries/sleepdisorders"
    file_path7 = "/Users/chloebright/Downloads/Queries/pain management"
    top_queries = get_top_queries_from_csv(file_path1) + get_top_queries_from_csv(file_path2) +get_top_queries_from_csv(file_path3) + get_top_queries_from_csv(file_path4) + get_top_queries_from_csv(file_path5) + get_top_queries_from_csv(file_path6) + get_top_queries_from_csv(file_path7)
    print("Top Queries:", top_queries)
    print(len(top_queries))
