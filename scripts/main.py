# Elegant Game Downloader UI with Progress Bar
import customtkinter as ctk
import requests
import os
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

SERVER_URL = "http://andrewbaker.ddns.net/download"
GAME_CHOICES = [
    "shiftatmidnight",
    "brotato",
    "madness-melee",
    "deltarune",
    "miside",
    "7zip",
    "solarsandbox",
    "ultrakill",
    "forzahorizon2",
    "granny",
    "minecraft-1.16.5"
]


class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Games4School Downloader")
        self.geometry("500x360")
        self.resizable(False, False)
        self.configure(bg="#10101a")

        # Title
        ctk.CTkLabel(
            self,
            text="Download a Game",
            font=("Orbitron", 28, "bold"),
            text_color="#00f0ff"
        ).pack(pady=(28, 8))

        ctk.CTkLabel(
            self,
            text="Select a game to download",
            font=("Tomorrow", 15),
            text_color="#ff00f0"
        ).pack(pady=(0, 18))

        # Dropdown
        self.game_var = ctk.StringVar(value=GAME_CHOICES[0])
        self.dropdown = ctk.CTkOptionMenu(
            self,
            values=GAME_CHOICES,
            variable=self.game_var,
            width=280,
            font=("Rajdhani", 16),
            fg_color="#222",
            text_color="#fff",
            dropdown_fg_color="#181830",
            dropdown_text_color="#00f0ff"
        )
        self.dropdown.pack(pady=10)

        # Download button
        self.download_btn = ctk.CTkButton(
            self,
            text="Download",
            font=("Rajdhani", 18, "bold"),
            fg_color="#00f0ff",
            text_color="#0a0a1a",
            hover_color="#ff00f0",
            command=self.start_download_thread
        )
        self.download_btn.pack(pady=18)

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            self,
            width=320,
            height=14,
            progress_color="#00f0ff"
        )
        self.progress.set(0)
        self.progress.pack(pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Tomorrow", 13),
            text_color="#aaa"
        )
        self.status_label.pack(pady=10)

    def start_download_thread(self):
        """Run download in a thread to keep UI responsive"""
        threading.Thread(target=self.download_file, daemon=True).start()

    def download_file(self):
        game = self.game_var.get()
        # File naming logic
        if game in ("solarsandbox", "7zip"):
            orig_ext = ".exe"
        else:
            orig_ext = ".zip"

        url_filename = game + ".mp3"
        temp_filename = game + ".mp3"
        final_filename = game + orig_ext

        self.download_btn.configure(state="disabled", text="Downloading...")
        self.status_label.configure(text="Starting download...",
                                    text_color="#aaa")
        self.progress.set(0)

        try:
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")  # noqa: E501
            temp_path = os.path.join(downloads_folder, temp_filename)
            final_path = os.path.join(downloads_folder, final_filename)

            with requests.get(f"{SERVER_URL}/{url_filename}", stream=True) as r:  # noqa: E501
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                chunk_size = 1024 * 1024  # 1 MB per chunk
                update_step = max(total // 100, chunk_size)  # update every ~1%

                with open(temp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Only update when enough data has been written
                        if total > 0 and downloaded % update_step < chunk_size:
                            progress_value = downloaded / total
                            self.progress.set(progress_value)
                            self.status_label.configure(
                                text=f"{downloaded // (1024*1024)} MB / {total // (1024*1024)} MB"  # noqa: E501
                            )
                            self.update_idletasks()

            # Rename .mp3 to original extension
            os.rename(temp_path, final_path)

            self.progress.set(1)
            self.status_label.configure(
                text=f"Downloaded to {final_path}",
                text_color="#00ff66"
            )
        except Exception as e:
            self.status_label.configure(
                text=f"Download failed: {e}",
                text_color="#ff004c"
            )
        finally:
            self.download_btn.configure(state="normal", text="Download")


if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
