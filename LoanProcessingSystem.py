"""
Banking Loan Approval System
Development Program: LoanProcessingSystem.java equivalent in Python
"""


class LoanValidationError(Exception):
    """Raised when input data fails validation rules."""
    pass


class LoanProcessingSystem:
    MIN_AGE = 21
    MAX_AGE = 60
    MIN_CREDIT_SCORE = 650
    MAX_DTI_RATIO = 50.0          # percent
    EXISTING_LOAN_THRESHOLD = 2000000   # 20 lakh
    MIN_SALARY = 10000

    INTEREST_RATES = {
        "SALARIED": 8.5,
        "SELF_EMPLOYED": 10.5,
        "BUSINESS": 11.0,
    }

    VALID_EMPLOYMENT_TYPES = set(INTEREST_RATES.keys())

    def __init__(self, customer_id, age, monthly_salary, existing_loan_amount,
                 credit_score, employment_type, requested_loan_amount, loan_tenure_months):
        self.customer_id = customer_id
        self.age = age
        self.monthly_salary = monthly_salary
        self.existing_loan_amount = existing_loan_amount
        self.credit_score = credit_score
        self.employment_type = employment_type
        self.requested_loan_amount = requested_loan_amount
        self.loan_tenure_months = loan_tenure_months
        self._validate_inputs()

    # ---------------------- validation ----------------------
    def _validate_inputs(self):
        if not isinstance(self.age, (int, float)) or isinstance(self.age, bool):
            raise LoanValidationError("Age must be numeric")
        if not isinstance(self.monthly_salary, (int, float)) or isinstance(self.monthly_salary, bool):
            raise LoanValidationError("Monthly salary must be numeric")
        if not isinstance(self.existing_loan_amount, (int, float)) or isinstance(self.existing_loan_amount, bool):
            raise LoanValidationError("Existing loan amount must be numeric")
        if not isinstance(self.credit_score, (int, float)) or isinstance(self.credit_score, bool):
            raise LoanValidationError("Credit score must be numeric")
        if not isinstance(self.requested_loan_amount, (int, float)) or isinstance(self.requested_loan_amount, bool):
            raise LoanValidationError("Requested loan amount must be numeric")
        if not isinstance(self.loan_tenure_months, int) or isinstance(self.loan_tenure_months, bool):
            raise LoanValidationError("Loan tenure must be an integer number of months")

        if self.monthly_salary <= 0:
            raise LoanValidationError("Monthly salary must be greater than zero")
        if self.monthly_salary < self.MIN_SALARY:
            raise LoanValidationError(f"Monthly salary below minimum threshold of {self.MIN_SALARY}")
        if self.existing_loan_amount < 0:
            raise LoanValidationError("Existing loan amount cannot be negative")
        if self.requested_loan_amount <= 0:
            raise LoanValidationError("Requested loan amount must be greater than zero")
        if self.loan_tenure_months <= 0 or self.loan_tenure_months > 360:
            raise LoanValidationError("Loan tenure must be between 1 and 360 months")
        if not (0 <= self.credit_score <= 900):
            raise LoanValidationError("Credit score must be between 0 and 900")
        if self.employment_type not in self.VALID_EMPLOYMENT_TYPES:
            raise LoanValidationError(f"Invalid employment type: {self.employment_type}")

    # ---------------------- calculations ----------------------
    def calculate_dti_ratio(self):
        """Debt-to-income ratio (%) using an assumed 3% monthly obligation on existing loan."""
        existing_emi_estimate = self.existing_loan_amount * 0.03
        ratio = (existing_emi_estimate / self.monthly_salary) * 100
        return round(ratio, 2)

    def calculate_interest_rate(self):
        rate = self.INTEREST_RATES[self.employment_type]
        if self.credit_score >= 750:
            rate -= 1.0
        elif self.credit_score < self.MIN_CREDIT_SCORE:
            rate += 2.0
        return round(rate, 2)

    def calculate_eligible_amount(self):
        """Eligible amount = 60x monthly salary minus existing loan exposure, never negative."""
        eligible = (self.monthly_salary * 60) - self.existing_loan_amount
        return max(0, round(eligible, 2))

    def calculate_emi(self, principal, annual_rate, tenure_months):
        if principal <= 0 or tenure_months <= 0:
            return 0.0
        monthly_rate = annual_rate / (12 * 100)
        if monthly_rate == 0:
            return round(principal / tenure_months, 2)
        factor = (1 + monthly_rate) ** tenure_months
        emi = principal * monthly_rate * factor / (factor - 1)
        return round(emi, 2)

    # ---------------------- decision engine ----------------------
    def process_application(self):
        reasons = []

        if not (self.MIN_AGE <= self.age <= self.MAX_AGE):
            reasons.append(f"Age must be between {self.MIN_AGE} and {self.MAX_AGE}")

        if self.credit_score < self.MIN_CREDIT_SCORE:
            reasons.append(f"Credit score below minimum required {self.MIN_CREDIT_SCORE}")

        if self.existing_loan_amount > self.EXISTING_LOAN_THRESHOLD:
            reasons.append("Existing loan amount exceeds allowed threshold")

        dti_ratio = self.calculate_dti_ratio()
        if dti_ratio > self.MAX_DTI_RATIO:
            reasons.append(f"Debt-to-income ratio {dti_ratio}% exceeds max {self.MAX_DTI_RATIO}%")

        eligible_amount = self.calculate_eligible_amount()
        if self.requested_loan_amount > eligible_amount:
            reasons.append("Requested amount exceeds eligible loan amount")

        interest_rate = self.calculate_interest_rate()
        emi = self.calculate_emi(self.requested_loan_amount, interest_rate, self.loan_tenure_months)

        status = "APPROVED" if not reasons else "REJECTED"

        return {
            "customer_id": self.customer_id,
            "status": status,
            "reasons": reasons,
            "dti_ratio": dti_ratio,
            "eligible_amount": eligible_amount,
            "interest_rate": interest_rate,
            "emi": emi,
        }


if __name__ == "__main__":
    loan = LoanProcessingSystem(
        customer_id="CUST001",
        age=30,
        monthly_salary=60000,
        existing_loan_amount=100000,
        credit_score=780,
        employment_type="SALARIED",
        requested_loan_amount=500000,
        loan_tenure_months=60,
    )
    result = loan.process_application()
    print(result)
