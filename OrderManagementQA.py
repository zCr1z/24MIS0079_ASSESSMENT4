import unittest
from OrderManagement import OrderManagement


class OrderManagementQA(unittest.TestCase):

    def order(self, products, coupon=None):
        return OrderManagement(products, coupon)

    def test_single_product(self):
        result = self.order([
            {"product_id": "P101", "quantity": 1}
        ]).calculate()
        self.assertGreater(result["final_amount"], 0)

    def test_multiple_products(self):
        result = self.order([
            {"product_id": "P101", "quantity": 1},
            {"product_id": "P102", "quantity": 2}
        ]).calculate()
        self.assertGreater(result["subtotal"], 20000)

    def test_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.order([{"product_id": "P101", "quantity": 0}]).calculate()

    def test_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.order([{"product_id": "P101", "quantity": -1}]).calculate()

    def test_invalid_product(self):
        with self.assertRaises(ValueError):
            self.order([{"product_id": "P999", "quantity": 1}]).calculate()

    def test_invalid_coupon(self):
        with self.assertRaises(ValueError):
            self.order([{"product_id": "P101", "quantity": 1}],
                       "BADCODE").calculate()

    def test_maximum_discount_limit(self):
        result = self.order([
            {"product_id": "P101", "quantity": 10}
        ], "SAVE20").calculate()
        self.assertLessEqual(result["discount"], result["subtotal"] * 0.30)

    def test_tax_calculation(self):
        result = self.order([
            {"product_id": "P104", "quantity": 1}
        ]).calculate()
        taxable = result["subtotal"] - result["discount"]
        self.assertAlmostEqual(result["gst"], taxable * 0.18, places=2)

    def test_free_shipping(self):
        result = self.order([
            {"product_id": "P101", "quantity": 1}
        ]).calculate()
        self.assertEqual(result["shipping"], 0)

    def test_paid_shipping(self):
        result = self.order([
            {"product_id": "P104", "quantity": 1}
        ]).calculate()
        self.assertEqual(result["shipping"], 100)

    def test_bulk_order(self):
        result = self.order([
            {"product_id": "P102", "quantity": 10}
        ]).calculate()
        self.assertGreater(result["discount"], 0)

    def test_out_of_stock(self):
        with self.assertRaises(ValueError):
            self.order([{"product_id": "P101", "quantity": 11}]).calculate()

    def test_coupon_save10(self):
        result = self.order([
            {"product_id": "P104", "quantity": 2}
        ], "SAVE10").calculate()
        self.assertGreater(result["discount"], 0)

    def test_electronics_discount(self):
        result = self.order([
            {"product_id": "P101", "quantity": 1}
        ]).calculate()
        self.assertGreater(result["discount"], 0)

    def test_clothing_discount(self):
        result = self.order([
            {"product_id": "P102", "quantity": 1}
        ]).calculate()
        self.assertGreater(result["discount"], 0)

    def test_grocery_discount(self):
        result = self.order([
            {"product_id": "P103", "quantity": 1}
        ]).calculate()
        self.assertGreater(result["discount"], 0)

    def test_books_no_category_discount(self):
        result = self.order([
            {"product_id": "P104", "quantity": 1}
        ]).calculate()
        self.assertEqual(result["discount"], 0)

    def test_final_amount(self):
        result = self.order([
            {"product_id": "P103", "quantity": 2}
        ]).calculate()
        self.assertGreater(result["final_amount"], result["subtotal"])

    def test_coupon_and_bulk_combination(self):
        result = self.order([
            {"product_id": "P102", "quantity": 10}
        ], "SAVE10").calculate()
        self.assertLessEqual(result["discount"], result["subtotal"] * 0.30)

    def test_quantity_boundary(self):
        result = self.order([
            {"product_id": "P101", "quantity": 10}
        ]).calculate()
        self.assertGreater(result["subtotal"], 0)

    def test_invalid_product_type(self):
        with self.assertRaises(ValueError):
            self.order([{"product_id": "P999", "quantity": 2}]).calculate()


if __name__ == "__main__":
    unittest.main(verbosity=2)
