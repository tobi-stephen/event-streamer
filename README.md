## Flask Restful App for Event Driven Development Scenario

### The project is a showcase of skills I recently learned regarding modern development workflows(as at 2024)

For all the components used, I began by setting up each of them locally successfully before trying out the managed cloud solutions
  
The project uses the following primarily
- flask https://flask.palletsprojects.com/en/3.0.x/
- confluent kafka https://developer.confluent.io/get-started/python/#introduction
- elastic search https://www.elastic.co/search-labs
- opensearch https://opensearch.org/
- mongodb https://www.mongodb.com/
- docker https://www.docker.com/
- kubernetes https://kubernetes.io/docs/home/

To run locally, 
- first get api keys from `confluent kafka`, `elastic search`, `mongodb`.
- update the config properties and environment variables, try the below steps and the missing fields might become more obvious
- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `flask run --debug`
- in another terminal, run the consumer app `python consumer_app.py`

The application is separated into 
- producer app: a Rest endpoint saves random idea object into mongodb and produce to a kafka topic
- Consumer app: a standalone python application that subscribes to a kafka topic and saves the idea object into an elastic search index

Created multiple deployment scenarios
- makefile: which can be used to create docker images of the individual apps and run a container
- docker-compose: using docker compose yml config to package all the components nicely
- kubernetes deployment: using the 'deployment' object to deploy with kubectl
