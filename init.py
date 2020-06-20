from flask import Flask, render_template, request, redirect, flash#, jsonify, make_response
from flaskext.markdown import Markdown

app = Flask(__name__)
Markdown(app) #in order to render the displacy render
cwd = app.root_path

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

print(f'\n**ENV is set to: {app.config["ENV"]}**\n')

app.config["PDF_UPLOADS"] = f"{cwd}/static/uploads"
app.config["ALLOWED_FILE_EXT"] = ["PDF", "TXT"]
app.config["MAX_FILESIZE"] = 50000 #bytes 
