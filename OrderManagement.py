class OrderManagement:
    PRODUCTS = {
        "P101": {"category": "electronics", "price": 20000, "stock": 10},
        "P102": {"category": "clothing", "price": 2000, "stock": 50},
        "P103": {"category": "grocery", "price": 500, "stock": 100},
        "P104": {"category": "books", "price": 800, "stock": 20},
    }

    COUPONS = {
        "SAVE10": 10,
        "SAVE20": 20
    }

    def __init__(self, products, coupon=None):
        self.products = products
        self.coupon = coupon

    def validate_products(self):
        for item in self.products:
            pid = item["product_id"]
            qty = item["quantity"]

            if pid not in self.PRODUCTS:
                raise ValueError("Invalid product")
            if qty <= 0:
                raise ValueError("Quantity must be positive")
            if qty > self.PRODUCTS[pid]["stock"]:
                raise ValueError("Out of stock")

    def subtotal(self):
        return sum(
            self.PRODUCTS[item["product_id"]]["price"] * item["quantity"]
            for item in self.products
        )

    def category_discount(self):
        total = 0
        for item in self.products:
            product = self.PRODUCTS[item["product_id"]]
            amount = product["price"] * item["quantity"]

            if product["category"] == "electronics":
                total += amount * 0.05
            elif product["category"] == "clothing":
                total += amount * 0.10
            elif product["category"] == "grocery":
                total += amount * 0.03

        return total

    def bulk_discount(self):
        total_qty = sum(item["quantity"] for item in self.products)
        return self.subtotal() * 0.05 if total_qty >= 10 else 0

    def coupon_discount(self, amount):
        if self.coupon is None:
            return 0
        if self.coupon not in self.COUPONS:
            raise ValueError("Invalid coupon code")
        return amount * self.COUPONS[self.coupon] / 100

    def calculate(self):
        self.validate_products()

        subtotal = self.subtotal()
        category_discount = self.category_discount()
        bulk_discount = self.bulk_discount()

        discount_base = max(0, subtotal - category_discount - bulk_discount)
        coupon_discount = self.coupon_discount(discount_base)

        # Maximum total discount = 30% of subtotal
        total_discount = min(
            category_discount + bulk_discount + coupon_discount,
            subtotal * 0.30
        )

        taxable_amount = subtotal - total_discount
        gst = taxable_amount * 0.18

        # Free shipping above ₹5000
        shipping = 0 if taxable_amount >= 5000 else 100

        final_amount = taxable_amount + gst + shipping

        return {
            "subtotal": round(subtotal, 2),
            "discount": round(total_discount, 2),
            "gst": round(gst, 2),
            "shipping": round(shipping, 2),
            "final_amount": round(final_amount, 2)
        }


if __name__ == "__main__":
    order = OrderManagement([
        {"product_id": "P101", "quantity": 1},
        {"product_id": "P102", "quantity": 2}
    ], "SAVE10")
    print(order.calculate())
