import unittest
import json
from grocery_profile_resolver import lookup_preferred_item, check_order_history

class TestGroceryProfileResolver(unittest.TestCase):
    def test_milk_resolution(self):
        res = lookup_preferred_item("buy 2 bottles of milk")
        self.assertEqual(res["status"], "resolved")
        self.assertEqual(res["category"], "milk")
        self.assertEqual(res["quantity"], 2)
        self.assertEqual(res["primary"]["brand"], "Juhayna")
        self.assertEqual(res["primary"]["size"], "1L")
        self.assertEqual(res["resolved_string"], "2 packs of Juhayna Full Cream Milk 1L")

    def test_sugar_resolution(self):
        res = lookup_preferred_item("buy sugar")
        self.assertEqual(res["status"], "resolved")
        self.assertEqual(res["category"], "sugar")
        self.assertEqual(res["quantity"], 1)
        self.assertEqual(res["primary"]["brand"], "Al Doha")
        self.assertEqual(res["primary"]["size"], "1kg")

    def test_rice_resolution(self):
        res = lookup_preferred_item("2 bags of rice")
        self.assertEqual(res["status"], "resolved")
        self.assertEqual(res["category"], "rice")
        self.assertEqual(res["quantity"], 2)
        self.assertEqual(res["primary"]["brand"], "Al Doha")

    def test_history_check(self):
        hist = check_order_history("milk")
        self.assertGreater(hist["total_orders"], 0)

if __name__ == "__main__":
    unittest.main()
