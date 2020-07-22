from flask import Flask, render_template, request, redirect, flash#, jsonify, make_response

app = Flask(__name__)
cwd = app.root_path

app.config.from_object("config.ProductionConfig")

app.config["PDF_UPLOADS"] = f"{cwd}/static/uploads"
app.config["ALLOWED_FILE_EXT"] = ["PDF", "TXT"]
app.config["MAX_FILESIZE"] = 5 * 1024 * 1024#bytes (~5MB)
