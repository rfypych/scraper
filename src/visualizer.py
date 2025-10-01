import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import logging
import os
from pathlib import Path
from pyvis.network import Network

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Define project root and output directory using absolute paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_sentiment_pie_chart(df, filename="sentiment_pie_chart.png"):
    """Creates and saves a pie chart of the sentiment distribution."""
    if df.empty or 'sentiment' not in df:
        logging.warning("DataFrame is empty or missing 'sentiment' column. Skipping pie chart creation.")
        return None

    logging.info("Creating sentiment distribution pie chart...")
    sentiment_counts = df['sentiment'].value_counts()

    plt.figure(figsize=(8, 8))
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140,
            colors=['#4CAF50', '#FFC107', '#F44336']) # Green, Amber, Red for pos, neu, neg
    plt.title('Sentiment Distribution')
    plt.ylabel('')

    save_path = OUTPUT_DIR / filename
    plt.savefig(save_path)
    plt.close()

    logging.info(f"Sentiment pie chart saved to {save_path}")
    return str(save_path)

def create_word_cloud(df, text_column='cleaned_text', filename="word_cloud.png"):
    """Creates and saves a word cloud from the text data."""
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

    save_path = OUTPUT_DIR / filename
    plt.savefig(save_path)
    plt.close()

    logging.info(f"Word cloud saved to {save_path}")
    return str(save_path)

def create_interactive_sna_graph(G, filename="interactive_sna_graph.html"):
    """
    Creates and saves an interactive Social Network Analysis graph as an HTML file.

    Args:
        G (nx.Graph): The NetworkX graph object.
        filename (str): The name of the HTML file to save the chart to.

    Returns:
        str: The path to the saved HTML file.
    """
    if not isinstance(G, nx.Graph) or G.number_of_nodes() == 0:
        logging.warning("Invalid or empty graph provided. Skipping interactive SNA graph creation.")
        return None

    logging.info("Creating interactive SNA graph with Pyvis...")

    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False)
    net.from_nx(G)

    # Set physics options for a better layout
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      }
    }
    """)

    save_path = OUTPUT_DIR / filename
    try:
        net.save_graph(str(save_path))
        logging.info(f"Interactive SNA graph saved to {save_path}")
        return str(save_path)
    except Exception as e:
        logging.error(f"Failed to save interactive SNA graph: {e}")
        return None

# This function is now deprecated in favor of the interactive one but kept for compatibility.
def draw_sna_graph(G, filename="sna_graph.png"):
    """Draws and saves a static SNA graph."""
    logging.warning("`draw_sna_graph` is deprecated. Use `create_interactive_sna_graph` instead.")
    return create_interactive_sna_graph(G, filename="interactive_sna_graph.html")


if __name__ == '__main__':
    print("Creating dummy data and graph to test the visualization module...")

    dummy_data = {
        'sentiment': ['positive', 'negative', 'positive', 'neutral', 'positive'],
        'cleaned_text': ['python is great', 'i hate bugs', 'learning python is fun', 'just a tweet', 'great community']
    }
    dummy_df = pd.DataFrame(dummy_data)

    dummy_graph = nx.Graph()
    dummy_graph.add_edges_from([('a', 'b'), ('a', 'c'), ('b', 'c'), ('c', 'd')])

    print("\nTesting Pie Chart Creation...")
    create_sentiment_pie_chart(dummy_df)

    print("\nTesting Word Cloud Creation...")
    create_word_cloud(dummy_df)

    print("\nTesting Interactive SNA Graph Drawing...")
    create_interactive_sna_graph(dummy_graph)