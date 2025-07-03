# Created by Angadpal Tak
# version 1.25.1

import uuid
import threading
import time
import logging
from flask import Flask, send_file, render_template, request, make_response
import sys
from passwords import passwords, premium_passwords
# flake8: noqa: E501

app = Flask(__name__)

# Configure logger
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[94m",    # Blue
        logging.INFO: "\033[92m",     # Green
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",    # Red
        logging.CRITICAL: "\033[95m", # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"

file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(ColorFormatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger(__name__)

logins: dict[str, str] = {}

login_times: dict[str, float] = {}
template_returns: tuple[str] = ("minecraft", "deltarune", "miside", "madness_melee", "ddlc", "rust", "steam", "bluestacks", "warthunder")

@app.before_request
def require_client_id():
    logger.info(f"Request to {request.endpoint} from {request.remote_addr}")
    if request.endpoint in template_returns:
        unique_id = request.cookies.get('client_id')
        if not unique_id:
            if request.endpoint != "login":
                logger.warning(f"Unauthorized access attempt to {request.endpoint} from {request.remote_addr}")
                return render_template('login.html')
        if unique_id not in logins:
            return render_template('expired.html')

def cleanup_logins():
    while True:
        now = time.time()
        expired = [uid for uid, t in login_times.items() if now - t > 3600]
        for uid in expired:
            logger.info(f"Session expired for client_id: {uid}")
            logins.pop(uid, None)
            login_times.pop(uid, None)
        time.sleep(60)

threading.Thread(target=cleanup_logins, daemon=True).start()

def add_eta_to_script(script_content, eta):
    # Add ETA as a comment at the top of the script
    lines = script_content.splitlines()
    if lines and lines[0].startswith('# ETA:'):
        lines[0] = f'# ETA: {eta}'
    else:
        lines = [f'# ETA: {eta}'] + lines
    return '\n'.join(lines)

def get_eta_for_script(file):
    eta_map = {
        "games/minecraft/run_minecraft_exe.ps": "~2-3 minutes",
        "games/deltarune/run_deltarune_exe.ps": "~1-2 minutes",
        "games/miside/run_miside_exe.ps": "~1 minute",
        "games/madness-melee/run_madness_melee_exe.ps": "~1-2 minutes",
        "games/ddlc/run_ddlc_exe.ps": "~1 minute",
        "games/rust/run_rust_exe.ps": "~3-5 minutes",
        "games/steam/run_steam_exe.ps": "~2-4 minutes",
        "games/bluestacks/run_bluestacks_exe.ps": "~2-3 minutes",
        "games/warthunder/run_warthunders_exe.ps": "~2-4 minutes",
    }
    return eta_map.get(file, "~1-3 minutes")

def script_response(file):
    try:
        with open(file, "r") as f:
            script_content = f.read()
        eta = get_eta_for_script(file)
        script_content = add_eta_to_script(script_content, eta)
        logger.info(f"Served script: {file} (ETA: {eta})")
        return render_template(
            'script_response.html',
            script_content=script_content,
            filename=file,
            instructions=f"""
1. Open <a href=\"/image-help\" target=\"_blank\">Windows Powershell</a><br>
2. Paste the above code in when loaded<br>
3. Press enter, if it isn't lagging then something will happen<br>
4. For image help, click <a href=\"/image-help\" target=\"_blank\">here</a>
"""
        )

    except Exception as e:  # noqa: E722
        logger.error(f"Error serving script {file}: {e}")
        print("**** ERROR ****")
        return render_template(
            'script_response.html',
            script_content=f'Error: {str(e)}',
            filename=file
        )


@app.route('/')
def root():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        logger.info(f"Login attempt with password: {password} from {request.remote_addr}")
        if password not in passwords():
            logger.warning(f"Failed login attempt with password: {password} from {request.remote_addr}")
            return render_template('login_failure.html')
        if password in logins.values():
            logger.warning(f"Duplicate login attempt with password: {password} from {request.remote_addr}")
            return render_template('login_failure.html')
        # Check for existing client ID cookie
        unique_id = request.cookies.get('client_id')
        if not unique_id:
            unique_id = str(uuid.uuid4())
        logins[unique_id] = password
        login_times[unique_id] = time.time()
        logger.info(f"Login success for client_id: {unique_id} from {request.remote_addr}")
        resp = make_response(render_template('login_success.html'))
        resp.set_cookie('client_id', unique_id, max_age=3600)
        return resp

    return render_template('login.html')


@app.route('/index')
def index():
    return render_template('help.html')


@app.route('/image-help')
def image_help():
    return render_template('image_help.html')


@app.route('/minecraft-py')
def download_minecraft_script():
    try:
        with open("games/minecraft/script.py", "r") as f:
            return f.read()
    except:  # noqa: E722
        return 'print("There was an unexpected error while reading the file to send :(")'  # noqa: E501


@app.route('/minecraft')  # Minecraft
def download_minecraft():
    unique_id = request.cookies.get('client_id')
    if not unique_id:
        return render_template("login.html")
    if logins[unique_id] not in premium_passwords:
        return render_template("premium_requirement.html")
    return script_response("games/minecraft/run_minecraft_exe.ps")


@app.route('/minecraft-exe')
def download_script_exe():
    return send_file(
        'games/minecraft/script.mp3',
        as_attachment=True,
        download_name='script.mp3',
        mimetype='application/octet-stream'
    )


@app.route('/gta4')  # Minecraft
def download_gta4():
    unique_id = request.cookies.get('client_id')
    if not unique_id:
        return render_template("login.html")
    if logins[unique_id] not in premium_passwords:
        return render_template("premium_requirement.html")
    return script_response("games/gta/run_gta4_exe.ps")


@app.route('/download-polymc')
def download_polymc():
    return send_file(
        'games/minecraft/PolyMC.zip',
        as_attachment=True,
        download_name='PolyMC.mp3',
        mimetype='application/mp3'
    )


@app.route('/download-jdk17')
def download_openjdk8():
    return send_file(
        'games/minecraft/OpenJDK17.zip',
        as_attachment=True,
        download_name='OpenJDK17.mp3',
        mimetype='application/mp3'
    )


@app.route('/deltarune')
def deltarune():
    return script_response("games/deltarune/run_deltarune_exe.ps")


@app.route('/deltarune-zip')
def deltarune_zip():
    return send_file(
        'games/deltarune/deltarunedemo.zip',
        as_attachment=True,
        download_name='deltarunedemo.zip',
        mimetype='application/zip'
    )


@app.route('/bluestacks')
def bluestacks():
    return script_response("games/bluestacks/run_bluestacks_exe.ps")


@app.route('/bluestacks-exe')
def bluestacks_exe():
    return send_file(
        'games/bluestacks/bluestacks.exe',
        as_attachment=True,
        download_name='bluestacks.mp3',
        mimetype='application/mp3'
    )


@app.route('/warthunder')
def warthunder():
    return script_response("games/warthunder/run_warthunder_exe.ps")


@app.route('/warthunder-exe')
def warthunder_exe():
    return send_file(
        'games/warthunder/warthunder.exe',
        as_attachment=True,
        download_name='warthunder.mp3',
        mimetype='application/mp3'
    )


@app.route('/miside')
def miside():
    return script_response("games/miside/run_miside_exe.ps")

@app.route('/miside-zip')
def miside_zip():
    return send_file(
        'games/miside/miside.zip',
        as_attachment=True,
        download_name='miside.zip',
        mimetype='application/zip'
    )


@app.route('/madness-melee')
def madness_melee():
    return script_response("games/madness-melee/run_madness_melee_exe.ps")


@app.route('/madness-melee-zip')
def madness_melee_zip():
    return send_file(
        'games/madness-melee/madness-melee.zip',
        as_attachment=True,
        download_name='madness-melee.zip',
        mimetype='application/zip'
    )


@app.route('/ddlc')
def ddlc():
    return script_response("games/ddlc/run_ddlc_exe.ps")

@app.route('/ddlc-zip')
def ddlc_zip():
    return send_file(
        'games/ddlc/DDLC.zip',
        as_attachment=True,
        download_name='DDLC.zip',
        mimetype='application/zip'
    )


@app.route('/rust')
def rust():
    unique_id = request.cookies.get('client_id')
    if logins[unique_id] not in premium_passwords:
        return render_template("premium_requirement.html")
    return script_response("games/rust/run_rust_exe.ps")

@app.route('/rust-tar')
def rust_tar():
    return send_file(
        'games/rust/rust.tar',
        as_attachment=True,
        download_name='rust.tar',
        mimetype='application/tar'
    )


@app.route('/steam')
def steam():
    unique_id = request.cookies.get('client_id')
    if not unique_id:
        return render_template("login.html")
    if logins[unique_id] not in premium_passwords:
        return render_template("premium_requirement.html")
    return script_response("games/steam/run_steam_exe.ps")


@app.route('/steam-zip')
def steam_zip():
    return send_file(
        'games/steam/Steam.exe',
        as_attachment=True,
        download_name='Steam.zip',
        mimetype='application/zip'
    )


@app.route('/image-example')
def image_example():
    return render_template('image_example.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=15028, debug=True)
