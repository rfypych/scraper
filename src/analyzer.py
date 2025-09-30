import pandas as pd
import networkx as nx
import logging
from transformers import pipeline
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to hold the sentiment analysis pipeline
# This is to avoid reloading the model on every call
sentiment_pipeline = None

def initialize_sentiment_model():
    """
    Initializes the sentiment analysis pipeline from Hugging Face.
    This function should be called once before analyzing sentiment.
    """
    global sentiment_pipeline
    if sentiment_pipeline is None:
        try:
            logging.info("Initializing sentiment analysis model (IndoBERT)...")
            # Using a well-known model for Indonesian sentiment analysis
            model_name = "mdhugol/indonesia-bert-sentiment-classification"
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=model_name
            )
            logging.info("Sentiment analysis model initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize sentiment model: {e}")
            sentiment_pipeline = None

def analyze_sentiment(df, text_column='cleaned_text'):
    """
    Analyzes the sentiment of tweets in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame with tweet data.
        text_column (str): The name of the column containing the cleaned text.

    Returns:
        pd.DataFrame: The DataFrame with an added 'sentiment' column.
    """
    global sentiment_pipeline
    if sentiment_pipeline is None:
        logging.error("Sentiment model is not initialized. Please call initialize_sentiment_model() first.")
        df['sentiment'] = 'neutral' # Default value
        return df

    if df.empty or text_column not in df:
        logging.warning(f"Input DataFrame is empty or lacks '{text_column}' column. Skipping sentiment analysis.")
        return df

    logging.info("Performing sentiment analysis...")

    # The pipeline returns a list of dicts, e.g., [{'label': 'positive', 'score': 0.99}]
    # We'll just extract the label.
    try:
        # The pipeline can take a list of strings directly
        sentiments = sentiment_pipeline(df[text_column].tolist())
        df['sentiment'] = [result['label'] for result in sentiments]
    except Exception as e:
        logging.error(f"An error occurred during sentiment analysis: {e}")
        df['sentiment'] = 'error'

    logging.info("Sentiment analysis complete.")
    return df

def create_sna_graph(df):
    """
    Creates a Social Network Analysis (SNA) graph from tweet data.
    The graph connects users who mention other users in their tweets.

    Args:
        df (pd.DataFrame): The DataFrame with tweet data. Must include 'Username' and 'Teks Tweet' columns.

    Returns:
        nx.Graph: A NetworkX graph object.
    """
    if df.empty:
        logging.warning("Input DataFrame is empty. Cannot create SNA graph.")
        return nx.Graph()

    logging.info("Creating Social Network Analysis (SNA) graph...")
    G = nx.Graph()

    for index, row in df.iterrows():
        author = row['Username']
        tweet_text = row['Teks Tweet']

        # Add the author as a node
        if not G.has_node(author):
            G.add_node(author)

        # Find all mentions in the tweet
        mentions = re.findall(r'@(\w+)', tweet_text)

        for mentioned_user in mentions:
            # Add the mentioned user as a node
            if not G.has_node(mentioned_user):
                G.add_node(mentioned_user)

            # Add an edge between the author and the mentioned user
            if G.has_edge(author, mentioned_user):
                # Increase the weight if the edge already exists
                G[author][mentioned_user]['weight'] += 1
            else:
                G.add_edge(author, mentioned_user, weight=1)

    logging.info(f"SNA graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

if __name__ == '__main__':
    # Example usage for testing
    print("Creating a dummy DataFrame to test the analysis module...")

    dummy_data = {
        'Username': ['user_a', 'user_b', 'user_c'],
        'Teks Tweet': [
            'Ini adalah tweet yang sangat positif! Saya suka sekali @user_b.',
            'Saya tidak setuju dengan @user_a, ini pengalaman yang buruk.',
            'Hari ini cuaca cerah, dan saya me-mention @user_a dan @user_b.'
        ],
        'cleaned_text': [
            'ini adalah tweet yang sangat positif saya suka sekali',
            'saya tidak setuju dengan ini pengalaman yang buruk',
            'hari ini cuaca cerah dan saya me-mention dan'
        ]
    }
    dummy_df = pd.DataFrame(dummy_data)

    print("\nOriginal DataFrame:")
    print(dummy_df)

    # Test sentiment analysis
    initialize_sentiment_model()
    if sentiment_pipeline:
        sentiment_df = analyze_sentiment(dummy_df.copy())
        print("\nDataFrame with Sentiment Analysis:")
        print(sentiment_df)
    else:
        print("\nSkipping sentiment analysis test because model initialization failed.")

    # Test SNA
    sna_graph = create_sna_graph(dummy_df.copy())
    print("\nSNA Graph Info:")
    print(f"Nodes: {list(sna_graph.nodes())}")
    print(f"Edges: {list(sna_graph.edges(data=True))}")