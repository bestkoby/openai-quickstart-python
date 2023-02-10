import os

import openai
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static')

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        if request.form["action"] == "Generate images":
            prompt = request.form["prompt"]
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response["data"][0]["url"]
            return redirect(url_for("index", result=image_url))
        elif request.form["action"] == "Variation":
            # check if the post request has the file part
            if 'file' not in request.files:
                print('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            filename = secure_filename(file.filename)
            print(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            if file and allowed_file(file.filename):
                response = openai.Image.create_variation(
                    image=open(os.path.join(app.config['UPLOAD_FOLDER'],filename), "rb"),
                    n=1,
                    size="1024x1024"
                )
                image_url = response['data'][0]['url']
                return redirect(url_for("index", result=image_url))
    result = request.args.get("result")
    return render_template("index.html", result=result)

