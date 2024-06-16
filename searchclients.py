# setting up consumer app as stand alone
from elasticsearch import Elasticsearch
from opensearchpy import OpenSearch

import logging
import os


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Search:

    def __init__(self, index=None):
        pass
    
    def create_index(self):
        raise NotImplementedError()

    def insert_document(self, id, document):
        raise NotImplementedError()
    
    def insert_documents(self, documents):
        raise NotImplementedError()
    
    def search(self, query_args):
        raise NotImplementedError()


class ESClient(Search):
    def __init__(self, index, debug=False):

        config = {
            'hosts': os.getenv('ELASTIC_HOSTS') and os.getenv('ELASTIC_HOSTS').split(',') or 'https://localhost:9200',
            'basic_auth': (os.getenv('ELASTIC_USER_NAME') or 'elastic', os.getenv('ELASTIC_USER_PASS') or 'StrongPass'),
            'ssl_assert_fingerprint': os.getenv('ELASTIC_SSL_ASSERT') and 'ssl_fingerprint_local'
        }
        logger.info(config)
        self.es = Elasticsearch(**config)
        if debug: logger.info(self.es.info())
        self.index = index

    def create_index(self):
        self.es.indices.delete(index=self.index, ignore_unavailable=True)
        self.es.indices.create(index=self.index)

    def insert_document(self, id, document):
        return self.es.index(index=self.index, id=id,body=document)
    
    def insert_documents(self, documents):
        operations = []
        for document in documents:
            operations.append({'index': {'_index': self.index}})
            operations.append(document)
        return self.es.bulk(operations=operations)
    
    def search(self, query_args):
        return self.es.search(index=self.index, **query_args)


class OpenSearchClient(Search):
    def __init__(self, index, debug=False):
        config = {
            'hosts': os.getenv('OPENSEARCH_HOSTS') and os.getenv('OPENSEARCH_HOSTS').split(',') or 'http://localhost:9201',
        }
        if debug: logger.info(config)
        self.es = OpenSearch(**config)
        if debug: logger.info(self.es.info())
        self.index = index

    def create_index(self):
        self.es.indices.delete(index=self.index, ignore_unavailable=True)
        self.es.indices.create(index=self.index)

    def insert_document(self, id, document):
        return self.es.index(index=self.index, id=id, body=document)
    
    def insert_documents(self, documents):
        operations = []
        for document in documents:
            operations.append({'index': {'_index': self.index}})
            operations.append(document)
        return self.es.bulk(operations=operations)
    
    def search(self, query_args):
        print(query_args)
        return self.es.search(index=self.index, **query_args)


providers = {
    'elastic': ESClient,
    'opensearch': OpenSearchClient
}


if __name__ == '__main__':
    client = ESClient(index='clients', debug=True)
