try:
    from tkinter import messagebox
    import customtkinter as ctk
    import threading
    import requests
except ImportError:
    import os
    print("Installing Dependencies...")
    os.system('pip install tk')
    os.system('pip install customtkinter requests')
    import customtkinter as ctk

SOURCES: dict[str, str] = {
    "Java8": "https://my.microsoftpersonalcontent.com/personal/90bca5534677330a/_layouts/15/download.aspx?UniqueId=e25a7706-3aed-4fec-bf6a-e06ff6f3c646&Translate=false&tempauth=v1e.eyJzaXRlaWQiOiI3YWRmMjc4Ni1mNmE2LTQ1NmUtYmQ3OC0yMWYwYjQ1ZjU2N2YiLCJhcHBpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDA0ODE3MTBhNCIsImF1ZCI6IjAwMDAwMDAzLTAwMDAtMGZmMS1jZTAwLTAwMDAwMDAwMDAwMC9teS5taWNyb3NvZnRwZXJzb25hbGNvbnRlbnQuY29tQDkxODgwNDBkLTZjNjctNGM1Yi1iMTEyLTM2YTMwNGI2NmRhZCIsImV4cCI6IjE3NDk4NDM1NjgifQ.2Ft_BAzNNPJ0WJjGKcIagKRQ65EvJtFIE4DqStkBLdgYxmVqjumhvFyYdXuPd56cxpWRdI3y5tMdS0x7sZTxMMbDGuvGgrrVOFOlUouX4VUrnpcungErRdcVLvPfZjPBYiKaRTBT3W2GVRSXYuOlMfpHHx5ypd1r-dU4ydKNIJ6SFUzphEBd0N0KoQgBfd_eREzyb4IASoDbuaxZcBmwyIq1Msu-5nfjDK5zrA_FmmkzoY8cay1EgY10lFFG9m9PWP6261gNvC6G--k4NVp2QR1AA6dGDBoSB7C189ipF4HJtPLJ_GtI5AWZEp-XWDQxM37dtIBRRFHfcGlWoY3aEIq414RPOsY2r627ElJcaYF_2uw-tNlDq0bl--rVE7A1smU1oXeW1G0neIWNAFHczFcLSY5wcXBXoT8TFvhXvHA.N5b4jQj8NDYBSq_GALOA0lMrLVDGVOofATHIpxDgTwU&ApiVersion=2.0&AVOverride=1"
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

    def on_username_change(self, *args):
        username = self.username_var.get()
        if len(username) > 3:
            self.start_button.pack(pady=10)
        else:
            self.start_button.pack_forget()

    def start_pressed(self):
        username = self.username_var.get()
        messagebox.showinfo("Welcome", f"Starting with username: {username}")
        self.start_button.pack_forget()
        self.log_box.pack(pady=10, fill="both", expand=False)
        self.log(f"Welcome, {username}!\n", "white")
        
        self.downloadJava()

        if self.java_downloaded == True:
            self.log("Finishing installation and opening Minecraft...\n", "gold")
    
    def downloadJava(self):
        def _download():
            url = SOURCES["Java8"]
            local_filename = "java8.zip"       
            self.log("Starting Java 8 download...\n", "gold")
            try:
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    total = int(r.headers.get('content-length', 0))
                    downloaded = 0        
                    with open(local_filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                percent = (downloaded / total) * 100 if total else 0
                                self.log(f"Download progress: {percent:1.1}%\n", "cyan")
                                    
                self.log("Java download complete!\n", "green")
                self.java_downloaded = True
                return
            except Exception as e:
                self.log(f"Download failed: {e}\n", "red")        
        threading.Thread(target=_download, daemon=True).start()
        
    def log(self, text: str, color: str = "white"):
        tag_name = f"color_{color}"
    
        # Get index before inserting
        start_index = self.log_box.index("end-1c")
        self.log_box.insert("end", text)
        end_index = self.log_box.index("end-1c")
    
        if not tag_name in self.log_box.tag_names():
            self.log_box.tag_config(tag_name, foreground=color)
    
        self.log_box.tag_add(tag_name, start_index, end_index)
        self.log_box.see("end")


    def start(self) -> None:
        self.app.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.start()

