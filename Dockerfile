FROM python:3.7-slim-buster
# to install the gcc for regex and other dependencies

ENV FLASK_ENV="production"

ADD . /app
WORKDIR /app
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt 
EXPOSE 8050
RUN mkdir models && \
    mv *.pkl /app/models

ENV FLASK_APP /app/app.py
RUN python -m nltk.downloader stopwords && \
    python -m nltk.downloader punkt && \ 
    python -m nltk.downloader averaged_perceptron_tagger

CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
