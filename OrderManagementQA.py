"""
E-Commerce Order Processing System - QA Program
OrderManagementQA.py

Run:  python3 -m unittest OrderManagementQA -v
"""
import unittest
from OrderManagement import (
    OrderManagement, Product, OutOfStockError, InvalidCouponError
)


class TestOrderManagement(unittest.TestCase):

    # 1. Single product
    def test_single_product_order(self):
        order = OrderManagement()
        order.add_product(Product("P1", "ELECTRONICS", 1, 1000))
        result = order.calculate_final_amount()
        self.assertEqual(result["subtotal"], 1000)

    # 2. Multiple products
    def test_multiple_products_order(self):
        order = OrderManagement()
        order.add_product(Product("P1", "ELECTRONICS", 1, 500))
        order.add_product(Product("P2", "GROCERY", 3, 100))
        result = order.calculate_final_amount()
        self.assertEqual(result["subtotal"], 800)

    # 3. Zero quantity
    def test_zero_quantity_raises(self):
        order = OrderManagement()
        with self.assertRaises(ValueError):
            order.add_product(Product("P1", "ELECTRONICS", 0, 500))

    # 4. Negative quantity
    def test_negative_quantity_raises(self):
        order = OrderManagement()
        with self.assertRaises(ValueError):
            order.add_product(Product("P1", "ELECTRONICS", -2, 500))

    # 5. Invalid product (no ID)
    def test_invalid_product_no_id_raises(self):
        with self.assertRaises(Exception):
            Product("", "ELECTRONICS", 1, 500)

    # 6. Out of stock product
    def test_out_of_stock_product_raises(self):
        order = OrderManagement()
        with self.assertRaises(OutOfStockError):
            order.add_product(Product("P1", "ELECTRONICS", 1, 500, in_stock=False))

    # 7. Invalid coupon
    def test_invalid_coupon_raises(self):
        order = OrderManagement()
        order.add_product(Product("P1", "ELECTRONICS", 1, 500))
        with self.assertRaises(InvalidCouponError):
            order.calculate_final_amount(coupon_code="BADCODE")

    # 8. Valid coupon
    def test_valid_coupon_applies_discount(self):
        order = OrderManagement()
        order.add_product(Product("P1", "GROCERY", 1, 1000))
        discount = order.apply_coupon("SAVE10")
        self.assertEqual(discount, 100.0)

    # 9. Maximum discount limit enforced
    def test_maximum_discount_limit_enforced(self):
        order = OrderManagement()
        order.add_product(Product("P1", "CLOTHING", 15, 1000))  # bulk + category
        discount = order.calculate_total_discount(coupon_code="SAVE20")
        subtotal = order.calculate_subtotal()
        max_allowed = subtotal * 0.40
        self.assertLessEqual(discount, max_allowed)

    # 10. Tax (GST) calculation
    def test_gst_calculation(self):
        order = OrderManagement()
        gst = order.calculate_gst(1000)
        self.assertEqual(gst, 180.0)

    # 11. Free shipping above threshold
    def test_free_shipping_above_threshold(self):
        order = OrderManagement()
        order.add_product(Product("P1", "ELECTRONICS", 1, 1500))
        result = order.calculate_final_amount()
        self.assertEqual(result["shipping"], 0.0)

    # 12. Shipping charged below threshold
    def test_shipping_charged_below_threshold(self):
        order = OrderManagement()
        order.add_product(Product("P1", "GROCERY", 1, 200))
        result = order.calculate_final_amount()
        self.assertEqual(result["shipping"], 50)

    # 13. Bulk order discount applied
    def test_bulk_order_discount_applied(self):
        order = OrderManagement()
        order.add_product(Product("P1", "BOOKS", 10, 100))
        discount = order.calculate_bulk_discount()
        self.assertEqual(discount, 50.0)  # 5% of 1000

    # 14. No bulk discount below threshold qty
    def test_no_bulk_discount_below_threshold(self):
        order = OrderManagement()
        order.add_product(Product("P1", "BOOKS", 9, 100))
        discount = order.calculate_bulk_discount()
        self.assertEqual(discount, 0.0)

    # 15. Category discount - electronics
    def test_category_discount_electronics(self):
        order = OrderManagement()
        order.add_product(Product("P1", "ELECTRONICS", 1, 1000))
        self.assertEqual(order.calculate_category_discount(), 50.0)

    # 16. Category discount - clothing
    def test_category_discount_clothing(self):
        order = OrderManagement()
        order.add_product(Product("P1", "CLOTHING", 1, 1000))
        self.assertEqual(order.calculate_category_discount(), 100.0)

    # 17. Unknown category has zero discount
    def test_unknown_category_zero_discount(self):
        order = OrderManagement()
        order.add_product(Product("P1", "TOYS", 1, 1000))
        self.assertEqual(order.calculate_category_discount(), 0.0)

    # 18. Empty order raises
    def test_empty_order_raises(self):
        order = OrderManagement()
        with self.assertRaises(ValueError):
            order.calculate_final_amount()

    # 19. Multiple products with mixed categories and bulk qty
    def test_mixed_categories_and_bulk(self):
        order = OrderManagement()
        order.add_product(Product("P1", "ELECTRONICS", 2, 500))
        order.add_product(Product("P2", "GROCERY", 15, 50))
        result = order.calculate_final_amount()
        self.assertEqual(result["subtotal"], 1750)
        self.assertGreater(result["discount"], 0)

    # 20. Final amount calculation end-to-end with coupon
    def test_final_amount_end_to_end(self):
        order = OrderManagement()
        order.add_product(Product("P1", "ELECTRONICS", 1, 2000))
        result = order.calculate_final_amount(coupon_code="WELCOME5")
        expected_after_discount = round(2000 - result["discount"], 2)
        self.assertEqual(result["amount_after_discount"], expected_after_discount)
        self.assertEqual(
            result["final_amount"],
            round(result["amount_after_discount"] + result["gst"] + result["shipping"], 2)
        )

    # 21. Negative unit price raises
    def test_negative_unit_price_raises(self):
        with self.assertRaises(ValueError):
            Product("P1", "ELECTRONICS", 1, -100)

    # 22. No coupon applied (None) results in zero coupon discount
    def test_no_coupon_zero_discount(self):
        order = OrderManagement()
        order.add_product(Product("P1", "GROCERY", 1, 500))
        self.assertEqual(order.apply_coupon(None), 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
