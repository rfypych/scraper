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
    logging.warning("To enable stemming, please ensure Sastrawi is installed correctly (`pip install Sastrawi`).")

def clean_tweet_text(text):
    """
    Cleans a single tweet text.
    - Removes URLs
    - Removes HTML tags
    - Removes mentions (@username)
    - Removes hashtags (#) but keeps the text
    - Removes special characters and numbers
    - Converts to lowercase
    """
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = text.replace('#', '')  # Remove hashtag symbol
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters and numbers
    text = text.lower()  # Convert to lowercase
    text = text.strip()  # Remove leading/trailing whitespace
    return text

def stem_text(text, stemmer):
    """
    Applies stemming to the text using the Sastrawi stemmer.
    """
    return stemmer.stem(text)

def process_data(df):
    """
    Processes the raw scraped data.

    Args:
        df (pd.DataFrame): The DataFrame containing raw tweet data.

    Returns:
        pd.DataFrame: The processed and cleaned DataFrame.
    """
    if df.empty:
        logging.warning("Input DataFrame is empty. Skipping processing.")
        return df

    logging.info("Starting data processing...")

    # 1. Clean the tweet text
    logging.info("Cleaning tweet text...")
    df['cleaned_text'] = df['Teks Tweet'].apply(clean_tweet_text)

    # 2. Stemming (only if Sastrawi is available)
    if SASTRAWI_AVAILABLE:
        logging.info("Initializing Sastrawi stemmer...")
        try:
            factory = StemmerFactory()
            stemmer = factory.create_stemmer()
            logging.info("Applying stemming to text...")
            # Note: Stemming can be slow on large datasets.
            df['stemmed_text'] = df['cleaned_text'].apply(lambda x: stem_text(x, stemmer))
            logging.info("Stemming complete.")
        except Exception as e:
            logging.error(f"An error occurred during stemming with Sastrawi: {e}")
            logging.warning("Skipping the stemming process due to an error.")
            df['stemmed_text'] = df['cleaned_text'] # Fallback
    else:
        # If the library is not available, just copy the cleaned text.
        df['stemmed_text'] = df['cleaned_text']

    # Remove rows where cleaned_text is empty after processing
    df.dropna(subset=['cleaned_text'], inplace=True)
    df = df[df['cleaned_text'] != '']

    logging.info(f"Data processing complete. Shape of the processed data: {df.shape}")

    return df

if __name__ == '__main__':
    # Example usage for testing
    print("Creating a dummy DataFrame to test the processing module...")

    dummy_data = {
        'Tweet ID': ['1', '2', '3'],
        'Teks Tweet': [
            'Wow, #Python itu keren banget! Cek link ini: https://python.org @guido',
            'Belajar data science dengan pandas itu menyenangkan. <html><body><p>Tag</p></body></html>',
            'Analisis sentimen menggunakan AI 123.'
        ]
    }
    dummy_df = pd.DataFrame(dummy_data)

    print("\nOriginal DataFrame:")
    print(dummy_df)

    processed_df = process_data(dummy_df.copy())

    print("\nProcessed DataFrame:")
    print(processed_df)
    print("\nNote: 'stemmed_text' will be the same as 'cleaned_text' if Sastrawi is not found.")