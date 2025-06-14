try:
    from tkinter import messagebox
    import customtkinter as ctk
    import threading
    import requests
    import pathlib
except ImportError:
    import os
    print("Installing Dependencies...")
    os.system('pip install tk')
    os.system('pip install customtkinter requests')
    import customtkinter as ctk

SOURCES: dict[str, str] = {
    "Java8": "http://mc.fissionhost.org:15028/download-jdk8",  # noqa: E501
    "PolyMC": "http://mc.fissionhost.org:15028/download-polymc"  # noqa: E501
}


class GUI:
    def __init__(self) -> None:
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.java_downloaded: bool = False
        self.polymc_downloaded: bool = False
        self.percent: int = 0
        self.stage: int = 0
        self.overall_percent: int = 0
        self.percent_lock = threading.Lock()

        self.app = ctk.CTk()
        self.app.title("Minecraft Downloader")
        self.app.geometry("800x420")

        self.main_frame = ctk.CTkFrame(self.app)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.username_label = ctk.CTkLabel(
            self.main_frame,
            text="Please enter your Minecraft username:"
        )
        self.username_label.pack(pady=(10, 0))

        self.username_var = ctk.StringVar()
        self.username_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Enter Username",
            textvariable=self.username_var
        )
        self.username_entry.pack(pady=20)

        self.username_var.trace_add("write", self.on_username_change)

        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="Start",
            command=self.start_pressed
        )
        self.start_button.pack(pady=10)
        self.start_button.pack_forget()

        # Log box (initially hidden)
        self.log_box = ctk.CTkTextbox(self.main_frame, height=150)
        self.log_box.pack(pady=10, fill="both", expand=False)
        self.log_box.pack_forget()

    def _download(self, url: str, filename: str, name: str):
        self.log(f"Starting download of: {name}\n", "gold")
        self.stage += 1
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            with self.percent_lock:
                                if total:
                                    self.percent = (downloaded/total) * 100
                                    self.overall_percent = (1*self.stage) + self.percent  # noqa: E501

                self.log(f"{name} download complete!\n", "green")
        except Exception as e:
            self.log(f"Download of {name} failed: {e}\n", "red")

    def startDownloadThread(self):
        def downloadAll():
            download_path = str(pathlib.Path.home() / "Downloads" / "OpenJDK8.tar.gz")  # noqa: E501
            self._download(SOURCES["Java8"],
                           download_path,
                           "Java")
            self.java_downloaded = True
            download_path = str(pathlib.Path.home() / "Downloads" / "PolyMC.zip")  # noqa: E501
            # self.download_progress.set(0)
            self._download(SOURCES["PolyMC"],
                           download_path,
                           "PolyMC")
            self.polymc_downloaded = True

        threading.Thread(target=self.updateProgressBar, daemon=True).start()
        threading.Thread(target=downloadAll, daemon=True).start()

    def updateProgressBar(self):
        self.log("Creating progress bar\n", color="cyan")
        while not all([self.java_downloaded, self.polymc_downloaded]):
            # Update download progress bar
            if not hasattr(self, "download_progress"):
                self.download_progress = ctk.CTkProgressBar(
                    self.main_frame
                )
                self.download_progress.pack(pady=5)
                self.download_progress.set(0)

            with self.percent_lock:
                percent = self.percent
            self.download_progress.set(percent / 100)

            # Update overall progress bar
            if not hasattr(self, "overall_progress"):
                self.overall_progress = ctk.CTkProgressBar(
                    self.main_frame
                )
                self.overall_progress.pack(pady=5)
                self.overall_progress.set(0)
            self.overall_progress.set(self.overall_percent / 200)

        self.download_progress.forget()
        self.log("Released download bar\n", "pink")

    def start_pressed(self):
        username = self.username_var.get()
        messagebox.showinfo("Welcome", f"Starting with username: {username}")
        self.start_button.pack_forget()
        self.log_box.pack(pady=10, fill="both", expand=False)
        self.log(f"Welcome, {username}!\n", "white")

        self.startDownloadThread()

    def log(self, text: str, color: str = "white"):
        tag_name = f"color_{color}"

        # Get index before inserting
        start_index = self.log_box.index("end-1c")
        self.log_box.insert("end", text)
        end_index = self.log_box.index("end-1c")

        if tag_name not in self.log_box.tag_names():
            self.log_box.tag_config(tag_name, foreground=color)

        self.log_box.tag_add(tag_name, start_index, end_index)
        self.log_box.see("end")

    def on_username_change(self, *args):
        username = self.username_var.get()
        if len(username) > 3:
            self.start_button.pack(pady=10)
        else:
            self.start_button.pack_forget()

    def start(self) -> None:
        self.app.mainloop()


if __name__ == "__main__":
    gui = GUI()
    gui.start()
