import pandas as pd
import networkx as nx
import logging
from transformers import pipeline
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sentiment_pipeline = None

def initialize_sentiment_model():
    """Initializes the sentiment analysis pipeline."""
    global sentiment_pipeline
    if sentiment_pipeline is None:
        try:
            logging.info("Initializing sentiment analysis model (IndoBERT)...")
            model_name = "mdhugol/indonesia-bert-sentiment-classification"
            sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)
            logging.info("Sentiment analysis model initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize sentiment model: {e}")
            sentiment_pipeline = None

def analyze_sentiment(df, text_column='cleaned_text'):
    """Analyzes the sentiment of text in the DataFrame."""
    global sentiment_pipeline
    if sentiment_pipeline is None:
        logging.error("Sentiment model is not initialized.")
        df['sentiment'] = 'neutral'
        return df

    if df.empty or text_column not in df:
        logging.warning(f"DataFrame is empty or lacks '{text_column}'. Skipping sentiment analysis.")
        return df

    logging.info("Performing sentiment analysis...")
    try:
        sentiments = sentiment_pipeline(df[text_column].tolist())
        df['sentiment'] = [result['label'] for result in sentiments]
    except Exception as e:
        logging.error(f"An error occurred during sentiment analysis: {e}")
        df['sentiment'] = 'error'

    logging.info("Sentiment analysis complete.")
    return df

def create_sna_graph(df):
    """
    Creates a Social Network Analysis (SNA) graph from tweet or post data.
    It identifies the correct author/text columns based on the platform.
    """
    if df.empty:
        logging.warning("Input DataFrame is empty. Cannot create SNA graph.")
        return nx.Graph()

    # --- Identify platform-specific columns ---
    if 'Username' in df.columns and 'Teks Tweet' in df.columns: # Twitter
        author_col = 'Username'
        text_col = 'Teks Tweet'
        logging.info("Detected Twitter data format for SNA.")
    elif 'Author' in df.columns and 'Text' in df.columns: # Reddit
        author_col = 'Author'
        text_col = 'Text'
        logging.info("Detected Reddit data format for SNA.")
    else:
        logging.error("Could not determine author/text columns for SNA graph.")
        return nx.Graph()

    logging.info("Creating Social Network Analysis (SNA) graph...")
    G = nx.Graph()

    for index, row in df.iterrows():
        author = row[author_col]
        text = row[text_col]

        if not isinstance(author, str) or not isinstance(text, str):
            continue

        if not G.has_node(author):
            G.add_node(author, type='author')

        # Find mentions (@ for Twitter, u/ for Reddit)
        mentions = re.findall(r'[@|u/](\w+)', text)

        for mentioned_user in mentions:
            if not G.has_node(mentioned_user):
                G.add_node(mentioned_user, type='mentioned')

            if G.has_edge(author, mentioned_user):
                G[author][mentioned_user]['weight'] += 1
            else:
                G.add_edge(author, mentioned_user, weight=1)

    logging.info(f"SNA graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

if __name__ == '__main__':
    # ... (Test cases can be updated)
    print("Analyzer module is now generic.")