FROM python:3.12-slim-bookworm

WORKDIR /consumer-app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY consumer_app.py consumer_app.py
COPY searchclients.py searchclients.py
COPY common.py common.py
COPY client.properties client.properties

CMD [ "python", "consumer_app.py" ]