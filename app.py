from werkzeug.utils import secure_filename
from functions import *

title = 'NLP PDF journal article keyword extraction'

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html', the_title=title)

@app.route("/upload-pdf", methods=["GET", "POST"])
def upload_pdf():
    if request.method == "POST":
        if request.files:
            if not allowed_filesize(request.cookies.get("filesize")): #based on filesize
                msg = 'File exceeded maximum size'
                print(msg)
                flash(msg, 'warning')
                return redirect('/', code=302)

            pdf_file = request.files["pdf_up"]

            if pdf_file.filename == "": #no file name
                msg = "Must select a file"
                print(msg)
                flash(msg, 'warning')
                return redirect('/', code=302)

            if allowed_file(pdf_file.filename): #file type
                filename = secure_filename(pdf_file.filename)
                filepath = os.path.join(app.config['PDF_UPLOADS'], filename)
                pdf_file.save(filepath)
                msg = f"pdf file saved ... {pdf_file}"
                print(msg)
                sci_output, en_output = tokenize_render(filepath, \
                                'Long-version keyword extraction', \
                                'Short-version keyword extraction', \
                                'ENTITY')
                return render_template("upload_pdf.html", \
                        sci_output=sci_output, \
                        en_output=en_output, \
                        the_title='NLP PDF journal article keyword extraction')
            else:
                msg = 'That file is not acceptable, should be .txt or .pdf'
                flash(msg, 'warning')
                print(msg)
                return redirect('/', code=302)
        return render_template('index.html',the_title=title)

if __name__ == '__main__':
    app.run()
