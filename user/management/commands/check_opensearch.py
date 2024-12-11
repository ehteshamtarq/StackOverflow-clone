from django.core.management.base import BaseCommand
from opensearch_dsl.connections import connections
from opensearch_dsl import exceptions


class Command(BaseCommand):
    help = "Check if OpenSearch DSL is working"

    def handle(self, *args, **options):
        try:
            connection = connections.get_connection('default')

            if connection.ping():
                self.stdout.write(self.style.SUCCESS("Successfully connected to OpenSearch!"))

                if hasattr(connection, 'cluster'):
                    health = connection.cluster.health()
                    self.stdout.write(self.style.SUCCESS(f"Cluster health: {health['status']}"))
                else:
                    self.stderr.write(self.style.ERROR("Cluster health is not accessible."))

        except exceptions.ConnectionError as e:
            self.stderr.write(self.style.ERROR(f"ConnectionError: {e}"))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Connection alias not found: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected error: {e}"))
