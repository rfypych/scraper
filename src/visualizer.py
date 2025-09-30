import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the output directory exists
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

def create_sentiment_pie_chart(df, filename="sentiment_pie_chart.png"):
    """
    Creates and saves a pie chart of the sentiment distribution.

    Args:
        df (pd.DataFrame): DataFrame with a 'sentiment' column.
        filename (str): The name of the file to save the chart to.

    Returns:
        str: The path to the saved image file.
    """
    if df.empty or 'sentiment' not in df:
        logging.warning("DataFrame is empty or missing 'sentiment' column. Skipping pie chart creation.")
        return None

    logging.info("Creating sentiment distribution pie chart...")
    sentiment_counts = df['sentiment'].value_counts()

    plt.figure(figsize=(8, 8))
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140,
            colors=['#4CAF50', '#F44336', '#FFC107']) # Green, Red, Amber
    plt.title('Sentiment Distribution')
    plt.ylabel('') # Hides the 'sentiment' label on the y-axis

    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path)
    plt.close() # Close the figure to free up memory

    logging.info(f"Sentiment pie chart saved to {save_path}")
    return save_path

def create_word_cloud(df, text_column='cleaned_text', filename="word_cloud.png"):
    """
    Creates and saves a word cloud from the text data.

    Args:
        df (pd.DataFrame): DataFrame with a text column.
        text_column (str): The column to use for the word cloud.
        filename (str): The name of the file to save the chart to.

    Returns:
        str: The path to the saved image file.
    """
    if df.empty or text_column not in df:
        logging.warning(f"DataFrame is empty or missing '{text_column}' column. Skipping word cloud creation.")
        return None

    logging.info("Creating word cloud...")
    text = " ".join(review for review in df[text_column].astype(str))

    if not text:
        logging.warning("No text available to generate a word cloud.")
        return None

    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("Most Frequent Words")

    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path)
    plt.close()

    logging.info(f"Word cloud saved to {save_path}")
    return save_path

def draw_sna_graph(G, filename="sna_graph.png"):
    """
    Draws and saves the Social Network Analysis graph.

    Args:
        G (nx.Graph): The NetworkX graph object.
        filename (str): The name of the file to save the chart to.

    Returns:
        str: The path to the saved image file.
    """
    if not isinstance(G, nx.Graph) or G.number_of_nodes() == 0:
        logging.warning("Invalid or empty graph provided. Skipping SNA graph drawing.")
        return None

    logging.info("Drawing SNA graph...")
    plt.figure(figsize=(12, 12))

    # Use a layout that spreads nodes out
    pos = nx.spring_layout(G, k=0.15, iterations=20)

    # Draw the graph
    nx.draw(G, pos, with_labels=True, node_size=50, font_size=8, width=0.5, edge_color='grey')

    plt.title("Social Network Analysis - User Mentions")

    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path)
    plt.close()

    logging.info(f"SNA graph saved to {save_path}")
    return save_path

if __name__ == '__main__':
    # Example usage for testing
    print("Creating dummy data and graph to test the visualization module...")

    # Dummy data for pie chart and word cloud
    dummy_data = {
        'sentiment': ['positive', 'negative', 'positive', 'neutral', 'positive'],
        'cleaned_text': ['python is great', 'i hate bugs', 'learning python is fun', 'just a tweet', 'great community']
    }
    dummy_df = pd.DataFrame(dummy_data)

    # Dummy graph for SNA
    dummy_graph = nx.Graph()
    dummy_graph.add_edges_from([('a', 'b'), ('a', 'c'), ('b', 'c'), ('c', 'd')])

    print("\nTesting Pie Chart Creation...")
    pie_chart_path = create_sentiment_pie_chart(dummy_df)
    if pie_chart_path:
        print(f"Pie chart created at: {pie_chart_path}")

    print("\nTesting Word Cloud Creation...")
    word_cloud_path = create_word_cloud(dummy_df)
    if word_cloud_path:
        print(f"Word cloud created at: {word_cloud_path}")

    print("\nTesting SNA Graph Drawing...")
    sna_graph_path = draw_sna_graph(dummy_graph)
    if sna_graph_path:
        print(f"SNA graph created at: {sna_graph_path}")