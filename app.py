from flask import Flask, send_file, render_template

app = Flask(__name__)
# flake8: noqa: E501

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
def help():
    return render_template('help.html')


@app.route('/image-help')
def image_help():
    return render_template('image_help.html')


@app.route('/minecraft-py')
def download_minecraft_script():
    try:
        with open("minecraft/script.py", "r") as f:
            return f.read()
    except:  # noqa: E722
        return 'print("There was an unexpected error while reading the file to send :(")'  # noqa: E501


@app.route('/minecraft')  # Minecraft
def download_minecraft():
    return script_response("minecraft/run_minecraft_exe.ps")


@app.route('/minecraft-exe')
def download_script_exe():
    return send_file(
        'minecraft/script.mp3',
        as_attachment=True,
        download_name='script.mp3',
        mimetype='application/octet-stream'
    )


@app.route('/download-polymc')
def download_polymc():
    return send_file(
        'minecraft/PolyMC.zip',
        as_attachment=True,
        download_name='PolyMC.zip',
        mimetype='application/zip'
    )


@app.route('/download-jdk17')
def download_openjdk8():
    return send_file(
        'minecraft/OpenJDK17.zip',
        as_attachment=True,
        download_name='OpenJDK17.zip',
        mimetype='application/zip'
    )


@app.route('/deltarune')
def deltarune():
    return script_response("deltarune/run_deltarune_exe.ps")


@app.route('/deltarune-zip')
def deltarune_zip():
    return send_file(
        'deltarune/deltarunedemo.zip',
        as_attachment=True,
        download_name='deltarunedemo.zip',
        mimetype='application/zip'
    )


@app.route('/madness-melee')
def madness_melee():
    return script_response("madness-melee/run_madness_melee_exe.ps")


@app.route('/madness-melee-zip')
def madness_melee_zip():
    return send_file(
        'madness-melee/madness-melee.zip',
        as_attachment=True,
        download_name='madness-melee.zip',
        mimetype='application/zip'
    )


@app.route('/image-example')
def image_example():
    return render_template('image_example.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=15028)
