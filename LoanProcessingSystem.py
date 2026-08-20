class LoanProcessingSystem:
    def __init__(self, customer_id, age, salary, existing_loan, credit_score,
                 employment_type, requested_loan, tenure):
        self.customer_id = customer_id
        self.age = age
        self.salary = salary
        self.existing_loan = existing_loan
        self.credit_score = credit_score
        self.employment_type = employment_type.lower()
        self.requested_loan = requested_loan
        self.tenure = tenure

    def validate(self):
        if self.age < 18 or self.age > 70:
            raise ValueError("Age must be between 18 and 70")
        if self.salary <= 0:
            raise ValueError("Salary must be positive")
        if self.existing_loan < 0 or self.requested_loan <= 0:
            raise ValueError("Loan amounts are invalid")
        if not 300 <= self.credit_score <= 900:
            raise ValueError("Credit score must be between 300 and 900")
        if self.tenure <= 0:
            raise ValueError("Loan tenure must be positive")
        if self.employment_type not in {"salaried", "self-employed", "business"}:
            raise ValueError("Invalid employment type")

    def debt_to_income_ratio(self):
        return self.existing_loan / self.salary

    def eligible_loan_amount(self):
        multiplier = {
            "salaried": 24,
            "self-employed": 20,
            "business": 18
        }[self.employment_type]

        credit_factor = 1.0
        if self.credit_score >= 750:
            credit_factor = 1.25
        elif self.credit_score >= 650:
            credit_factor = 1.0
        else:
            credit_factor = 0.60

        eligible = self.salary * multiplier * credit_factor
        return round(max(0, eligible - self.existing_loan), 2)

    def interest_rate(self):
        if self.credit_score >= 800:
            return 7.5
        if self.credit_score >= 750:
            return 8.0
        if self.credit_score >= 650:
            return 9.5
        return 12.0

    def emi(self, principal=None):
        if principal is None:
            principal = self.requested_loan

        rate = self.interest_rate() / 12 / 100
        months = self.tenure * 12

        if rate == 0:
            return round(principal / months, 2)

        value = principal * rate * (1 + rate) ** months
        return round(value / ((1 + rate) ** months - 1), 2)

    def approval_status(self):
        self.validate()

        dti = self.debt_to_income_ratio()
        eligible = self.eligible_loan_amount()

        approved = (
            21 <= self.age <= 60
            and self.credit_score >= 650
            and dti <= 0.40
            and self.existing_loan <= self.salary * 5
            and self.requested_loan <= eligible
        )

        return "APPROVED" if approved else "REJECTED"

    def process(self):
        self.validate()
        return {
            "customer_id": self.customer_id,
            "dti": round(self.debt_to_income_ratio(), 4),
            "eligible_loan": self.eligible_loan_amount(),
            "interest_rate": self.interest_rate(),
            "emi": self.emi(),
            "status": self.approval_status()
        }


if __name__ == "__main__":
    loan = LoanProcessingSystem(
        "C101", 30, 60000, 50000, 780,
        "salaried", 500000, 5
    )
    print(loan.process())
