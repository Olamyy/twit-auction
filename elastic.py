from elasticsearch import Elasticsearch
from config import CONFIG


class Elastic:
    def __init__(self):
        config = CONFIG.get('elasticsearch')
        self._elastic = Elasticsearch([{"host": config.get('host'), "port": config.get('port')}])

    def mapping(self):

        mapping = {
            "mappings": {
                "user": {
                    "properties": {
                        "user": {"type": "string"},
                        "created_at": {"type": "string"}
                    }
                },

            }
        }

        if self._elastic.indices.exists("auction-index"):
            self._elastic.indices.delete(index="auction-index")

        self._elastic.indices.create(index="auction-index", ignore=400, body=mapping)

    def insert(self, index, doc_type, body):
        result = self._elastic.index(index=index, doc_type=doc_type, body=body)
        return result

    def query(self, index, doc_type, doc_id):
        data = self._elastic.get(index=index, doc_type=doc_type, id=doc_id)
        return data

    def search(self, index, body):
        result = self._elastic.search(index=index, body=body)
        return result

    def update(self, index, doc_type, doc_id, body):
        data = self._elastic.update(index=index, doc_type=doc_type,
                                    id=doc_id, body=body)
        return data
