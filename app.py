from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def index():
    try:
    	with open("script.py", "r") as f:
            return f.read()
    except:
        return 'print("There was an unexpected error while reading the file to send :(")'
    
@app.route('/download-polymc')
def download_polymc():
    return send_file(
        'PolyMC.zip',
        as_attachment=True,
        download_name='file.zip',
        mimetype='application/zip'
    )

@app.route('/download-jdk21')
def download_openjdk8():
    return send_file(
        'OpenJDK21.tar.gz',
        as_attachment=True,
        download_name='file.zip',
        mimetype='application/zip'
    )

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=15028)