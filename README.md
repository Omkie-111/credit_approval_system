# Credit Approval System

This repository contains the code for a Credit Approval System built with Python/Django stack, utilizing Django Rest Framework. The system includes APIs for customer registration, loan eligibility check, loan creation, and loan details viewing. The application is Dockerized and uses a PostgreSQL database.

## Setup and Initialization

### Setup

- Ensure you have Docker installed on your system.
- Use Django 4+ and Django Rest Framework.
- No frontend is required for this application.
- Dockerize the entire application and its dependencies.
- Use PostgreSQL as the database.

### Initialization

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/credit-approval-system.git
    ```

2. **Move to the project directory:**

    ```bash
    cd backend
    ```

3. **Build and run the Docker containers:**

    ```bash
    docker-compose up --build
    ```

   This command will set up the application, initialize the database with customer and loan data, and start the server.

## API Endpoints

### `/register`

**POST**

- **Request body:**
  - `first_name` (string): First name of the customer.
  - `last_name` (string): Last name of the customer.
  - `age` (int): Age of the customer.
  - `monthly_income` (int): Monthly income of the individual.
  - `phone_number` (int): Phone number of the customer.

- **Response body:**
  - `customer_id` (int): ID of the customer.
  - `name` (string): Name of the customer.
  - `age` (int): Age of the customer.
  - `monthly_income` (int): Monthly income of the individual.
  - `approved_limit` (int): Approved credit limit.
  - `phone_number` (int): Phone number of the customer.

### `/check-eligibility`

**POST**

- **Request body:**
  - `customer_id` (int): ID of the customer.
  - `loan_amount` (float): Requested loan amount.
  - `interest_rate` (float): Interest rate on the loan.
  - `tenure` (int): Tenure of the loan.

- **Response body:**
  - `customer_id` (int): ID of the customer.
  - `approval` (bool): Can the loan be approved.
  - `interest_rate` (float): Interest rate on the loan.
  - `corrected_interest_rate` (float): Corrected interest rate based on credit rating (if applicable).
  - `tenure` (int): Tenure of the loan.
  - `monthly_installment` (float): Monthly installment to be paid as repayment.

### `/create-loan`

**POST**

- **Request body:**
  - `customer_id` (int): ID of the customer.
  - `loan_amount` (float): Requested loan amount.
  - `interest_rate` (float): Interest rate on the loan.
  - `tenure` (int): Tenure of the loan.

- **Response body:**
  - `loan_id` (int): ID of the approved loan (null if not approved).
  - `customer_id` (int): ID of the customer.
  - `loan_approved` (bool): Is the loan approved.
  - `message` (string): Appropriate message if the loan is not approved.
  - `monthly_installment` (float): Monthly installment to be paid as repayment.

### `/view-loan/{loan_id}`

**GET**

- **Response body:**
  - `loan_id` (int): ID of the approved loan.
  - `customer` (JSON): Contains `id`, `first_name`, `last_name`, `phone_number`, `age` of the customer.
  - `loan_amount` (bool): Is the loan approved.
  - `interest_rate` (float): Interest rate of the approved loan.
  - `monthly_installment` (float): Monthly installment to be paid as repayment.
  - `tenure` (int): Tenure of the loan.

### `/view-loans/{customer_id}`

**GET**

- **Response body:**
  - List of loan items, each with:
    - `loan_id` (int): ID of the approved loan.
    - `loan_amount` (bool): Is the loan approved.
    - `interest_rate` (float): Interest rate of the approved loan.
    - `monthly_installment` (float): Monthly installment to be paid as repayment.
    - `repayments_left` (int): Number of EMIs left.

## Additional Information

- The system uses a compound interest scheme for the calculation of monthly interest.
- Error handling is implemented with appropriate status codes for each API endpoint.
- Test Cases are also implemented for APIViews.


