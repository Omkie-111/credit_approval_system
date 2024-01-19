import os
from celery import shared_task
import pandas as pd
from django.conf import settings
from Credit.models import Customer, Loan

@shared_task(bind=True)
def ingest_customer_data(self):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'Alemeno', 'customer_data.xlsx')
        df = pd.read_excel(file_path)

        # Create Customer objects and save them
        for _, row in df.iterrows():
            Customer.objects.create(
                customer_id=row['Customer ID'],
                first_name=row['First Name'],
                last_name=row['Last Name'],
                age=row['Age'],
                monthly_income=row['Monthly Salary'],
                approved_limit=row['Approved Limit'],
                phone_number=row['Phone Number']
            )
    except Exception as e:
        # Log or report the error
        print(f"Error during customer data ingestion: {e}")


@shared_task(bind=True)
def ingest_loan_data(self):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'Alemeno', 'loan_data.xlsx')
        df = pd.read_excel(file_path)
        df['Loan Approved'] = True

        # Create Loan objects and save them
        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['Customer ID'])
            except Customer.DoesNotExist:
                continue

            Loan.objects.create(
                customer=customer,
                loan_id=row['Loan ID'],
                loan_amount=row['Loan Amount'],
                interest_rate=row['Interest Rate'],
                tenure=row['Tenure'],
                monthly_installment=row['Monthly payment'],
                emis_paid_on_time=row['EMIs paid on Time'],
                end_date=row['End Date'],
                date_of_approval=row['Date of Approval'],
                loan_approved=row['Loan Approved']
            )
    except Exception as e:
        # Log or report the error
        print(f"Error during loan data ingestion: {e}")
