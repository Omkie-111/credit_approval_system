from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerSerializer, CheckEligibilitySerializer, LoanSerializer, LoanDetailSerializer
from django.db.models import Sum, Max
from .models import Customer, Loan
from datetime import date

class RegisterCustomerView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'customer_id'
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        monthly_salary = serializer.validated_data['monthly_income']
        approved_limit = round(36 * monthly_salary, -5)

        customer = serializer.save(approved_limit=approved_limit)

        response_data = {
            'customer_id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': customer.age,
            'monthly_income': customer.monthly_income,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class CheckEligibilityView(generics.CreateAPIView):
    serializer_class = CheckEligibilitySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']

        # Perform eligibility checks here, accessing Customer data if needed
        data = {
            "customer_id" : customer_id,
            "loan_amount" :loan_amount,
            "interest_rate" : interest_rate,
            "tenure" : tenure,
        }
        is_eligible = check_eligibility_helper(data)

        response_data = {'Eligibility': is_eligible}
        return Response(response_data, status=status.HTTP_200_OK)


def calculate_credit_score(customer, loan_amount):
    # Initialize credit_score
    credit_score = 0

    # i. Past Loans paid on time
    past_loans = Loan.objects.filter(customer=customer, emis_paid_on_time=True).count()
    credit_score += past_loans * 5  # Assume each past loan paid on time contributes 5 points

    # ii. No of loans taken in past
    total_loans_taken = Loan.objects.filter(customer=customer).count()
    credit_score += total_loans_taken * 2  # Assume each past loan contributes 2 points

    # iii. Loan activity in the current year
    current_year = date.today().year
    loans_this_year = Loan.objects.filter(customer=customer, date_of_approval__year=current_year).count()
    credit_score += loans_this_year * 3  # Assume each loan taken in the current year contributes 3 points

    # iv. Loan approved volume
    loan_approved_volume = Loan.objects.filter(customer=customer).aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    credit_score += loan_approved_volume * 4  # Assume each approved loan contributes 4 points

    # v. If sum of current loans of customer > approved limit of customer, credit score = 0
    highest_loan_amount = Loan.objects.filter(customer=customer).aggregate(Max('loan_amount'))
    approved_limit = highest_loan_amount['loan_amount__max'] or 0
    if float(loan_amount) > approved_limit:
        credit_score = 0
        
    return credit_score

def check_eligibility_helper(data):
    customer_id = data['customer_id']
    loan_amount = data['loan_amount']
    interest_rate = data['interest_rate']
    tenure = data['tenure']

    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return {
            'approval': False,
            'interest_rate': 0.0,
            'corrected_interest_rate': 0.0,
            'monthly_installment': 0.0,
            'message': 'Customer not found'
        }

    # Calculate credit score
    credit_score = calculate_credit_score(customer, loan_amount)

    # Check loan eligibility based on credit score
    if credit_score > 50:
        approval = True
        corrected_interest_rate = min(interest_rate, 12.0)
    elif 30 < credit_score <= 50:
        approval = True
        corrected_interest_rate = min(interest_rate, 16.0)
    elif 10 < credit_score <= 30:
        approval = True
        corrected_interest_rate = min(interest_rate, 20.0)
    else:
        approval = False
        interest_rate = 0.0
        corrected_interest_rate = 0.0
        tenure = 0
        monthly_installment = 0.0

    # Check if sum of all current EMIs > 50% of monthly salary
    loan_info = Loan.objects.filter(customer=customer, loan_approved=True).aggregate(Sum('monthly_installment'))
    sum_current_emis = loan_info['monthly_installment__sum'] or 0
    emis_ratio = sum_current_emis / (0.5 * customer.monthly_income)

    if emis_ratio > 1:
        approval = False

    if approval:
        # Calculate monthly installment
        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
    else : 
        monthly_installment = 0

    return {
        'approval': approval,
        'interest_rate': interest_rate,
        'corrected_interest_rate': corrected_interest_rate,
        'tenure': tenure,
        'monthly_installment': monthly_installment
    }

    
def calculate_monthly_installment(loan_amount, annual_interest_rate, tenure, compounding_frequency=12):
    # Convert annual interest rate to decimal and calculate monthly interest rate
    print(loan_amount, annual_interest_rate, tenure)
    monthly_interest_rate = annual_interest_rate / (compounding_frequency * 100)

    # Calculate the total number of compounding periods
    total_compounding_periods = compounding_frequency * tenure

    # Calculate the compound factor
    compound_factor = (1 + monthly_interest_rate)**total_compounding_periods

    # Check for division by zero
    if compound_factor == 1:
        raise ValueError("Invalid input: Compound factor is 1, causing division by zero")

    # Calculate monthly installment using compound interest formula
    monthly_installment = (loan_amount * monthly_interest_rate * compound_factor) / (compound_factor - 1)

    return monthly_installment


class CreateLoanView(generics.CreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        # Check eligibility
        eligibility_result = check_eligibility_helper(data)

        if not eligibility_result['approval']:
            return Response({'loan_id': None, 'customer_id': data['customer_id'], 'loan_approved': False, 'message': 'Loan not approved', 'monthly_installment': 0.0}, status=status.HTTP_200_OK)

        # If eligible, create a new Loan instance
        loan_serializer = self.get_serializer(data=data)
        loan_serializer.is_valid(raise_exception=True)
        loan_serializer.save()

        # Get the newly created Loan instance
        loan_instance = Loan.objects.get(id=loan_serializer.data['id'])

        # Prepare the response data
        response_data = {
            'loan_id': loan_instance.id,
            'customer_id': loan_instance.customer.id,
            'loan_approved': True,
            'message': 'Loan approved',
            'monthly_installment': loan_instance.monthly_installment
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class LoanDetailView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanDetailSerializer
    lookup_field = 'id'
    
    
class LoanListView(generics.ListAPIView):
    serializer_class = LoanDetailSerializer
    lookup_field = 'loan_id'

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Loan.objects.none()

        return Loan.objects.filter(customer=customer, loan_approved=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Modify each item in the response to include repayments_left
        response_data = []
        for loan_data in serializer.data:
            repayments_left = loan_data['tenure'] - loan_data['emis_paid_on_time']
            loan_data['repayments_left'] = repayments_left
            response_data.append(loan_data)

        return Response(response_data, status=status.HTTP_200_OK)
