# Social Media Scraper & Analyzer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Automated-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A desktop application designed to scrape, analyze, and visualize data from social media platforms like X (formerly Twitter). This tool provides an end-to-end pipeline from raw data collection to insightful analysis, all within a user-friendly graphical interface.

## 🚀 Key Features

- **Graphical User Interface (GUI):** An intuitive desktop app built with Tkinter, eliminating the need for command-line interaction.
- **Targeted Scraping:** Scrape data from X/Twitter based on specific keywords and date ranges.
- **Secure Authentication:** A pop-up window for session-based login ensures your credentials are never stored.
- **Automated Data Cleaning:** Automatically removes URLs, HTML tags, mentions, and other noise from tweet text.
- **AI-Powered Analysis:**
  - **Sentiment Analysis:** Classifies each tweet as `positive`, `negative`, or `neutral` using a pre-trained IndoBERT model.
  - **Social Network Analysis (SNA):** Maps user interactions (mentions) to identify key influencers and communities.
- **Rich Visualizations:** Automatically generates and saves:
  - A **Pie Chart** for sentiment distribution.
  - A **Word Cloud** for the most frequent terms.
  - An **SNA Graph** to visualize user networks.
- **Data Export:** Easily export the full, analyzed dataset to a `.csv` file and save all visualizations with a single click.
- **Robust & Responsive:** The backend runs in a separate thread to keep the GUI responsive, and it gracefully handles potential library issues (like `Sastrawi`).

## 🛠️ Tech Stack

- **GUI:** `Tkinter`
- **Web Scraping:** `Playwright`
- **Data Manipulation:** `Pandas`
- **AI & NLP:** `Transformers (Hugging Face)`, `PyTorch`
- **Network Analysis:** `NetworkX`
- **Data Visualization:** `Matplotlib`, `WordCloud`

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
All required libraries are listed in `requirements.txt`.
```bash
pip install -r requirements.txt
```

**4. Install Playwright Browsers**
Playwright needs to download browser binaries for automation. This command will do it for you.
```bash
playwright install
```
If you encounter any issues on Linux, run the following command to install system dependencies:
```bash
playwright install-deps
```

## ▶️ How to Use

1.  **Run the Application**
    From the project's root directory, run the following command:
    ```bash
    python src/app.py
    ```

2.  **Enter Parameters**
    - Fill in the **Kata Kunci** (Keyword).
    - Specify the **Tanggal Mulai** (Start Date) and **Tanggal Selesai** (End Date) in `YYYY-MM-DD` format.

3.  **Start the Process**
    - Click the **"Mulai Scraping"** button.

4.  **Log In**
    - A pop-up window will appear. Enter your X/Twitter username and password.

5.  **Monitor and Wait**
    - The application will start scraping and analyzing data. You can monitor the progress in the **Log Status** window.

6.  **Export Results**
    - Once the process is complete, the **"Ekspor Hasil"** button will become active. Click it to save the `.csv` data and all visualization images to the `output` directory.

---
*This project is intended for educational and research purposes. Please be aware of the terms of service of the social media platforms you are scraping.*