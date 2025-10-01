import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Toplevel
import threading
import asyncio
from datetime import datetime
import queue
import os
from pathlib import Path

# --- Define project root and output directory using absolute paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Import backend modules ---
from scraper import scrape_x
from reddit_scraper import scrape_reddit
from processor import process_data
from analyzer import initialize_sentiment_model, analyze_sentiment, create_sna_graph
from visualizer import create_sentiment_pie_chart, create_word_cloud, draw_sna_graph, create_interactive_sna_graph

class LoginPopup(Toplevel):
    # ... (LoginPopup class remains unchanged)
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login X/Twitter")
        self.geometry("350x150")
        self.transient(parent)
        self.grab_set()
        self.username = None
        self.password = None
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)
        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.username_entry.focus_set()
        ttk.Label(main_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ok_button = ttk.Button(button_frame, text="Login", command=self.on_ok)
        ok_button.pack(side=tk.LEFT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Batal", command=self.on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=5)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window(self)
    def on_ok(self, event=None):
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()
        if not self.username or not self.password:
            messagebox.showwarning("Input Kosong", "Username dan password tidak boleh kosong.", parent=self)
            return
        self.destroy()
    def on_cancel(self):
        self.username = None
        self.password = None
        self.destroy()

class SocialScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media Scraper & Analyzer")
        self.geometry("700x650")
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        platform_frame = ttk.LabelFrame(self.main_frame, text="Pilih Platform")
        platform_frame.pack(fill=tk.X, padx=5, pady=5)
        platform_frame.columnconfigure(1, weight=1)
        ttk.Label(platform_frame, text="Platform:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.platform_var = tk.StringVar(value="Twitter")
        self.platform_menu = ttk.Combobox(platform_frame, textvariable=self.platform_var, values=["Twitter", "Reddit"], state="readonly")
        self.platform_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.platform_menu.bind("<<ComboboxSelected>>", self.update_ui_for_platform)
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Parameter Input")
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)
        self.input_frame.columnconfigure(1, weight=1)
        self.target_label = ttk.Label(self.input_frame, text="Kata Kunci:")
        self.target_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_entry = ttk.Entry(self.input_frame)
        self.target_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.start_date_label = ttk.Label(self.input_frame, text="Tanggal Mulai (YYYY-MM-DD):")
        self.start_date_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_date_entry = ttk.Entry(self.input_frame)
        self.start_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.end_date_label = ttk.Label(self.input_frame, text="Tanggal Selesai (YYYY-MM-DD):")
        self.end_date_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.end_date_entry = ttk.Entry(self.input_frame)
        self.end_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        self.reddit_target_type_label = ttk.Label(self.input_frame, text="Tipe Target:")
        self.reddit_target_type_var = tk.StringVar(value="Subreddit")
        self.reddit_target_type_menu = ttk.Combobox(self.input_frame, textvariable=self.reddit_target_type_var, values=["Subreddit", "Kata Kunci Pencarian"], state="readonly")
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        control_frame.columnconfigure((0, 1, 2), weight=1)
        self.start_button = ttk.Button(control_frame, text="Mulai Scraping", command=self.start_scraping_thread)
        self.start_button.grid(row=0, column=0, padx=5, sticky=tk.EW)
        self.stop_button = ttk.Button(control_frame, text="Berhenti", state=tk.DISABLED, command=self.stop_scraping)
        self.stop_button.grid(row=0, column=1, padx=5, sticky=tk.EW)
        self.export_button = ttk.Button(control_frame, text="Ekspor Hasil", state=tk.DISABLED, command=self.export_results)
        self.export_button.grid(row=0, column=2, padx=5, sticky=tk.EW)
        log_frame = ttk.LabelFrame(self.main_frame, text="Log Status")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.scraping_thread = None
        self.stop_event = threading.Event()
        self.log_queue = queue.Queue()
        self.final_df = None
        self.output_files = {}
        self.after(100, self.process_log_queue)
        self.update_ui_for_platform()

    def update_ui_for_platform(self, event=None):
        platform = self.platform_var.get()
        self.reddit_target_type_label.grid_remove()
        self.reddit_target_type_menu.grid_remove()
        if platform == "Twitter":
            self.target_label.config(text="Kata Kunci (dipisah koma):")
            self.start_date_label.grid()
            self.start_date_entry.grid()
            self.end_date_label.grid()
            self.end_date_entry.grid()
        elif platform == "Reddit":
            self.reddit_target_type_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            self.reddit_target_type_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
            self.target_label.config(text="Subreddit / Kata Kunci:")
            self.start_date_label.grid_remove()
            self.start_date_entry.grid_remove()
            self.end_date_label.grid_remove()
            self.end_date_entry.grid_remove()

    def log_message(self, message):
        self.log_queue.put(message)

    def process_log_queue(self):
        while not self.log_queue.empty():
            try:
                message = self.log_queue.get_nowait()
                self.log_area.config(state=tk.NORMAL)
                self.log_area.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
                self.log_area.see(tk.END)
                self.log_area.config(state=tk.DISABLED)
                self.update_idletasks()
            except queue.Empty:
                pass
        self.after(100, self.process_log_queue)

    def start_scraping_thread(self):
        platform = self.platform_var.get()
        target_input = self.target_entry.get().strip()

        if not target_input:
            messagebox.showwarning("Input Diperlukan", "Input target tidak boleh kosong.")
            return

        self.update_ui_for_scraping_start()

        if platform == "Twitter":
            keywords = [k.strip() for k in target_input.split(',')]
            keywords = [k for k in keywords if k]
            if not keywords:
                messagebox.showwarning("Input Diperlukan", "Format kata kunci salah.")
                self.update_ui_for_scraping_end()
                return
            formatted_keyword = f"({' OR '.join(keywords)})" if len(keywords) > 1 else keywords[0]
            self.log_message(f"Keywords processed. Search query will be: {formatted_keyword}")

            login_popup = LoginPopup(self)
            username, password = login_popup.username, login_popup.password
            if not username or not password:
                self.log_message("Proses login dibatalkan.")
                self.update_ui_for_scraping_end()
                return

            args = (platform, formatted_keyword, self.start_date_entry.get(), self.end_date_entry.get(), username, password)

        elif platform == "Reddit":
            reddit_target_type = self.reddit_target_type_var.get()
            self.log_message(f"Targeting Reddit {reddit_target_type}: {target_input}")
            args = (platform, target_input, reddit_target_type)

        self.scraping_thread = threading.Thread(target=self.run_scraping_pipeline, args=args)
        self.scraping_thread.start()

    def run_scraping_pipeline(self, platform, *args):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            self.log_message("Menginisialisasi model analisis sentimen...")
            initialize_sentiment_model()

            raw_df = None
            if platform == "Twitter":
                keyword, start_date, end_date, username, password = args
                self.log_message(f"Memulai proses scraping dari {platform}...")
                raw_df = loop.run_until_complete(scrape_x(keyword, start_date, end_date, username, password, stop_event=self.stop_event))
            elif platform == "Reddit":
                target, target_type = args
                self.log_message(f"Memulai proses scraping dari {platform}...")
                raw_df = loop.run_until_complete(scrape_reddit(target, target_type, stop_event=self.stop_event))

            if self.stop_event.is_set() or raw_df is None or raw_df.empty:
                self.log_message("Proses dihentikan atau tidak ada data yang ditemukan.")
                return

            self.log_message(f"Ditemukan {len(raw_df)} item. Memulai pembersihan data...")
            # We need to make processor and analyzer more generic
            processed_df = process_data(raw_df)
            if processed_df.empty:
                self.log_message("Tidak ada data tersisa setelah pembersihan.")
                return

            self.log_message("Melakukan analisis sentimen...")
            sentiment_df = analyze_sentiment(processed_df, text_column='cleaned_text')

            self.log_message("Membuat graf Social Network Analysis (SNA)...")
            sna_graph = create_sna_graph(sentiment_df)

            self.final_df = sentiment_df

            self.log_message("Membuat visualisasi hasil analisis...")
            self.output_files['pie_chart'] = create_sentiment_pie_chart(sentiment_df)
            self.output_files['word_cloud'] = create_word_cloud(sentiment_df)
            # Use interactive graph for SNA
            self.output_files['sna_graph'] = create_interactive_sna_graph(sna_graph, filename="interactive_sna.html")

            self.log_message("Semua proses telah selesai!")
            self.log_message("Anda sekarang dapat mengekspor hasilnya.")

        except Exception as e:
            self.log_message(f"Terjadi error: {e}")
            messagebox.showerror("Error", f"Terjadi kesalahan pada proses backend:\n{e}")
        finally:
            self.stop_event.clear()
            self.after(0, self.update_ui_for_scraping_end)

    def stop_scraping(self):
        if self.scraping_thread and self.scraping_thread.is_alive():
            self.log_message("Mengirim sinyal berhenti...")
            self.stop_event.set()

    def export_results(self):
        if self.final_df is not None and not self.final_df.empty:
            try:
                csv_path = OUTPUT_DIR / "scraped_data_analyzed.csv"
                self.final_df.to_csv(csv_path, index=False)
                report_message = "Hasil telah berhasil diekspor ke direktori 'output':\n"
                report_message += f"\n- Data CSV: {os.path.basename(str(csv_path))}"
                if self.output_files.get('pie_chart'):
                    report_message += f"\n- Grafik Sentimen: {os.path.basename(self.output_files['pie_chart'])}"
                if self.output_files.get('word_cloud'):
                    report_message += f"\n- Word Cloud: {os.path.basename(self.output_files['word_cloud'])}"
                if self.output_files.get('sna_graph'):
                    report_message += f"\n- Grafik SNA Interaktif (HTML): {os.path.basename(self.output_files['sna_graph'])}"
                messagebox.showinfo("Ekspor Berhasil", report_message)
            except Exception as e:
                messagebox.showerror("Error Ekspor", f"Gagal menyimpan file: {e}")
        else:
            messagebox.showwarning("Tidak Ada Data", "Tidak ada data untuk diekspor.")

    def update_ui_for_scraping_start(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.DISABLED)
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete('1.0', tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.output_files = {}

    def update_ui_for_scraping_end(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.final_df is not None and not self.final_df.empty:
            self.export_button.config(state=tk.NORMAL)
        self.stop_event.clear()

if __name__ == "__main__":
    app = SocialScraperApp()
    app.log_message("Aplikasi siap. Pilih platform dan masukkan parameter.")
    app.mainloop()