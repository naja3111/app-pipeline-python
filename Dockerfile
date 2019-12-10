FROM ubuntu:xenial

LABEL maintainer="Ubuntu Docker Maintainer - NajaMohamed - naja3111@stthomas.edu"

EXPOSE 8090

RUN apt-get update -y && \
    apt-get install -y python-pip

RUN mkdir app

COPY appserver.py app/appserver.py
COPY requirements.txt app/requirements.txt
COPY Pipfile app/Pipfile
COPY Pipfile.lock app/Pipfile.lock
COPY templates app/templates
COPY static app/static

WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["appserver.py"]