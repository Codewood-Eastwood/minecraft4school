# Created by Angadpal Tak
# version 1.30.6


import passwords
from flask import Flask, send_file, render_template, make_response, request, Response, abort, send_from_directory, abort
from local_logger import logger
from datetime import datetime, timezone, timedelta
import re
import os
from host_details import host_details
from werkzeug.utils import safe_join

# flake8: noqa: E501
app = Flask(__name__)

normal_games: tuple[str] = ("shiftatmidnight", "brotato", "madness-melee", "deltarune", "miside", "7zip", "solarsandbox", "ultrakill", "forzahorizon2", "granny", "minecraft-1.16.5", "app")
premium_games: tuple[str] = ()
passwords_in_use: dict[str, int] = {}
DOWNLOAD_FOLDER = '/shared/hosted'

banners = {
    'shiftatmidnight': 'static/banners/shiftatmidnight.png',
    'brotato': 'static/banners/brotato.jpg',
    'madness-melee': 'static/banners/madness-melee.avif',
    'deltarune': 'static/banners/deltarune.png',
    'miside': 'static/banners/miside.png',
    '7zip': 'static/banners/7zip.png',
    'solarsandbox': 'static/banners/solarsandbox.png',
    'ultrakill': 'static/banners/ultrakill.jpg',
    'forzahorizon2': 'static/banners/forzahorizon.jpeg',
    'granny': 'static/banners/granny.jpg',
    'minecraft-1.16.5': 'static/banners/minecraft-1.16.5.jpg',
    'app': 'static/images/app.png'
}

