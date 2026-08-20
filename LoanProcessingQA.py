import unittest
from LoanProcessingSystem import LoanProcessingSystem


class LoanProcessingQA(unittest.TestCase):

    def valid_loan(self, **changes):
        data = {
            "customer_id": "C101",
            "age": 30,
            "salary": 60000,
            "existing_loan": 50000,
            "credit_score": 780,
            "employment_type": "salaried",
            "requested_loan": 500000,
            "tenure": 5
        }
        data.update(changes)
        return LoanProcessingSystem(**data)

    def test_minimum_age(self):
        self.assertEqual(self.valid_loan(age=18).approval_status(), "APPROVED")

    def test_maximum_age(self):
        self.assertEqual(self.valid_loan(age=70).approval_status(), "REJECTED")

    def test_invalid_salary(self):
        with self.assertRaises(ValueError):
            self.valid_loan(salary=0).process()

    def test_poor_credit_score(self):
        self.assertEqual(
            self.valid_loan(credit_score=500).approval_status(),
            "REJECTED"
        )

    def test_existing_loan_threshold(self):
        self.assertEqual(
            self.valid_loan(existing_loan=400000).approval_status(),
            "REJECTED"
        )

    def test_high_dti(self):
        self.assertEqual(
            self.valid_loan(existing_loan=30000, salary=60000,
                            requested_loan=1000000).approval_status(),
            "REJECTED"
        )

    def test_employment_categories(self):
        for category in ["salaried", "self-employed", "business"]:
            result = self.valid_loan(employment_type=category).process()
            self.assertIn("eligible_loan", result)

    def test_boundary_loan_amount(self):
        loan = self.valid_loan()
        eligible = loan.eligible_loan_amount()
        self.assertEqual(
            self.valid_loan(requested_loan=eligible).approval_status(),
            "APPROVED"
        )

    def test_emi_calculation(self):
        loan = self.valid_loan()
        expected = loan.emi(500000)
        self.assertEqual(loan.emi(500000), expected)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            self.valid_loan(age=17).process()

    def test_invalid_employment(self):
        with self.assertRaises(ValueError):
            self.valid_loan(employment_type="student").process()


if __name__ == "__main__":
    unittest.main(verbosity=2)
