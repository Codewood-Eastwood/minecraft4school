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
    "Java8": "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u452-b09/OpenJDK8U-jdk_x64_windows_hotspot_8u452b09.zip"  # noqa: E501
}


class GUI:
    def __init__(self) -> None:
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.java_downloaded: bool = False

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
                            percent = (downloaded / total) * 100 if total \
                                else 0
                            self.log(f"Download progress: {percent:.1f}"
                                     "%\n",
                                     "cyan")
                self.log(f"{name} download complete!\n", "green")
        except Exception as e:
            self.log(f"Download of {name} failed: {e}\n", "red")

    def startDownloadThread(self):
        def downloadJava():
            self._download(SOURCES["Java8"],
                           f"{pathlib.Path.home()}/Downloads",
                           "Java")
            self.java_downloaded = True
            return
        threading.Thread(target=downloadJava, daemon=True).start()

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
