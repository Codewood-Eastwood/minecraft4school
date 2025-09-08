import io
import urllib.request
from PIL import Image
import customtkinter as ctk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Game data (mirrored from help.html)
GAMES = [
    {
        "name": "Games4School App",
        "desc": (
            "Progress saving with cloud uploads, easier + faster downloads, "
            "etc.."
        ),
        "img": "static/images/app.png",
        "download_time": "~0.67 seconds",
        "downloadable": False,
    },
    {
        "name": "Shift at Midnight",
        "desc": "CATCH THE DOPPELGANGERS IN THIS 3D HORROR",
        "img": (
            "https://img.itch.zone/aW1nLzIxNzk3Mzc0LnBuZw==/"
            "original/NufRDr.png"
        ),
        "download_time": "~69 seconds",
        "downloadable": True,
    },
    {
        "name": "Brotato",
        "desc": (
            "A rougelike shooter game where you control a potato who fights "
            "against aliens."
        ),
        "img": (
            "https://img.itch.zone/aW1nLzE3MjI1OTYxLmpwZw==/"
            "315x250%23c/YqL6JE.jpg"
        ),
        "download_time": "~6m 41s",
        "downloadable": True,
    },
    {
        "name": "Ultrakill",
        "desc": "A fast-paced ultraviolent old school FPS (shooter)",
        "img": "https://media.indiedb.com/images/games/1/74/73138/mkGtq6.jpg",
        "download_time": "~20m 53s",
        "downloadable": True,
    },
    {
        "name": "Forza Horizon 2",
        "desc": (
            "A 2014 racing video game developed for Microsoft's Xbox One and "
            "Xbox 360 consoles."
        ),
        "img": (
            "https://store-images.s-microsoft.com/image/apps.6287."
            "63666767995551875.0b03e540-65d9-46bc-bd9f-88298b0f8395."
            "296de0bb-2d82-4de4-8419-768684865655"
        ),
        "download_time": "~1 hour",
        "downloadable": True,
    },
    {
        "name": "Granny",
        "desc": (
            "A first-person survival horror game where players must escape "
            "from a sinister old woman's house"
        ),
        "img": (
            "https://play-lh.googleusercontent.com/asizZn0YOpPiBoOae-"
            "QbuPtyuh6tEhdswfYW_0cXwkADerTmCEVR7idTxxMnTDH1m90v"
        ),
        "download_time": "~5m 56s",
        "downloadable": True,
    },
    # Old Games
    {
        "name": "Madness Melee",
        "desc": "2D combat with lots of blood",
        "img": (
            "https://img.itch.zone/aW1nLzEwMjY4NDM0LnBuZw==/"
            "315x250%23c/1L35qR.png"
        ),
        "download_time": "~67 seconds",
        "downloadable": True,
    },
    {
        "name": "Deltarune",
        "desc": (
            "Fight alongside new characters in UNDERTALE's parallel story, "
            "DELTARUNE!"
        ),
        "img": (
            "https://img.itch.zone/aW1hZ2UvMTE5MzgyOC82OTg0NDIwLnBuZw==/"
            "347x500/hxV8FS.png"
        ),
        "download_time": "~1m 17s",
        "downloadable": True,
    },
    {
        "name": "Miside",
        "desc": "Gooner game. I didn't want to add an icon",
        "img": (
            "https://img.itch.zone/aW1nLzEyOTQzOTYzLnBuZw==/"
            "315x250%23c/uY7ctb.png"
        ),
        "download_time": "~2m 28s",
        "downloadable": True,
    },
    {
        "name": "Minecraft",
        "desc": "You know what Minecraft is",
        "img": (
            "https://cdn2.steamgriddb.com/file/sgdb-cdn/icon_thumb/"
            "0a17ad0fa0870b05f172deeb05efef8e.png"
        ),
        "download_time": "~17m 46s",
        "downloadable": False,
    },
    {
        "name": "Solar Sandbox",
        "desc": "A game where you can interact with physics in space.",
        "img": (
            "https://img.itch.zone/aW1nLzIyNDE4OTgxLmdpZg==/"
            "original/DCQDYF.gif"
        ),
        "download_time": "~50 seconds",
        "downloadable": True,
    },
    # Tools
    {
        "name": "7-Zip",
        "desc": "Used to install large games",
        "img": "https://logodix.com/logo/1966283.png",
        "download_time": "~0.53 seconds",
        "downloadable": True,
    },
]


def get_image(img_url, size=(260, 150)):
    """Fetch image from URL or local file and resize to given size."""
    try:
        if img_url.startswith("http"):
            with urllib.request.urlopen(img_url) as u:
                raw = u.read()
            im = Image.open(io.BytesIO(raw)).convert("RGBA")
        else:
            im = Image.open(img_url).convert("RGBA")

        return ctk.CTkImage(light_image=im, dark_image=im, size=size)

    except Exception as e:
        print(f"Failed to load image {img_url}: {e}")
        return None


class GameCard(ctk.CTkFrame):
    def __init__(self, master, game, *args, **kwargs):
        super().__init__(
            master,
            fg_color="#181830",
            border_width=3,
            border_color="#00f0ff",
            corner_radius=14,
            *args,
            **kwargs
        )
        self.grid_propagate(False)

        self.img = get_image(game["img"])
        if self.img:
            img_label = ctk.CTkLabel(self, image=self.img, text="")
            img_label.pack(pady=(14, 6))

        ctk.CTkLabel(
            self,
            text=game["name"],
            font=("System", 18, "bold"),
            text_color="#00f0ff",
        ).pack(pady=(6, 4))

        ctk.CTkLabel(
            self,
            text=game["desc"],
            font=("System", 13),
            text_color="#fff",
            wraplength=260,
            justify="center",
        ).pack(pady=(0, 12))

        if game["downloadable"]:
            ctk.CTkButton(
                self,
                text="Download",
                fg_color="#00f0ff",
                text_color="#0a0a1a",
            ).pack(pady=(0, 8))
        else:
            ctk.CTkButton(
                self,
                text="Coming soon" if "App" in game["name"] else "More",
                fg_color="#222",
                text_color="#fff",
                state="disabled",
            ).pack(pady=(0, 8))

        ctk.CTkLabel(
            self,
            text=game["download_time"],
            font=("Tomorrow", 11),
            text_color="#aaa",
        ).pack(pady=(0, 12))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Games4School - Game Portal")
        self.geometry("1400x900")
        self.configure(fg_color="#0a0a1a")
        self.resizable(False, False)

        title = ctk.CTkLabel(
            self,
            text="Games for Eastwood",
            font=("System", 36, "bold"),
            text_color="#00f0ff",
        )
        title.pack(pady=(30, 12))

        subtitle = ctk.CTkLabel(
            self,
            text="Don't be stupid",
            font=("System", 20),
            text_color="#ff00f0",
        )
        subtitle.pack(pady=(0, 20))

        scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="#0a0a1a", width=1350, height=700
        )
        scroll_frame.pack(padx=25, pady=15, fill="both", expand=True)

        cols = 3
        for i, game in enumerate(GAMES):
            row, col = divmod(i, cols)
            card = GameCard(scroll_frame, game, width=340, height=400)
            card.grid(row=row, column=col, padx=30, pady=30)


if __name__ == "__main__":
    app = App()
    app.mainloop()
