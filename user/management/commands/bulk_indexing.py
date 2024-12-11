from django.core.management.base import BaseCommand
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
from questions.models import Question
from user.documents import QuestionDocument
import os

HOST =  os.getenv('HOST')

class Command(BaseCommand):
    help = "Indexes questions into OpenSearch"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting bulk indexing...")
        bulk_indexing()
        self.stdout.write(self.style.SUCCESS('Bulk indexing completed successfully!'))

def bulk_indexing():
    client = OpenSearch(
        HOST,
        verify_certs=True,
        timeout=30
    )

    QuestionDocument.init()

    actions = []
    for question in Question.objects.prefetch_related('tags'):
        actions.append(
            {
                "_op_type": "index",
                "_index": "questions_index",
                "_id": question.id,
                "_source": {
                    "title": question.title,
                    "body": question.body,
                    "tags": [tag.tag.name for tag in question.tags.all()]
                }
            }
        )

    try:
        success, failed = bulk(client, actions)
        print(f"Successfully indexed {success} documents, failed to index {failed} documents.")
    except Exception as e:
        print(f"An error occurred during bulk indexing: {e}")
