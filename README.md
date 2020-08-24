# NLP web-app to parse PDF journal articles

This small flask application demonstrates use of NLTK to extract keywords (such as unique NSC identifiers and taxonomy related words) from PDF journal articles and render on the web-page for easy interpretation.

#### Installation
There are two version of the `Dockerfile`; one for testing locally and a second for deploying on the server. Choose the local version for a local install. Simply enter in the terminal: `docker build -t app-name 'path/to/app'`.

After installing all dependencies and building from `Dockerfile`, run the app by entering its folder and typing:

`docker run -d app-name`

The file could be a `.txt` or `.pdf` file. There will be two outputs, each in their own small `HTML` table:
1. Possible NSC numbers that relate to the natural product extract (compound)
2. Possible taxonomy names that were found in the corpus

Screenshot of the web-app:
![Screenshot](static/screenshot.png)
