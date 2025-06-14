try:
    from tkinter import messagebox
    import customtkinter as ctk
    import threading
    import requests
    import pathlib
    import tarfile, zipfile, time
    import json, uuid, os, hashlib
except ImportError:
    import os
    print("Installing Dependencies...")
    os.system('pip install tk')
    os.system('pip install customtkinter requests')
    import customtkinter as ctk

SOURCES: dict[str, str] = {
    "Java21": "http://mc.fissionhost.org:15028/download-jdk21",  # noqa: E501
    "PolyMC": "http://mc.fissionhost.org:15028/download-polymc"  # noqa: E501
}


class GUI:
    def __init__(self) -> None:
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.java_downloaded: bool = False
        self.polymc_downloaded: bool = False
        self.extracted_all: bool = False
        self.installed: bool = False
        self.percent: int = 0
        self.stage: int = 0
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

        self.overall_progress = ctk.CTkProgressBar(
                    self.main_frame
        )
        self.overall_progress.pack(pady=5)
        self.overall_progress.set(0)

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

                self.log(f"{name} download complete!\n", "green")
        except Exception as e:
            self.log(f"Download of {name} failed: {e}\n", "red")

    def startDownloadThread(self):
        def downloadAll():
            download_path = str(pathlib.Path.home() / "Downloads" / "OpenJDK21.tar.gz")  # noqa: E501
            self._download(SOURCES["Java21"],
                           download_path,
                           "Java")
            self.java_downloaded = True
            self.overall_progress.set(0.25)
            download_path = str(pathlib.Path.home() / "Downloads" / "PolyMC.zip")  # noqa: E501
            # self.download_progress.set(0)
            self._download(SOURCES["PolyMC"],
                           download_path,
                           "PolyMC")
            self.polymc_downloaded = True
            self.overall_progress.set(0.5)

        threading.Thread(target=self.updateProgressBar, daemon=True).start()
        threading.Thread(target=self.extractAll, daemon=True).start()
        threading.Thread(target=self.configureAll, daemon=True).start()
        threading.Thread(target=downloadAll, daemon=True).start()

    def configureAll(self):
        # Wait until both files are downloaded
        while not self.extracted_all:
            time.sleep(0.1)
    
        self.log("Creating minecraft account.\n", "gold")
        polymc_path = str(pathlib.Path.home() / "Downloads" / "PolyMC" / "PolyMC")
        uuid_str = hashlib.md5(f"OfflinePlayer:{self.username}".encode('utf-8')).hexdigest()

        account_entry = {
            "active": True,
            "profile": {
                "capes": [],
                "id": uuid_str,
                "name": self.username,
                "skin": {
                    "id": "",
                    "url": "",
                    "variant": ""
                }
            },
            "type": "Offline",
            "ygg": {
                "extra": {
                    "clientToken": str(uuid.uuid4()).replace('-', ''),
                    "userName": self.username
                },
                "iat": int(time.time()),
                "token": "offline"
            }
        }
        
        # Build the final accounts structure
        accounts_json = {
            "accounts": [account_entry],
            "formatVersion": 3
        }

        polymc_config = f"""
AutoCloseConsole=false
AutoUpdate=true
CentralModsDir=mods
CloseAfterLaunch=false
ConsoleFont=Courier New
ConsoleFontSize=10
ConsoleMaxLines=100000
ConsoleOverflowStop=true
DefaultModPlatform=Modrinth
EnableFeralGamemode=false
EnableMangoHud=false
FlameKeyOverride=
FlameKeyShouldBeFetchedOnStartup=false
IconTheme=pe_colored
IconsDir=icons
IgnoreJavaCompatibility=false
IgnoreJavaWizard=false
InstSortMode=Name
InstanceDir=instances
JProfilerPath=
JVisualVMPath=
JavaPath={pathlib.Path.home()}/Downloads/OpenJDK21/jdk21u452-b09/bin/javaw.exe
JsonEditor=
JvmArgs=
Language=en_GB
LastHostname=DESKTOP-C7KQAGU
LastUsedGroupForNewInstance=
LaunchMaximized=false
MCEditPath=
MSAClientIDOverride=
MainWindowGeometry=AdnQywADAAAAAAEbAAAAHQAABDoAAAKTAAABGwAAADwAAAQ6AAACkwAAAAAAAAAABVYAAAEbAAAAPAAABDoAAAKT
MainWindowState=AAAA/wAAAAD9AAAAAAAAApEAAAIHAAAABAAAAAQAAAAIAAAACPwAAAADAAAAAQAAAAEAAAAeAGkAbgBzAHQAYQBuAGMAZQBUAG8AbwBsAEIAYQByAwAAAAD/////AAAAAAAAAAAAAAACAAAAAQAAABYAbQBhAGkAbgBUAG8AbwBsAEIAYQByAQAAAAD/////AAAAAAAAAAAAAAADAAAAAQAAABYAbgBlAHcAcwBUAG8AbwBsAEIAYQByAQAAAAD/////AAAAAAAAAAA=
MaxMemAlloc=3920
MenuBarInsteadOfToolBar=false
MetaURLOverride=
MinMemAlloc=512
MinecraftWinHeight=480
MinecraftWinWidth=854
ModMetadataDisabled=false
NewInstanceGeometry=AdnQywADAAAAAAJJAAAArAAABSIAAANaAAACSQAAAMsAAAUiAAADWgAAAAAAAAAAB4AAAAJJAAAAywAABSIAAANa
PagedGeometry=AdnQywADAAAAAAEIAAAAAAAABDkAAALDAAABCAAAAB8AAAQ5AAACwwAAAAAAAAAABVYAAAEIAAAAHwAABDkAAALD
PastebinCustomAPIBase=
PastebinType=3
PermGen=128
PostExitCommand=
PreLaunchCommand=
ProxyAddr=127.0.0.1
ProxyPass=
ProxyPort=8080
ProxyType=None
ProxyUser=
QuitAfterGameStop=false
RecordGameTime=true
SelectedInstance=Simply Optimized
ShowConsole=false
ShowConsoleOnError=true
ShowGameTime=true
ShowGlobalGameTime=true
UpdateChannel=118dbc6f
UseDiscreteGpu=false
UseNativeGLFW=false
UseNativeOpenAL=false
UserAgentOverride=
WrapperCommand=
"""
        
        account_file = os.path.join(polymc_path, 'accounts.json')
        with open(account_file, 'w') as f:
            json.dump(accounts_json, f, indent=4)

        cfg_file = os.path.join(polymc_path, 'polymc.cfg')
        with open(cfg_file, 'w') as f:
            json.dump(polymc_config, f, indent=4)

        self.log("Installation complete!")
        self.installed = True
        messagebox.showinfo("Success", f"Please wait while Minecraft launcher starts")
        os.system(str(pathlib.Path.home() / "Downloads" / "PolyMC" / "PolyMC" / "polymc.exe"))
        quit()
        

    def extractAll(self):
        # Wait until both files are downloaded
        while not all([self.java_downloaded, self.polymc_downloaded]):
            time.sleep(0.1)
    
        self.log("Installing apps...\n", "gold")
    
        try:
            # Extract OpenJDK21.tar.gz
            jdk_path = pathlib.Path.home() / "Downloads" / "OpenJDK21.tar.gz"
            jdk_extract_path = pathlib.Path.home() / "Downloads" / "OpenJDK21"
    
            self.log(f"Extracting Java to {jdk_extract_path}\n", "cyan")
            with tarfile.open(jdk_path, "r:gz") as tar:
                tar.extractall(path=jdk_extract_path)
            self.log("Java extraction complete!\n", "green")
            self.stage += 1
            self.overall_progress.set(0.75)
    
        except Exception as e:
            self.log(f"Java extraction failed: {e}\n", "red")
    
        try:
            # Extract PolyMC.zip
            polymc_path = pathlib.Path.home() / "Downloads" / "PolyMC.zip"
            polymc_extract_path = pathlib.Path.home() / "Downloads" / "PolyMC"
    
            self.log(f"Extracting PolyMC to {polymc_extract_path}\n", "cyan")
            with zipfile.ZipFile(polymc_path, 'r') as zip_ref:
                zip_ref.extractall(polymc_extract_path)
            self.log("PolyMC extraction complete!\n", "green")
            self.stage += 1
            self.overall_progress.set(1)
    
        except Exception as e:
            self.log(f"PolyMC extraction failed: {e}\n", "red")
    
        self.log("All installations done!\n", "white")
        self.extracted_all = True
    
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

        self.download_progress.forget()
        self.log("Released download bar\n", "pink")

    def start_pressed(self):
        self.username = self.username_var.get()
        messagebox.showinfo("Welcome", f"Starting with username: {self.username}")
        self.start_button.pack_forget()
        self.log_box.pack(pady=10, fill="both", expand=False)
        self.log(f"Welcome, {self.username}!\n", "white")

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

class PlayGUI:
    def __init__(self) -> None:
        print("Load assets")

        self.app = ctk.CTk()
        self.expected_quit = False
        self.app.title("PolyMC Launcher")
        self.app.geometry("300x200")

        # Play Button
        self.play_button = ctk.CTkButton(
            master=self.app,
            text="Play",
            command=self.play_game
        )
        self.play_button.pack(pady=10)

        # Reinstall Button
        self.reinstall_button = ctk.CTkButton(
            master=self.app,
            text="Reinstall",
            command=self.reinstall_game
        )
        self.reinstall_button.pack(pady=10)

    def play_game(self) -> None:
        os.system(str(pathlib.Path.home() / "Downloads" / "PolyMC" / "PolyMC" / "polymc.exe"))

    def reinstall_game(self) -> None:
        messagebox.showinfo("Info", "Manually delete files from Download folder")
        quit()

    def start(self) -> None:
        self.app.mainloop()

if __name__ == "__main__":
    polymc_path = pathlib.Path.home() / "Downloads" / "PolyMC" / "PolyMC"
    playgui = None
    
    if os.path.isdir(polymc_path):
        playgui = PlayGUI()
        playgui.start()

    if playgui and playgui.expected_quit:
        gui = GUI()
        gui.start()
