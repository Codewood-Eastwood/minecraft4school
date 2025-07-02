# Created by Angadpal Tak
# version 1.22.3

import uuid
import threading
import time
from flask import Flask, send_file, render_template, request, make_response
# flake8: noqa: E501

app = Flask(__name__)

logins: dict[str, str] = {}
passwords: list[str] = ["caidon67", "grade3", "sixseven", "vedsucks123", "lovenatsuki", "130iq", "mnn3gkczLnH4", "ginger1"]
premium_passwords: list[str] = ["caidon67", "mnn3gkczLnH4", "ginger1", "vedsucks123"]

login_times: dict[str, float] = {}
template_returns: tuple[str] = ("minecraft", "deltarune", "miside", "madness-melee", "ddlc", "rust", "steam")

@app.before_request
def require_client_id():
    if request.endpoint in template_returns:
        if not request.cookies.get('client_id'):
            if request.endpoint != "login":
                return render_template('login.html')

def cleanup_logins():
    while True:
        now = time.time()
        expired = [uid for uid, t in login_times.items() if now - t > 3600]
        for uid in expired:
            logins.pop(uid, None)
            login_times.pop(uid, None)
        time.sleep(60)

threading.Thread(target=cleanup_logins, daemon=True).start()

def script_response(file):
    try:
        with open(file, "r") as f:
            script_content = f.read()
        return render_template(
            'script_response.html',
            script_content=script_content,
            filename=file,
            instructions="""
1. Open <a href="/image-help" target="_blank">Windows Powershell</a><br>
2. Paste the above code in when loaded<br>
3. Press enter, if it isn't lagging then something will happen<br>
4. For image help, click <a href="/image-help" target="_blank">here</a>
"""
        )

    except Exception as e:  # noqa: E722
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

        if password not in passwords:
            return render_template('login_failure.html')
        
        if password in logins.values():
            return render_template('login_failure.html')

        # Check for existing client ID cookie
        unique_id = request.cookies.get('client_id')
        if not unique_id:
            unique_id = str(uuid.uuid4())

        logins[unique_id] = password
        login_times[unique_id] = time.time()
        resp = make_response(render_template('login_success.html'))
        resp.set_cookie('client_id', unique_id, max_age=3600)  # 1 year
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
