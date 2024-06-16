consumer-app:
	docker build -f consumer_app.Dockerfile -t event_consumer_app . && \
		docker run --rm -it --name consumer_app -e ELASTIC_SSL_ASSERT='' -e ELASTIC_HOSTS=https://localhost:9200 -e ELASTIC_USER_PASS=StrongPass  event_consumer_app


producer-app:
	docker build -f Dockerfile -t event_producer_app . && \
		docker run --rm -it --name producer_app -p 5000:5000 -e ELASTIC_SSL_ASSERT='' -e ELASTIC_HOSTS=https://localhost:9200 -e ELASTIC_USER_PASS=StrongPass event_producer_app


clean-apps:
	docker image rm -f event_consumer_app || true && \
		docker image rm -f event_producer_app || true