screenshots = {
    'shiftatmidnight': ['https://img.itch.zone/aW1hZ2UvMzY2MzAwOC8yMTc5NzM4MC5wbmc=/347x500/3zlcWM.png', 'https://img.itch.zone/aW1hZ2UvMzY2MzAwOC8yMTc5NzM3OC5wbmc=/347x500/BMi4tj.png', 'https://img.itch.zone/aW1hZ2UvMzY2MzAwOC8yMTc5NzM4Ny5wbmc=/347x500/CXkCOR.png', 'https://img.itch.zone/aW1hZ2UvMzY2MzAwOC8yMTc5NzM4My5wbmc=/347x500/G1ClGw.png'],
    'brotato': ['https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1942280/ss_79be0eea0299da76bc50cef160fb669509f74e0b.600x338.jpg?t=1754906841', 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1942280/ss_61ad3d242282311207828c1a7d87c1c9d7b4d8bf.600x338.jpg?t=1754906841', 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1942280/ss_9d7d1532397e65d39a3b63e3b25bd3adf7a81b37.600x338.jpg?t=1754906841', 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1942280/ss_8d4467bb3278d7f50bf457337bbe76d0053ebd83.600x338.jpg?t=1754906841'],
    'madness-melee': ['https://img.itch.zone/aW1hZ2UvMTc0NTE2Ny8xMDI2ODQ1My5wbmc=/347x500/cya8yw.png', 'https://img.itch.zone/aW1hZ2UvMTc0NTE2Ny8xMDI2ODQ1NC5wbmc=/347x500/xkRb97.png', 'https://img.itch.zone/aW1hZ2UvMTc0NTE2Ny8xMDI2ODQ1NS5wbmc=/347x500/0jOyHX.png', 'https://img.itch.zone/aW1hZ2UvMTc0NTE2Ny8xMDI2ODQ1Ni5wbmc=/347x500/lLMrht.png'],
    'deltarune': ['https://img.itch.zone/aW1hZ2UvMTE5MzgyOC82OTg0NDIwLnBuZw==/347x500/hxV8FS.png', 'https://img.itch.z  ne/aW1hZ2UvMTE5MzgyOC82OTg0NDE5LnBuZw==/original/R%2BOobw.png', 'https://img.itch.zone/aW1hZ2UvMTE5MzgyOC82OTg0NDE2LnBuZw==/347x500/s4Hn0N.png', 'https://img.itch.zone/aW1hZ2UvMTE5MzgyOC82OTg0NDE3LnBuZw==/347x500/0xY9tq.png'],
    'miside': ['https://img.itch.zone/aW1nLzEyNjM4MDkxLnBuZw==/original/FUX5gl.png', 'https://img.itch.zone/aW1nLzEyNjM4MDk5LnBuZw==/original/sv2y3V.png', 'https://img.itch.zone/aW1nLzEyNjM5ODc4LnBuZw==/original/v8zsxu.png', 'https://static.deltiasgaming.com/2024/12/ss_0052fb30551d9d7bb6e342ee47005f57856d0a16.1920x1080.jpg'],
    '7zip': ['https://i.ytimg.com/vi/Ng43hSsApMY/maxresdefault.jpg', 'https://i.ytimg.com/vi/V1zICMxPfNs/maxresdefault.jpg', 'https://nerdschalk.com/content/images/wp-content/uploads/2022/10/7zip-win-11-5.png', 'https://athomecomputer.co.uk/wp-content/uploads/2023/01/7zip-Windows-11.png'],
    'solarsandbox': ['https://img.itch.zone/aW1nLzIxMjk0NTQ4LmdpZg==/original/g789JN.gif', 'https://img.itch.zone/aW1nLzIxMjk0NDg3LmdpZg==/original/61JKDT.gif', 'https://img.itch.zone/aW1nLzIyNjI3NTkxLmdpZg==/original/rKxOhX.gif', 'https://img.itch.zone/aW1nLzIyNjI3Mzc1LnBuZw==/original/4yXUyx.png'],
    'ultrakill': ['https://images.gog-statics.com/550f470ca2e97cdc7a6eb8848f8b63e78a4729a80b786856968e299f657aa9cd_product_card_v2_mobile_slider_639.jpg', 'https://images4.alphacoders.com/135/1350600.png', 'https://3dnews.ru/assets/external/illustrations/2024/01/18/1098939/ULTRAKILL_screenshot_onpage_2.jpg', 'https://i.playground.ru/i/screenshot/107435/ultrakill.jpg?1200x675'],
    'forzahorizon2': ['https://gamefabrique.com/images/video/original/forza-horizon-2.mp4', 'https://gamefabrique.com/storage/screenshots/pc/forza-horizon-2-02.webp', 'https://gamefabrique.com/screenshots2/pc/forza-horizon-2-08.big.jpg', 'https://gamefabrique.com/screenshots2/pc/forza-horizon-2-04.big.jpg'],
    'granny': ['https://cdn.cloudflare.steamstatic.com/steam/apps/2110820/ss_79f289f593de40cdb7d58c330c9fad2db5724ff5.1920x1080.jpg?t=1695852924', 'https://wallpapers.com/images/hd/granny-pictures-crnny099clfn963l.jpg', 'https://thvnext.bing.com/th/id/OIP.GMu5C9i9-bfofgyC3BCP5wHaEK?w=278&h=180&c=7&r=0&o=5&cb=ucfimg2&pid=1.7&ucfimg=1', 'https://imag.malavida.com/mvimgbig/download-fs/granny-20748-3.jpg'],
    'minecraft-1.16.5': ['https://i.ytimg.com/vi/gouhmtcbKDM/maxresdefault.jpg','https://static.planetminecraft.com/files/image/minecraft/project/2021/511/14797291_l.webp','https://static.planetminecraft.com/files/image/minecraft/project/2021/511/14810628_l.jpg','https://uk.minecraft.wiki/images/thumb/1.16.5_(Java_Edition)_%D0%BC%D0%B5%D0%BD%D1%8E.png/640px-1.16.5_(Java_Edition)_%D0%BC%D0%B5%D0%BD%D1%8E.png?28ddc'],
    'app': ['','','','']
}

descriptions = {
    'shiftatmidnight': """CATCH THE DOPPELGANGERS IN THIS 3D HORROR.
Demo Playthrough:   ~40 mins
•    Serve customers, spot the Doppelgangers. 
•    Question them, check their Paperwork. 
•    Board up, lay Traps and Hide.""",
    'brotato': """Brotato is a top-down arena shooter roguelite where you play a potato wielding up to 6 weapons at a time to fight off hordes of aliens. Choose from a variety of traits and items to create unique builds and survive until help arrives.""",
    'madness-melee': """Madness Melee is a 2D madness combat fangame.

Enter the new Sleepwalker Program, and fight through 100 arena waves while upgrading your character the whole way through! Unlock new characters to beat the arena with, after completing the game.""",
    'deltarune': """Dive into the parallel story to UNDERTALE! Fight or spare your way through action-packed battles as you explore a mysterious world alongside an endearing cast of new and familiar characters. Chapters 1-4 will be available at launch, with more planned as free updates!

A massive soundtrack and story written by Toby Fox!
Meet new and endearing main characters, as well as familiar faces like Toriel, Sans, and more. Huh? Papyrus? No, he's busy. Sorry
Smooth and expressive pixel-animation by Temmie. She also has a new hat (in-game)
A linear, chapter-based system that you can pick up from anywhere.\
Creative bullet-dodging based battles inspired by games like the Touhou series and Chrono Trigger.
Jevilishly difficult hidden bosses.
And...
...
... only 1 ending...?""",
    'miside': """Let's imagine that you have a game in which you care for a character. But could you imagine one day getting into that game yourself?\n
The developers describe the content like this:

- In the settings there is an option to enable censorship.
- The game contains murder scenes, also present: blood, corpses, dismemberment.""",
    '7zip': 'Fast processing for .zip, .tar, .7zip, etc.. files',
    'solarsandbox': """Solar Sandbox is a game where you can interact with physics in space.""",
    'ultrakill': "ULTRAKILL is a fast-paced ultraviolent retro FPS combining the skill-based style scoring from character action games with unadulterated carnage inspired by the best shooters of the '90s. Rip apart your foes with varied destructive weapons and shower in their blood to regain your health.",
    'forzahorizon2': "Forza Horizon 2 is a racing video game, featuring an open world environment.[2] The player participates in the Horizon Festival, a fictional racing competition set within Southern France and Northern Italy.[3] The game has approximately three times more drivable area than that of its predecessor Forza Horizon, with events set in Provence, Liguria and Côte d'Azur (Nice) along with scaled down towns of Sisteron and Saint-Martin-du-Var. ",
    'granny': """Welcome to Granny. Granny keeps you locked in her house right now. You wake up in a dark room, the only thing that lights up the room is your flashlight lying on a table, you have a headache and it feels like someone has hit you in the head. As a result, you must make your way out of her home, but you must be cautious and remain silent. She hears everything. If you drop anything on the floor, she will hear it and hurry up to you. You may conceal yourselves in closets or beneath beds, but you must be cautious that she does not discover where you are hide yourself.""",
    'minecraft-1.16.5': """Minecraft 1.16, known as the Nether Update, was released on June 23, 2020. It overhauled the Nether dimension, introducing new biomes, mobs, and materials to enhance gameplay.

Key Features:

New Biomes: The Nether now includes the Crimson Forest, Warped Forest, Soul Sand Valley, and Basalt Deltas, each with unique terrain and resources.

New Mobs: Introduced Piglins, Hoglins, Zoglins, and Striders, adding depth to Nether encounters.

Netherite: A new material stronger than diamond, crafted from ancient debris found in the Nether, offering enhanced durability for tools and armor.

Crying Obsidian & Respawn Anchor: Crying Obsidian can be used to craft Respawn Anchors, allowing players to set spawn points in the Nether.

New Blocks & Structures: Added blocks like Blackstone and structures such as Bastion Remnants and Ruined Portals, enriching exploration and building options.""",
    'app': 'App to make downloading games as easy as possible'
}

@app.before_request
def require_client_id():
    logger.info(f"Request to {request.endpoint} from {request.remote_addr}")
    if not request.cookies.get('password'):
        if request.endpoint not in ['login'] and not request.path.startswith('/download/'):
            return render_template('login.html')

    pass

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/minecraft')
def minecraft():
    return render_template("minecraft.html")

@app.route('/download/<path:filename>')
def download_file(filename):
    # Make sure the file exists
    file_path = safe_join(DOWNLOAD_FOLDER, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

@app.route('/passwords')
def password_manager(error=None):
    password = request.cookies.get('password')
    if password and password == "mnn3gkczLnH4":
        all_passwords = passwords.get_passwords()
        premium_passwords = passwords.get_premium_passwords()
        normal_passwords = [p for p in all_passwords if not p.get('premium')]

        return render_template(
            'password_builder.html',
            all_passwords=normal_passwords,
            premium_passwords=premium_passwords,
            error=error if error else None,
            host_details=host_details
        )
    else:
        return render_template("login.html")


@app.route('/passwords/search')
def search_passwords():
    query = request.args.get('query', '').lower()
    all_passwords = passwords.get_passwords()
    premium_passwords = passwords.get_premium_passwords()
    if query:
        filtered_normal = [p for p in all_passwords if not p.get('premium') and (query in p['name'].lower() or query in p['password'].lower())]
        filtered_premium = [p for p in premium_passwords if query in p['name'].lower() or query in p['password'].lower()]
    else:
        filtered_normal = [p for p in all_passwords if not p.get('premium')]
        filtered_premium = premium_passwords
    return render_template('password_builder.html',
        all_passwords=filtered_normal,
        premium_passwords=filtered_premium,
        error=None,
        host_details=host_details
    )


@app.route('/work')
def work():
    return render_template("help.html")


@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    if password:
        if password in [password["password"] for password in passwords.get_passwords()]:
            if password in passwords_in_use.values() and password != "mnn3gkczLnH4":
                return render_template("login.html", error="Password will expire in: {} minutes".format(
                    int((list(passwords_in_use.keys())[list(passwords_in_use.values()).index(password)] - datetime.now(timezone.utc)).total_seconds() // 60)
                ))
            resp = make_response(render_template("help.html"))
            resp.headers["Location"] = "/work"
            resp.status_code = 302
            resp.set_cookie("password", password)

            password_created = datetime.now(timezone.utc)
            expiration_time = password_created + timedelta(minutes=55)

            passwords_in_use[expiration_time] = password

            return resp
        else:
            return render_template("login.html", error="Invalid password")
    return render_template("login.html", error="Please enter a password")

def send_file_partial(path):
    # Helper to support HTTP Range requests for download resuming
    range_header = request.headers.get('Range', None)
    if not os.path.exists(path):
        abort(404)
    file_size = os.path.getsize(path)
    if not range_header:
        return send_file(path, as_attachment=True)
    byte1, byte2 = 0, None
    m = None
    m = re.search(r'bytes=(\d+)-(\d*)', range_header)
    if m:
        g = m.groups()
        byte1 = int(g[0])
        if g[1]:
            byte2 = int(g[1])
    length = file_size - byte1
    if byte2 is not None:
        length = byte2 - byte1 + 1
    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)
    rv = Response(data,
                  206,
                  mimetype='application/octet-stream',
                  content_type='application/octet-stream',
                  direct_passthrough=True)
    rv.headers.add('Content-Range', f'bytes {byte1}-{byte1 + length - 1}/{file_size}')
    rv.headers.add('Accept-Ranges', 'bytes')
    rv.headers.add('Content-Length', str(length))
    rv.headers.add('Content-Disposition', f'attachment; filename="{os.path.basename(path)}"')
    return rv

@app.route('/download-script/<game>')
def download_script(game):
    script_path = f"scripts/run_{game}_exe.ps"
    return send_file_partial(script_path)

@app.route('/get-script', methods=['POST'])
def get_script():
    game = request.form.get('game')
    password = request.cookies.get('password')
    if game in premium_games and password not in [password["password"] for password in passwords.get_premium_passwords()]:
        return render_template("premium_requirement.html")
    
    script_path = f"scripts/run_{game}_exe.ps"
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
    except FileNotFoundError:
        return render_template("script_response.html",
                               filename=script_path,
                               script_content="Script file not found.")
    download_url = f"/download-script/{game}"
    return render_template("script_response.html",
                           filename=script_path,
                           script_content=script_content,
                           download_url=download_url,
                           banner=banners[game],
                           description=descriptions[game],
                           screenshot1=screenshots[game][0],
                           screenshot2=screenshots[game][1],
                           screenshot3=screenshots[game][2],
                           screenshot4=screenshots[game][3]
                           )
    

def restart_app():
    """Restart the current application by incrementing version on line 2."""
    logger.warning("Restarting app...")

    filename = 'app.py'
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)


@app.route('/passwords/exec-code', methods=['POST'])
def exec_code():
    result = eval(request.form.get('custom_code'))
    return password_manager("Success" if result is None else result)


@app.route('/passwords/add', methods=['POST'])
def add_password():
    password = request.cookies.get('password')
    if not (password and password == "mnn3gkczLnH4"):
        return render_template("login.html")
    name = request.form.get('name')
    pw = request.form.get('password')
    is_premium = request.form.get('is_premium') == 'on'
    error = None
    if not name or not pw:
        error = "Both name and password are required."
    else:
        try:
            if is_premium:
                passwords.add_premium_password(name, pw)
            else:
                passwords.add_password(name, pw)
            restart_app()
        except Exception as e:
            error = str(e)
    return password_manager(error)

@app.route('/passwords/edit', methods=['POST'])
def edit_password():
    password = request.cookies.get('password')
    if not (password and password == "mnn3gkczLnH4"):
        return render_template("login.html")
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')
    new_password = request.form.get('new_password')
    is_premium = request.form.get('is_premium') == 'on'
    error = None
    if not old_name or not new_name or not new_password:
        error = "All fields are required."
    else:
        try:
            if is_premium:
                passwords.edit_premium_password(old_name, new_name, new_password)
            else:
                passwords.edit_password(old_name, new_name, new_password)
            restart_app()
        except Exception as e:
            error = str(e)
    return password_manager(error)

@app.route('/passwords/delete', methods=['POST'])
def delete_password():
    password = request.cookies.get('password')
    if not (password and password == "mnn3gkczLnH4"):
        return render_template("login.html")
    name = request.form.get('name')
    is_premium = request.form.get('is_premium') == 'on'
    error = None
    if not name:
        error = "Name is required."
    else:
        try:
            if is_premium:
                passwords.delete_premium_password(name)
            else:
                passwords.delete_password(name)
            restart_app()
        except Exception as e:
            error = str(e)
    return password_manager(error)

@app.route('/static/<path:filename>')
def get_static_image(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6767, debug=True)
