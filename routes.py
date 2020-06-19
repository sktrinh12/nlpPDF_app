from werkzeug.utils import secure_filename
from functions import *

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html', the_title='NLP PDF journal article keyword extraction')

@app.route("/upload-pdf", methods=["GET", "POST"])
def upload_pdf():
    if request.method == "POST":
        if request.files:
            if not allowed_filesize(request.cookies.get("filesize")): #based on filesize
                msg = 'File exceeded maximum size'
                print(msg)
                return redirect(request.url)

            pdf_file = request.files["pdf_up"]

            if pdf_file.filename == "": #no file name
                msg = "File must have a filename"
                print(msg)
                return redirect(request.url)

            if not allowed_file(pdf_file.filename): #file type
                msg = 'That file is not acceptable'
                print(msg)
                return redirect(request.url)
            else:
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


if __name__ == '__main__':
    app.run(debug=True)
