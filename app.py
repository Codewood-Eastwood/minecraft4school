# Created by Angadpal Tak
# version 1.26.1


from flask import Flask, send_file, render_template, make_response, request
from passwords import passwords, premium_passwords
from local_logger import logger
from datetime import datetime, timezone, timedelta

# flake8: noqa: E501
app = Flask(__name__)

normal_games: tuple[str] = ("7zip", "deltarune", "madness_melee")
premium_games: tuple[str] = ("hoi4", "minecraft", "rust", "sims4", "gta4")
passwords_in_use: dict[str, int] = {}

@app.before_request
def require_client_id():
    logger.info(f"Request to {request.endpoint} from {request.remote_addr}")
    if not request.cookies.get('password') and request.endpoint != "login":
        return render_template('login.html')

    pass

@app.route('/')
def index():
    return render_template("login.html")


@app.route('/games')
def games():
    return render_template("help.html")


@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    if password:
        if password in passwords():
            if password in passwords_in_use.values():
                return render_template("login.html", error="Password will expire in: {} minutes".format(
                    int((list(passwords_in_use.keys())[list(passwords_in_use.values()).index(password)] - datetime.now(timezone.utc)).total_seconds() // 60)
                ))
            resp = make_response(render_template("help.html"))
            resp.headers["Location"] = "/games"
            resp.status_code = 302
            resp.set_cookie("password", password)

            password_created = datetime.now(timezone.utc)
            expiration_time = password_created + timedelta(minutes=55)

            passwords_in_use[expiration_time] = password

            return resp
        else:
            return render_template("login.html", error="Invalid password")
    return render_template("login.html", error="Please enter a password")

@app.route('/get-script', methods=['POST'])
def get_script():
    game = request.form.get('game')
    password = request.cookies.get('password')
    if game in premium_games and password not in premium_passwords:
        return render_template("premium_requirement.html")
    
    script_path = f"scripts/run_{game}_exe.ps"
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
    except FileNotFoundError:
        return render_template("script_response.html",
                               filename=script_path,
                               script_content="Script file not found.")
    return render_template("script_response.html",
                           filename=script_path,
                           script_content=script_content)
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=15028, debug=True)
