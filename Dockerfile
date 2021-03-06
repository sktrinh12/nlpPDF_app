FROM python:3.7-slim-buster
# to install the gcc for regex and other dependencies

ADD . /app
WORKDIR /app
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
EXPOSE 8050
RUN mkdir models && mkdir -p static/uploads
COPY models/*.pkl /app/models
# copy the pkl files since excluding in dockerignore, but makefile will copy it from other directory and then rm at the end

ENV FLASK_APP /app/app.py
RUN python -m nltk.downloader stopwords && \
    python -m nltk.downloader punkt && \
    python -m nltk.downloader averaged_perceptron_tagger

ENV FLASK_ENV=production
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
