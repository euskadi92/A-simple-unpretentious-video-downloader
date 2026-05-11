import customtkinter as ctk
from tkinter import filedialog
import yt_dlp
import threading
import os
import subprocess


# Appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_PATH = os.path.expanduser("~\Videos")


class YouTubeDownloaderApp(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        icon_path = os.path.join(os.path.dirname(__file__), "yt-downloader.ico")
        self.iconbitmap(icon_path)
        self.geometry("520x380")
        self.resizable(False, False)

        # --- URL ---
        ctk.CTkLabel(self, text="YouTube URL").pack(pady=(20, 5))
        self.url_entry = ctk.CTkEntry(self, width=420)
        self.url_entry.pack()

        # --- Path ---
        ctk.CTkLabel(self, text="Download Folder").pack(pady=(20, 5))

        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(pady=5)

        self.path_entry = ctk.CTkEntry(self.path_frame, width=300)
        self.path_entry.insert(0, DEFAULT_PATH)
        self.path_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            self.path_frame, text="Browse", command=self.browse_path, width=80
        ).pack(side="left")

        # --- Download Button ---
        self.download_button = ctk.CTkButton(
            self, text="Download", command=self.start_download, height=40
        )
        self.download_button.pack(pady=20)

        # --- Progress Bar ---
        self.progress = ctk.CTkProgressBar(self, width=420)
        self.progress.set(0)
        self.progress.pack(pady=(10, 5))

        # --- Status + Speed Row ---
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(pady=(5, 10))

        self.status_label = ctk.CTkLabel(self.info_frame, text="")
        self.status_label.pack(side="left", padx=(0, 5))

        self.separator_label = ctk.CTkLabel(self.info_frame, text="||")
        self.separator_label.pack(side="left", padx=5)

        self.speed_label = ctk.CTkLabel(self.info_frame, text="")
        self.speed_label.pack(side="left", padx=(5, 0))

    

    def browse_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def start_download(self):
        threading.Thread(target=self.download_video, daemon=True).start()

    def open_folder(self, path):
            subprocess.Popen(f'explorer "{path}"')

    def download_video(self):
        url = self.url_entry.get()
        output_path = self.path_entry.get()
        print("Video will be output to: " + output_path)

        if not url:
            self.update_status("Please enter a URL")
            return

        self.update_status("Starting download...")
        self.progress.set(0)
        self.update_speed("")
        self.download_button.configure(state="disabled")

        

        def progress_hook(d):
            if d["status"] == "downloading":
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded_bytes = d.get("downloaded_bytes", 0)

                if total_bytes:
                    percent = downloaded_bytes / total_bytes
                    self.update_progress(percent)
                    self.update_status(f"{percent * 100:.1f}% downloaded")


                speed = d.get("speed")
                if speed:
                    speed_mb = speed / 1024 / 1024
                    self.update_speed(f"{speed_mb:.2f} MB/s")

            elif d["status"] == "finished":
                self.update_progress(1)
                self.update_status("Processing file...")

        try:
            ydl_opts = {
                "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "noplaylist": True,
                "progress_hooks": [progress_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.update_status("Download completed")
            self.update_speed("")
            self.download_button.configure(state="enabled")
            self.open_folder(self, output_path)


        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.update_speed("")

    


    # --- UI thread-safe updates ---
    def update_progress(self, value):
        self.after(0, lambda: self.progress.set(value))

    def update_status(self, message):
        self.after(0, lambda: self.status_label.configure(text=message))

    def update_speed(self, message):
        self.after(0, lambda: self.speed_label.configure(text=message))


if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()