import pandas as pd
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Graceful degradation for Sastrawi ---
try:
    from sastrawi.stemmer.stemmer_factory import StemmerFactory
    SASTRAWI_AVAILABLE = True
    logging.info("Sastrawi stemmer library found and imported successfully.")
except ImportError:
    SASTRAWI_AVAILABLE = False
    logging.warning("Sastrawi library not found. Stemming will be skipped.")

def clean_text(text):
    """Cleans a single text entry."""
    if not isinstance(text, str): return ""
    text = re.sub(r'http\S+', '', text); text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'@\w+', '', text); text = text.replace('#', '')
    text = re.sub(r'[^a-zA-Z\s]', '', text); text = text.lower(); text = text.strip()
    return text

def stem_text(text, stemmer):
    """Applies stemming to the text using the Sastrawi stemmer."""
    return stemmer.stem(text)

def process_data(df):
    """
    Processes raw scraped data from any platform.
    - Identifies the correct text columns.
    - For Google News, it combines Title and Snippet.
    - Cleans and optionally stems the text.
    """
    if df.empty:
        logging.warning("Input DataFrame is empty. Skipping processing.")
        return df

    logging.info("Starting data processing...")

    # --- Identify and prepare the source text column ---
    if 'Teks Tweet' in df.columns: # Twitter
        source_text_col = 'Teks Tweet'
        df['source_text'] = df[source_text_col]
    elif 'Text' in df.columns: # Reddit
        source_text_col = 'Text'
        df['source_text'] = df[source_text_col]
    elif 'Title' in df.columns and 'Snippet' in df.columns: # Google News
        source_text_col = 'Google News (Title + Snippet)'
        df['source_text'] = df['Title'] + ' ' + df['Snippet']
    else:
        logging.error("No recognizable text columns found in DataFrame.")
        return pd.DataFrame()

    logging.info(f"Using '{source_text_col}' as the source text.")

    # 1. Clean the text
    logging.info("Cleaning text...")
    df['cleaned_text'] = df['source_text'].apply(clean_text)

    # 2. Stemming (optional)
    if SASTRAWI_AVAILABLE:
        logging.info("Initializing and applying Sastrawi stemmer...")
        try:
            factory = StemmerFactory(); stemmer = factory.create_stemmer()
            df['stemmed_text'] = df['cleaned_text'].apply(lambda x: stem_text(x, stemmer))
            logging.info("Stemming complete.")
        except Exception as e:
            logging.error(f"An error occurred during stemming: {e}")
            df['stemmed_text'] = df['cleaned_text']
    else:
        df['stemmed_text'] = df['cleaned_text']

    # Remove rows where cleaned_text is empty
    df.dropna(subset=['cleaned_text'], inplace=True)
    df = df[df['cleaned_text'] != '']

    logging.info(f"Data processing complete. Shape of the processed data: {df.shape}")

    return df