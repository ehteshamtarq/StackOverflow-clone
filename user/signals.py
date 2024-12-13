from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from opensearchpy import OpenSearch
from questions.models import Question
import os

HOST =  os.getenv('HOST')

client = OpenSearch(
    HOST,
    verify_certs=True,
    timeout=30
)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Question)
def index_question(sender, instance, created, **kwargs):

    action = {
        "_op_type": "index" if created else "update",  # Index if created, update if modified
        "_index": "questions_index",  # Specify the index name
        "_id": instance.id,  # The document ID
        "_source": {
            "title": instance.title,
            "body": instance.body,
            "tags": [tag.tag.name for tag in instance.tags.all()]
        }
    }

    try:
        # Perform the indexing or update operation
        client.index(index="questions_index", id=instance.id, body=action["_source"])
        print(f"Successfully indexed/updated question: {instance.title}")
    except Exception as e:
        print(f"Failed to index/update question: {instance.title}. Error: {e}")


@receiver(post_delete, sender=Question)
def delete_question(sender, instance, **kwargs):
    try:
        client.delete(index="questions_index", id=instance.id)
        print(f"Successfully deleted question: {instance.title} from OpenSearch")
    except Exception as e:
        print(f"Failed to delete question: {instance.title}. Error: {e}")
