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
    """
    Cleans a single text entry.
    - Removes URLs
    - Removes HTML tags
    - Removes mentions (@username)
    - Removes hashtags (#) but keeps the text
    - Removes special characters and numbers
    - Converts to lowercase
    """
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'@\w+', '', text)
    text = text.replace('#', '')
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    text = text.strip()
    return text

def stem_text(text, stemmer):
    """Applies stemming to the text using the Sastrawi stemmer."""
    return stemmer.stem(text)

def process_data(df):
    """
    Processes the raw scraped data from any platform.
    It identifies the correct text column ('Teks Tweet' or 'Text') and processes it.
    """
    if df.empty:
        logging.warning("Input DataFrame is empty. Skipping processing.")
        return df

    logging.info("Starting data processing...")

    # --- Identify the source text column ---
    if 'Teks Tweet' in df.columns:
        source_text_col = 'Teks Tweet'
    elif 'Text' in df.columns:
        source_text_col = 'Text'
    else:
        logging.error("No recognizable text column ('Teks Tweet' or 'Text') found in DataFrame.")
        return df # Return original df if no text column

    logging.info(f"Identified '{source_text_col}' as the source text column.")

    # 1. Clean the text
    logging.info("Cleaning text...")
    df['cleaned_text'] = df[source_text_col].apply(clean_text)

    # 2. Stemming (optional)
    if SASTRAWI_AVAILABLE:
        logging.info("Initializing Sastrawi stemmer...")
        try:
            factory = StemmerFactory()
            stemmer = factory.create_stemmer()
            logging.info("Applying stemming to text...")
            df['stemmed_text'] = df['cleaned_text'].apply(lambda x: stem_text(x, stemmer))
            logging.info("Stemming complete.")
        except Exception as e:
            logging.error(f"An error occurred during stemming with Sastrawi: {e}")
            df['stemmed_text'] = df['cleaned_text']
    else:
        df['stemmed_text'] = df['cleaned_text']

    # Remove rows where cleaned_text is empty
    df.dropna(subset=['cleaned_text'], inplace=True)
    df = df[df['cleaned_text'] != '']

    logging.info(f"Data processing complete. Shape of the processed data: {df.shape}")

    return df

if __name__ == '__main__':
    # ... (Test cases can be updated to reflect this new generic approach)
    print("Processor module is now generic.")