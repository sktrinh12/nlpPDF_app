from werkzeug.utils import secure_filename
from functions import *

title = 'NLP PDF journal article keyword extraction'

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html', the_title=title)

#@app.route("/upload-pdf2", methods=["GET", "POST"])
#def upload_pdf():
#    if request.method == "POST":
#        if request.files and "filesize" in request.cookies:
#            if not allowed_filesize(request.cookies.get("filesize")):
#                #based on filesize
#                msg = f'File exceeded maximum size {request.cookies.get("filesize")}'
#                print(msg)
#                flash(msg, 'warning')
#                return redirect('/', code=302)

#            pdf_file = request.files["pdf_up"]

#            if pdf_file.filename == "": #no file name
#                msg = "Must select a file"
#                print(msg)
#                flash(msg, 'warning')
#                return redirect('/', code=302)

#            if allowed_file(pdf_file.filename): #file type
#                filename = secure_filename(pdf_file.filename)
#                filepath = os.path.join(app.config['PDF_UPLOADS'], filename)
#                pdf_file.save(filepath)
#                msg = f"pdf file saved ... {pdf_file}"
#                print(msg)

#                dict_output = tokenize_render(filepath, \
#                                'long-version keyword extraction', \
#                                'short-version keyword extraction'
#                                )

#                return render_template("upload_pdf.html", \
#                        sci_output=dict_output['sci_output'], \
#                        en_output=dict_output['en_output'], \
#                        filename=filename, \
#                        nscs=dict_output['nscs'], \
#                        pg_no=dict_output['pg_no'], \
#                        the_title=title)
#            else:
#                msg = 'That file is not acceptable, should be .txt or .pdf'
#                flash(msg, 'warning')
#                print(msg)
#                return redirect('/', code=302)
#        return render_template('index.html',the_title=title)

@app.route("/test", methods=["GET", "POST"])
def test():
    poss_wp, poss_nscs = [
                        "resemble tanke",
                        "labored asfk",
                        "fog pweoiqr",
                        "ride 234jlkcv",
                        "painstaking aspfoiu23",
                        "vegetable aspoij2",
                        "possessive aspoiuj",
                        "wrist 98s0afup",
                        "existence apsofij",
                        "chance japsofiu",
                        "behave p93845ji",
                        "roomy aslifj;",
                        "arrange i2jlksf",
                        "company 2oi3u4hs",
                        "broad 23iu4hjljas",
                        "cars jaklsaf;",
                        "box alksjfa;ks",
                        ], "N1238980"

    return render_template("upload_pdf2.html", \
            filename='test_file.file', \
            poss_wp=poss_wp, \
            nscs=poss_nscs, \
            the_title='title')

@app.route("/upload-pdf", methods=["GET", "POST"])
def upload_pdf():
    if request.method == "POST":
        if request.files and "filesize" in request.cookies:
            if not allowed_filesize(request.cookies.get("filesize")):
                #based on filesize
                msg = f'File exceeded maximum size {request.cookies.get("filesize")}'
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

                poss_wp, poss_nscs = tokenise_render_v2(filepath)

                return render_template("upload_pdf2.html", \
                        filename=filename, \
                        poss_wp=poss_wp, \
                        nscs=poss_nscs, \
                        the_title=title)
            else:
                msg = 'That file is not acceptable, should be .txt or .pdf'
                flash(msg, 'warning')
                print(msg)
                return redirect('/', code=302)
        return render_template('index.html',the_title=title)

if __name__ == '__main__':
    app.run()
