import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import os

SERVER_URL = "http://andrewbaker.ddns.net/download"

def download_file():
    filename = filename_entry.get().strip()
    if not filename:
        messagebox.showerror("Error", "Please enter a filename")
        return
    
    try:
        output_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)
        with requests.get(f"{SERVER_URL}/{filename}", stream=True) as r:
            r.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        messagebox.showinfo("Success", f"Downloaded to {output_path}")
    except Exception as e:
        messagebox.showerror("Download Failed", str(e))

# GUI setup
root = tk.Tk()
root.title("File Downloader")
root.geometry("400x150")

tk.Label(root, text="Enter filename to download:").pack(pady=10)
filename_entry = tk.Entry(root, width=50)
filename_entry.pack(pady=5)

download_button = tk.Button(root, text="Download", command=download_file)
download_button.pack(pady=20)

root.mainloop()
