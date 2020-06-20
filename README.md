# NLP web-app to parse PDF journal articles 

This small flask application demonstrates use of NLTK and spaCy to extract keywords from PDF journal articles and render on the web-page for easy interpretation.

#### Installation
After installing all dependencies, run the app by entering its folder and typing:

`$ python app.py`

At the moment the file must be a `.txt` file however, in the future will implement `pdfminer` to convert to `.txt` file. The output will be a short condensed version of the keyword extraction (more strict rules to filter stop words) and a long version which uses a more generous stop-word exclusion rule.
