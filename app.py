# Created by Angadpal Tak
# version 1.29.8


import passwords
from flask import Flask, send_file, render_template, make_response, request, Response, abort, send_from_directory, abort
from local_logger import logger
from datetime import datetime, timezone, timedelta
import os; os.system('pip install psutil')
import re
from host_details import host_details
from werkzeug.utils import safe_join

# flake8: noqa: E501
app = Flask(__name__)

normal_games: tuple[str] = ("shiftatmidnight", "brotato", "madness-melee", "deltarune", "miside", "7zip", "solarsandbox", "ultrakill", "forzahorizon2", "granny")
premium_games: tuple[str] = ()
passwords_in_use: dict[str, int] = {}
DOWNLOAD_FOLDER = '/shared/hosted'

@app.before_request
def require_client_id():
    logger.info(f"Request to {request.endpoint} from {request.remote_addr}")
    if not request.cookies.get('password') and request.endpoint not in [
        'login', 'download_file'
    ]:
        return render_template('login.html')

    pass

@app.route('/')
def index():
    return render_template("login.html")

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
                           instructions="""
1. Open <a href="/image-help" target="_blank">Windows Powershell</a><br>
2. Paste the above code in when loaded<br>
3. Press enter, if it isn't lagging then something will happen<br>
4. For image help, you don't get any because i'm too lazy<br>
"""
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6767, debug=True)
