from django.urls import path
from .views import (
    RegisterCustomerView,
    CheckEligibilityView,
    CreateLoanView,
    LoanDetailView,
    LoanListView
)

urlpatterns = [
    path('register/', RegisterCustomerView.as_view(), name='register-customer'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check_eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create_loan'),
    path('view-loan/<int:id>/', LoanDetailView.as_view(), name='view_loan'),
    path('view-loans/<int:customer_id>/', LoanListView.as_view(), name='view_loans'),
]
