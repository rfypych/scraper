import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Toplevel
import threading
import asyncio
from datetime import datetime
import queue
import os

# Import backend modules
from scraper import scrape_x
from processor import process_data
from analyzer import initialize_sentiment_model, analyze_sentiment, create_sna_graph
from visualizer import create_sentiment_pie_chart, create_word_cloud, draw_sna_graph

class LoginPopup(Toplevel):
    """A Toplevel window for the user to input their login credentials."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login X/Twitter")
        self.geometry("350x150")
        self.transient(parent) # Keep on top of the main window
        self.grab_set() # Modal

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
        self.geometry("700x600")

        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(self.main_frame, text="Parameter Input")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Kata Kunci:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.keyword_entry = ttk.Entry(input_frame)
        self.keyword_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(input_frame, text="Tanggal Mulai (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_date_entry = ttk.Entry(input_frame)
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(input_frame, text="Tanggal Selesai (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.end_date_entry = ttk.Entry(input_frame)
        self.end_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

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

        # --- State Variables & Threading ---
        self.scraping_thread = None
        self.stop_event = threading.Event()
        self.log_queue = queue.Queue()
        self.final_df = None
        self.output_files = {}

        # Start checking the log queue
        self.after(100, self.process_log_queue)

    def log_message(self, message):
        self.log_queue.put(message)

    def process_log_queue(self):
        """Processes messages from the log queue to update the GUI."""
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
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Input Diperlukan", "Kata kunci tidak boleh kosong.")
            return

        login_popup = LoginPopup(self)
        username, password = login_popup.username, login_popup.password

        if not username or not password:
            self.log_message("Proses login dibatalkan.")
            return

        self.update_ui_for_scraping_start()
        self.scraping_thread = threading.Thread(
            target=self.run_scraping_pipeline,
            args=(keyword, self.start_date_entry.get(), self.end_date_entry.get(), username, password)
        )
        self.scraping_thread.start()

    def run_scraping_pipeline(self, keyword, start_date, end_date, username, password):
        """The main pipeline executed in a separate thread."""
        try:
            # This is a bridge between synchronous (threading) and asynchronous (asyncio) code
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # --- 1. Initialize models ---
            self.log_message("Menginisialisasi model analisis sentimen...")
            initialize_sentiment_model()

            # --- 2. Scrape Data ---
            self.log_message("Memulai proses scraping dari X/Twitter...")
            # Note: We'll need to modify scrape_x to accept the stop_event
            raw_df = loop.run_until_complete(scrape_x(keyword, start_date, end_date, username, password, stop_event=self.stop_event))

            if self.stop_event.is_set() or raw_df is None or raw_df.empty:
                self.log_message("Proses dihentikan atau tidak ada data yang ditemukan.")
                return

            # --- 3. Process Data ---
            self.log_message(f"Ditemukan {len(raw_df)} tweet. Memulai pembersihan data...")
            processed_df = process_data(raw_df)
            if processed_df.empty:
                self.log_message("Tidak ada data tersisa setelah pembersihan.")
                return

            # --- 4. Analyze Data ---
            self.log_message("Melakukan analisis sentimen...")
            sentiment_df = analyze_sentiment(processed_df, text_column='cleaned_text')

            self.log_message("Membuat graf Social Network Analysis (SNA)...")
            sna_graph = create_sna_graph(sentiment_df)

            self.final_df = sentiment_df # Store for export

            # --- 5. Visualize Data ---
            self.log_message("Membuat visualisasi hasil analisis...")
            self.output_files['pie_chart'] = create_sentiment_pie_chart(sentiment_df)
            self.output_files['word_cloud'] = create_word_cloud(sentiment_df)
            self.output_files['sna_graph'] = draw_sna_graph(sna_graph)

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
                csv_path = os.path.join("output", "scraped_data_analyzed.csv")
                self.final_df.to_csv(csv_path, index=False)

                report_message = "Hasil telah berhasil diekspor ke direktori 'output':\n"
                report_message += f"\n- Data CSV: {os.path.basename(csv_path)}"
                if self.output_files.get('pie_chart'):
                    report_message += f"\n- Grafik Sentimen: {os.path.basename(self.output_files['pie_chart'])}"
                if self.output_files.get('word_cloud'):
                    report_message += f"\n- Word Cloud: {os.path.basename(self.output_files['word_cloud'])}"
                if self.output_files.get('sna_graph'):
                    report_message += f"\n- Grafik SNA: {os.path.basename(self.output_files['sna_graph'])}"

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
    app.log_message("Aplikasi siap. Masukkan parameter dan klik 'Mulai Scraping'.")
    app.mainloop()