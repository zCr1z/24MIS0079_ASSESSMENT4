"""
Banking Loan Approval System - QA Program
LoanProcessingQA.py

Run standalone:      python3 LoanProcessingQA.py
Run with unittest:   python3 -m unittest LoanProcessingQA -v
Run with pytest:     pytest LoanProcessingQA.py -v
"""
import unittest
from LoanProcessingSystem import LoanProcessingSystem, LoanValidationError


def make_loan(**overrides):
    defaults = dict(
        customer_id="CUST001",
        age=30,
        monthly_salary=60000,
        existing_loan_amount=100000,
        credit_score=780,
        employment_type="SALARIED",
        requested_loan_amount=500000,
        loan_tenure_months=60,
    )
    defaults.update(overrides)
    return LoanProcessingSystem(**defaults)


class TestLoanProcessingSystem(unittest.TestCase):

    # ---- age boundaries ----
    def test_minimum_age_boundary_approved(self):
        loan = make_loan(age=21)
        result = loan.process_application()
        self.assertNotIn("Age must be between 21 and 60", result["reasons"])

    def test_maximum_age_boundary_approved(self):
        loan = make_loan(age=60)
        result = loan.process_application()
        self.assertNotIn("Age must be between 21 and 60", result["reasons"])

    def test_below_minimum_age_rejected(self):
        loan = make_loan(age=20)
        result = loan.process_application()
        self.assertEqual(result["status"], "REJECTED")

    def test_above_maximum_age_rejected(self):
        loan = make_loan(age=61)
        result = loan.process_application()
        self.assertEqual(result["status"], "REJECTED")

    # ---- invalid salary ----
    def test_zero_salary_raises(self):
        with self.assertRaises(LoanValidationError):
            make_loan(monthly_salary=0)

    def test_negative_salary_raises(self):
        with self.assertRaises(LoanValidationError):
            make_loan(monthly_salary=-5000)

    def test_below_minimum_salary_raises(self):
        with self.assertRaises(LoanValidationError):
            make_loan(monthly_salary=5000)

    # ---- credit score ----
    def test_poor_credit_score_rejected(self):
        loan = make_loan(credit_score=500)
        result = loan.process_application()
        self.assertEqual(result["status"], "REJECTED")
        self.assertTrue(any("Credit score" in r for r in result["reasons"]))

    def test_high_credit_score_gets_rate_discount(self):
        loan = make_loan(credit_score=800)
        rate = loan.calculate_interest_rate()
        self.assertEqual(rate, 7.5)  # 8.5 base - 1.0 for excellent score

    # ---- existing loan threshold ----
    def test_existing_loan_exceeding_threshold_rejected(self):
        loan = make_loan(existing_loan_amount=3000000)
        result = loan.process_application()
        self.assertEqual(result["status"], "REJECTED")
        self.assertTrue(any("threshold" in r for r in result["reasons"]))

    # ---- debt to income ratio ----
    def test_high_dti_ratio_rejected(self):
        loan = make_loan(monthly_salary=15000, existing_loan_amount=1900000)
        result = loan.process_application()
        self.assertGreater(result["dti_ratio"], 50.0)
        self.assertEqual(result["status"], "REJECTED")

    # ---- employment categories ----
    def test_salaried_employment_rate(self):
        loan = make_loan(employment_type="SALARIED", credit_score=700)
        self.assertEqual(loan.calculate_interest_rate(), 8.5)

    def test_self_employed_employment_rate(self):
        loan = make_loan(employment_type="SELF_EMPLOYED", credit_score=700)
        self.assertEqual(loan.calculate_interest_rate(), 10.5)

    def test_business_employment_rate(self):
        loan = make_loan(employment_type="BUSINESS", credit_score=700)
        self.assertEqual(loan.calculate_interest_rate(), 11.0)

    def test_invalid_employment_type_raises(self):
        with self.assertRaises(LoanValidationError):
            make_loan(employment_type="FREELANCER")

    # ---- boundary loan amounts ----
    def test_requested_amount_equal_to_eligible_approved(self):
        loan = make_loan(monthly_salary=60000, existing_loan_amount=0, requested_loan_amount=3600000)
        result = loan.process_application()
        self.assertEqual(result["eligible_amount"], 3600000)
        self.assertNotIn("Requested amount exceeds eligible loan amount", result["reasons"])

    def test_requested_amount_over_eligible_rejected(self):
        loan = make_loan(monthly_salary=60000, existing_loan_amount=0, requested_loan_amount=3600001)
        result = loan.process_application()
        self.assertEqual(result["status"], "REJECTED")

    # ---- EMI calculation accuracy ----
    def test_emi_calculation_known_value(self):
        loan = make_loan()
        emi = loan.calculate_emi(principal=500000, annual_rate=8.5, tenure_months=60)
        self.assertAlmostEqual(emi, 10258.28, delta=0.5)

    def test_emi_zero_interest(self):
        loan = make_loan()
        emi = loan.calculate_emi(principal=120000, annual_rate=0, tenure_months=12)
        self.assertEqual(emi, 10000.0)

    # ---- invalid input handling ----
    def test_non_numeric_age_raises(self):
        with self.assertRaises(LoanValidationError):
            make_loan(age="thirty")

    def test_non_integer_tenure_raises(self):
        with self.assertRaises(LoanValidationError):
            make_loan(loan_tenure_months=60.5)

    def test_negative_existing_loan_raises(self):
        with self.assertRaises(LoanValidationError):
            make_loan(existing_loan_amount=-1)

    # ---- exception handling ----
    def test_zero_tenure_raises(self):
        with self.assertRaises(LoanValidationError):
            make_loan(loan_tenure_months=0)

    def test_credit_score_out_of_range_raises(self):
        with self.assertRaises(LoanValidationError):
            make_loan(credit_score=1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
