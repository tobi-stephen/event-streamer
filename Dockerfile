FROM python:3.12-slim-bookworm

WORKDIR /producer-app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "-m", "flask", "run", "--debug", "--host=0.0.0.0" ]