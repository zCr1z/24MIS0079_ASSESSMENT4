"""
E-Commerce Order Processing System
Development Program: OrderManagement.java equivalent in Python
"""


class OutOfStockError(Exception):
    pass


class InvalidCouponError(Exception):
    pass


class InvalidProductError(Exception):
    pass


class Product:
    def __init__(self, product_id, category, quantity, unit_price, discount_percent=0,
                 tax_percent=0, in_stock=True):
        if not product_id:
            raise InvalidProductError("Product ID is required")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative")

        self.product_id = product_id
        self.category = category
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount_percent = discount_percent
        self.tax_percent = tax_percent
        self.in_stock = in_stock

    def line_total(self):
        return round(self.quantity * self.unit_price, 2)


class OrderManagement:
    COUPONS = {
        "SAVE10": 10,
        "SAVE20": 20,
        "WELCOME5": 5,
    }
    CATEGORY_DISCOUNTS = {
        "ELECTRONICS": 5,
        "CLOTHING": 10,
        "GROCERY": 2,
        "BOOKS": 7,
    }
    MAX_DISCOUNT_PERCENT = 40
    FREE_SHIPPING_THRESHOLD = 1000
    BULK_ORDER_QTY = 10
    BULK_DISCOUNT_PERCENT = 5
    GST_PERCENT = 18
    SHIPPING_CHARGE = 50

    def __init__(self):
        self.products = []

    def add_product(self, product: Product):
        if product.quantity <= 0:
            raise ValueError("Quantity must be greater than zero to add to order")
        if not product.in_stock:
            raise OutOfStockError(f"Product {product.product_id} is out of stock")
        self.products.append(product)

    def calculate_subtotal(self):
        return round(sum(p.line_total() for p in self.products), 2)

    def calculate_category_discount(self):
        total_discount = 0.0
        for p in self.products:
            pct = self.CATEGORY_DISCOUNTS.get(p.category, 0)
            total_discount += p.line_total() * (pct / 100)
        return round(total_discount, 2)

    def calculate_bulk_discount(self):
        total_discount = 0.0
        for p in self.products:
            if p.quantity >= self.BULK_ORDER_QTY:
                total_discount += p.line_total() * (self.BULK_DISCOUNT_PERCENT / 100)
        return round(total_discount, 2)

    def apply_coupon(self, coupon_code):
        if coupon_code is None:
            return 0.0
        if coupon_code not in self.COUPONS:
            raise InvalidCouponError(f"Invalid coupon code: {coupon_code}")
        subtotal = self.calculate_subtotal()
        discount = subtotal * (self.COUPONS[coupon_code] / 100)
        return round(discount, 2)

    def calculate_total_discount(self, coupon_code=None):
        subtotal = self.calculate_subtotal()
        discount = (self.calculate_category_discount() +
                    self.calculate_bulk_discount() +
                    self.apply_coupon(coupon_code))
        max_allowed = subtotal * (self.MAX_DISCOUNT_PERCENT / 100)
        return round(min(discount, max_allowed), 2)

    def calculate_gst(self, amount):
        return round(amount * (self.GST_PERCENT / 100), 2)

    def calculate_shipping(self, amount_after_discount):
        if amount_after_discount >= self.FREE_SHIPPING_THRESHOLD:
            return 0.0
        return self.SHIPPING_CHARGE

    def calculate_final_amount(self, coupon_code=None):
        if not self.products:
            raise ValueError("Cannot process an order with no products")

        subtotal = self.calculate_subtotal()
        discount = self.calculate_total_discount(coupon_code)
        amount_after_discount = round(subtotal - discount, 2)
        gst = self.calculate_gst(amount_after_discount)
        shipping = self.calculate_shipping(amount_after_discount)
        final_amount = round(amount_after_discount + gst + shipping, 2)

        return {
            "subtotal": subtotal,
            "discount": discount,
            "amount_after_discount": amount_after_discount,
            "gst": gst,
            "shipping": shipping,
            "final_amount": final_amount,
        }


if __name__ == "__main__":
    order = OrderManagement()
    order.add_product(Product("P1", "ELECTRONICS", 2, 500, in_stock=True))
    order.add_product(Product("P2", "BOOKS", 12, 100, in_stock=True))
    print(order.calculate_final_amount(coupon_code="SAVE10"))
