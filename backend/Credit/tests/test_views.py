from datetime import date
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from ..models import Customer, Loan
from ..serializers import LoanDetailSerializer


class RegisterCustomerViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('register-customer')
        self.customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'monthly_income': 5000,
            'phone_number': '1234567890',
        }

    def test_register_customer_view(self):
        response = self.client.post(self.url, data=self.customer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)


class CheckEligibilityViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('check_eligibility')
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            monthly_income=5000,
            phone_number='1234567890'
        )
        self.serializer_data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 10000,
            'interest_rate': 10.0,
            'tenure': 12,
        }

    def test_check_eligibility_view(self):
        response = self.client.post(self.url, data=self.serializer_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_eligible', response.data)
        self.assertTrue(response.data['is_eligible'])


class CreateLoanViewTest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            monthly_income=5000,
            phone_number='1234567890'
        )
        self.url = reverse('create_loan')
        self.loan_data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 10000,
            'interest_rate': 10.0,
            'tenure': 12,
        }

    def test_create_loan_view_approved(self):
        response = self.client.post(self.url, data=self.loan_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['loan_approved'])
        self.assertIsNone(response.data['loan_id'])
        self.assertEqual(str(response.data['customer_id']), str(self.customer.customer_id))
        self.assertEqual(response.data['message'], 'Loan not approved')
        self.assertEqual(response.data['monthly_installment'], 0.0)
        self.assertEqual(Loan.objects.count(), 0)


class LoanViewTests(TestCase):
    def setUp(self):
        # Create a test customer
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            monthly_income=5000.0,
            approved_limit=20000.0,
            phone_number="1234567890"
        )

        # Create a test loan
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_id=1,
            loan_amount=10000.0,
            interest_rate=5.0,
            tenure=12,
            monthly_installment=900.0,
            emis_paid_on_time=6,
            end_date=date.today(),
            date_of_approval=date.today(),
            loan_approved=True
        )

        # Set up the API client
        self.client = APIClient()

    def test_loan_detail_view(self):
        url = reverse('view_loan', kwargs={'loan_id': self.loan.loan_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serialized_data = LoanDetailSerializer(self.loan).data
        self.assertEqual(response.data, serialized_data)

    def test_loan_list_view(self):
        url = reverse('view_loans', kwargs={'customer_id': self.customer.customer_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Check if the added 'repayments_left' field is present in the response
        expected_repayments_left = self.loan.tenure - self.loan.emis_paid_on_time
        self.assertEqual(response.data[0]['repayments_left'], expected_repayments_left)
