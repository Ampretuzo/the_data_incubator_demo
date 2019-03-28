import io
import json
import re
import mimetypes

from flask import Flask, send_file
from flask import Response, request
from werkzeug.utils import secure_filename


app = Flask(__name__)


@app.route("/")
def root():
    """This is a workaround, production system must use webserver like nginx
    for serving static files"""
    return app.send_static_file("index.html")


def _json_response(response_body, status=200):
    if type(response_body) is dict:
        json_str = json.dumps(response_body)
    else:
        json_str = response_body
    return Response(status=status, response=json_str, content_type="application/json")


@app.route("/img/", methods=["POST"])
def img():
    if "img" not in request.files:
        return _json_response({"img": "Required"}, 400)
    img = request.files["img"]
    if not img.filename:
        return _json_response({"img": "Select a file"}, 400)
    filename = secure_filename(img.filename)
    if re.match(r"image/.+", mimetypes.guess_type(filename)[0]) is None:
        return _json_response({"img": "Unsupported file extension"}, 400)
    return send_file(
        io.BytesIO(img.stream.read()),
        attachment_filename=filename,
        mimetype=img.mimetype,
    )


@app.route("/status/", methods=["GET"])
def status():
    return _json_response({"status": "UP"})
