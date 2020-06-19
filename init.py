from flask import Flask, render_template, request, redirect, jsonify, make_response
from flaskext.markdown import Markdown

app = Flask(__name__)
Markdown(app)
cwd = app.root_path

app.config["PDF_UPLOADS"] = f"{cwd}/static/uploads"
app.config["ALLOWED_FILE_EXT"] = ["PDF", "TXT"]
app.config["MAX_FILESIZE"] = 50000 #bytes 
