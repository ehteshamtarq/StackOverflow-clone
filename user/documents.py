from opensearch_dsl import Document, Text, Keyword
from opensearch_dsl.connections import connections
import os

HOST =  os.getenv('HOST')

connections.create_connection(hosts=[HOST])

class QuestionDocument(Document):
    title = Text()
    body = Text()
    tags = Keyword()

    class Index:
        name = 'questions_index'

    def save(self, **kwargs):
        return super().save(**kwargs)
