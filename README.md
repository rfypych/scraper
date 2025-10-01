# Social Media Scraper & Analyzer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Automated-green.svg)
![Pyvis](https://img.shields.io/badge/Pyvis-Interactive_Graphs-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A versatile desktop application designed to scrape, analyze, and visualize data from social media platforms. This tool provides an end-to-end pipeline from raw data collection to insightful analysis, all within a user-friendly graphical interface. Currently supports **Twitter** and **Reddit**.

## 🚀 Key Features

- **Multi-Platform Support:** Scrape data from both **Twitter** and **Reddit** using a simple dropdown menu.
- **Flexible Targeting:**
    - **Twitter:** Scrape by single or multiple keywords within a specific date range.
    - **Reddit:** Scrape top posts from a specific **Subreddit** or from a global **Keyword Search**.
- **Interactive SNA Visualization:** Generates a dynamic, interactive 3D Social Network Analysis graph as an `.html` file, allowing you to zoom, pan, and explore user connections.
- **Rich Data Collection:** Gathers not just posts but also **all top-level comments** from Reddit threads for deeper discourse analysis.
- **AI-Powered Analysis:**
  - **Sentiment Analysis:** Classifies each post/comment as `positive`, `negative`, atau `neutral` using a pre-trained IndoBERT model.
- **Comprehensive Visualizations:** In addition to the interactive SNA graph, it also generates:
  - A **Pie Chart** for sentiment distribution.
  - A **Word Cloud** for the most frequent terms.
- **Robust & Responsive:** The backend runs in a separate thread to keep the GUI responsive, and it gracefully handles potential library issues.

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
    - Use the **"Platform"** dropdown menu to choose either "Twitter" or "Reddit". The input fields will change automatically.

3.  **Enter Parameters**

    **If you selected Twitter:**
    - **Kata Kunci:** Enter a single keyword or multiple keywords separated by a comma (e.g., `ganjar, prabowo`).
    - **Tanggal Mulai & Selesai:** Specify the date range.

    **If you selected Reddit:**
    - **Tipe Target:** Choose whether you want to scrape a "Subreddit" or perform a "Kata Kunci Pencarian" (Keyword Search).
    - **Subreddit / Kata Kunci:** Enter the name of the subreddit (e.g., `indonesia`) or your search term.

4.  **Start the Process**
    - Click the **"Mulai Scraping"** button.
    - If you chose Twitter, a login pop-up will appear. Reddit scraping does not require a login.

5.  **Monitor and Wait**
    - The application will start its process. You can monitor the real-time progress in the **Log Status** window.

6.  **Export Results**
    - Once complete, click the **"Ekspor Hasil"** button. This will save the following to the `output` directory:
      - A `.csv` file with all the scraped data.
      - A sentiment pie chart (`.png`).
      - A word cloud (`.png`).
      - An **interactive SNA graph (`.html`)** which you can open in your web browser.

---
*This project is intended for educational and research purposes. Please be aware of the terms of service of the social media platforms you are scraping.*