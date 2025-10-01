# Social Media & News Scraper / Analyzer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Automated-green.svg)
![Pyvis](https://img.shields.io/badge/Pyvis-Interactive_Graphs-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A versatile desktop application designed to scrape, analyze, and visualize data from various online platforms. This tool provides an end-to-end pipeline from raw data collection to insightful analysis, all within a user-friendly graphical interface. Currently supports **Twitter**, **Reddit**, and **Google News**.

## 🚀 Key Features

- **Multi-Platform Support:** Scrape data from **Twitter**, **Reddit**, and **Google News** using a simple dropdown menu.
- **Flexible Targeting:**
    - **Twitter:** Scrape by single or multiple keywords within a specific date range.
    - **Reddit:** Scrape top posts from a specific **Subreddit** or from a global **Keyword Search**.
    - **Google News:** Scrape top news articles based on a search query.
- **Interactive SNA Visualization:** For social media platforms, it generates a dynamic, interactive 3D Social Network Analysis graph as an `.html` file.
- **Rich Data Collection:** Gathers not just posts but also **all top-level comments** from Reddit threads for deeper discourse analysis.
- **AI-Powered Analysis:**
  - **Sentiment Analysis:** Classifies each post, comment, or news article as `positive`, `negative`, atau `neutral`.
- **Comprehensive Visualizations:** In addition to the interactive SNA graph, it also generates:
  - A **Pie Chart** for sentiment distribution.
  - A **Word Cloud** for the most frequent terms.
- **Robust & Responsive:** The backend runs in a separate thread to keep the GUI responsive.

## 🛠️ Tech Stack

- **GUI:** `Tkinter`
- **Web Scraping:** `Playwright`
- **Data Manipulation:** `Pandas`
- **AI & NLP:** `Transformers (Hugging Face)`
- **Network Analysis:** `NetworkX`
- **Data Visualization:** `Matplotlib`, `WordCloud`, `Pyvis`

## ⚙️ Installation

Follow these steps to set up the project on your local machine.

**1. Clone the Repository**
```bash
git clone <repository-url>
cd <repository-directory>
```

**2. Set Up a Virtual Environment (Recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

**3. Install Python Dependencies**
```bash
pip install -r requirements.txt
```

**4. Install Playwright Browsers**
```bash
playwright install
```
If you encounter any issues on Linux, run `playwright install-deps`.

## ▶️ How to Use

1.  **Run the Application**
    From the project's root directory, run the following command:
    ```bash
    python src/app.py
    ```

2.  **Select a Platform**
    - Use the **"Platform"** dropdown menu to choose your target. The input fields will change automatically.

3.  **Enter Parameters**

    **If you selected Twitter:**
    - **Kata Kunci:** Enter a single keyword or multiple keywords separated by a comma (e.g., `ganjar, prabowo`).
    - **Tanggal Mulai & Selesai:** Specify the date range.

    **If you selected Reddit:**
    - **Tipe Target:** Choose "Subreddit" or "Kata Kunci Pencarian".
    - **Subreddit / Kata Kunci:** Enter the name of the subreddit (e.g., `indonesia`) or your search term.

    **If you selected Google News:**
    - **Kata Kunci Pencarian:** Enter your search query.
    - **Jumlah Artikel:** Specify the maximum number of articles to scrape (default is 50).

4.  **Start the Process**
    - Click the **"Mulai Scraping"** button.
    - If you chose Twitter, a login pop-up will appear. Reddit and Google News do not require a login.

5.  **Monitor and Wait**
    - The application will start its process. You can monitor the real-time progress in the **Log Status** window.

6.  **Export Results**
    - Once complete, click the **"Ekspor Hasil"** button. This will save the following to the `output` directory:
      - A `.csv` file with all the scraped data.
      - A sentiment pie chart (`.png`).
      - A word cloud (`.png`).
      - An **interactive SNA graph (`.html`)** if you scraped from Twitter or Reddit.

---
*This project is intended for educational and research purposes. Please be aware of the terms of service of the platforms you are scraping.*