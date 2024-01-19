from django.core.management.base import BaseCommand
from Credit.tasks import ingest_customer_data, ingest_loan_data

class Command(BaseCommand):
    help = 'Ingest data into the system using background workers'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Ingesting customer data...'))
        ingest_customer_data.delay()
        self.stdout.write(self.style.SUCCESS('Customer data ingestion task enqueued.'))

        self.stdout.write(self.style.SUCCESS('Ingesting loan data...'))
        ingest_loan_data.delay()
        self.stdout.write(self.style.SUCCESS('Loan data ingestion task enqueued.'))
