from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    monthly_income = models.FloatField()
    approved_limit = models.FloatField(null=True, blank=True)
    phone_number = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            # Set customer_id only if it's not provided
            last_customer = Customer.objects.order_by('-customer_id').first()
            if last_customer:
                self.customer_id = last_customer.customer_id + 1
            else:
                # Handle the case when no records exist yet
                self.customer_id = 1
        super().save(*args, **kwargs)

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_id = models.IntegerField()
    loan_amount = models.FloatField()
    interest_rate = models.FloatField()
    tenure = models.IntegerField()
    monthly_installment = models.FloatField()
    emis_paid_on_time = models.IntegerField()
    end_date = models.DateField()
    date_of_approval = models.DateField()
    loan_approved = models.BooleanField(default=False)
