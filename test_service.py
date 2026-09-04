"""
Unit Tests สำหรับระบบ Inventory System ใน Lab 3 (Spec-Driven Development)
"""
import unittest
from io import StringIO
import sys
from src.models import Product, StockTransaction
from src.notifiers import NotifierFactory, EmailNotifier, SMSNotifier
from src.service import InventoryService


class TestInventoryService(unittest.TestCase):
    def setUp(self):
        # สร้าง Notifier ด้วย Factory
        self.email_notifier = NotifierFactory.create("email", recipient_email="admin@eng-shop.com")
        self.sms_notifier = NotifierFactory.create("sms", phone_number="089-123-4567")

        # สร้าง Service พร้อมฉีด Dependencies (Observer)
        self.service = InventoryService(observers=[self.email_notifier, self.sms_notifier])

        # เพิ่มข้อมูลสินค้าทดสอบ
        self.p1 = Product(code="WIRE01", name="สายไฟ 2.5 sq.mm", category="ไฟฟ้า", quantity=20, unit_price=50.0, threshold=15)
        self.p2 = Product(code="BRK01", name="เบรกเกอร์ 30A", category="ไฟฟ้า", quantity=5, unit_price=200.0, threshold=2)
        self.p3 = Product(code="PIPE01", name="ท่อ PVC 1 นิ้ว", category="ประปา", quantity=50, unit_price=80.0, threshold=10)

        self.service.add_product(self.p1)
        self.service.add_product(self.p2)
        self.service.add_product(self.p3)

    # -------------------------------------------------------------
    # US-01: รับ / จ่าย สินค้า
    # -------------------------------------------------------------
    def test_us01_receive_product_success(self):
        """รับสินค้าเข้าสต็อกสำเร็จ และอัปเดตยอดคงเหลือ"""
        new_qty = self.service.receive("WIRE01", 30)
        self.assertEqual(new_qty, 50)
        self.assertEqual(self.p1.quantity, 50)

    def test_us01_issue_product_success(self):
        """จ่ายสินค้าเมื่อสต็อกพอ"""
        new_qty = self.service.issue("PIPE01", 10)
        self.assertEqual(new_qty, 40)
        self.assertEqual(self.p3.quantity, 40)

    def test_us01_issue_insufficient_stock(self):
        """จ่ายสินค้าเมื่อสต็อกไม่พอ ต้องเกิด ValueError และยอดไม่เปลี่ยน"""
        with self.assertRaises(ValueError):
            self.service.issue("WIRE01", 25)
        self.assertEqual(self.p1.quantity, 20)

    # -------------------------------------------------------------
    # US-02: แจ้งเตือนเมื่อสต็อกต่ำกว่า threshold (< threshold)
    # -------------------------------------------------------------
    def test_us02_issue_triggers_low_stock_notification(self):
        """จ่ายสินค้าจนสต็อกคงเหลือต่ำกว่า threshold (< 15) ต้องเกิดการแจ้งเตือน"""
        captured_output = StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            # สต็อกเริ่มต้น 20 จ่าย 8 เหลือ 12 (< 15) -> ต้องแจ้งเตือน
            self.service.issue("WIRE01", 8)
        finally:
            sys.stdout = old_stdout

        output = captured_output.getvalue()
        self.assertIn("[Email: admin@eng-shop.com]", output)
        self.assertIn("[SMS: 089-123-4567]", output)
        self.assertIn("WIRE01", output)

    def test_us02_issue_does_not_trigger_when_above_threshold(self):
        """จ่ายสินค้าแต่สต็อกยังสูงกว่า threshold ไม่ต้องแจ้งเตือน"""
        captured_output = StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            # สต็อกเริ่มต้น 50 จ่าย 10 เหลือ 40 (> 10) -> ไม่ต้องแจ้งเตือน
            self.service.issue("PIPE01", 10)
        finally:
            sys.stdout = old_stdout

        output = captured_output.getvalue()
        self.assertEqual(output.strip(), "")

    def test_us02_issue_exact_threshold_edge_case(self):
        """Edge Case: จ่ายจนสต็อกเท่ากับ threshold พอดี ต้องไม่แจ้งเตือน (เพราะแจ้งเฉพาะเมื่อ < threshold)"""
        captured_output = StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            # สต็อกเริ่มต้น 20 จ่าย 5 เหลือ 15 (เท่ากับ threshold 15 พอดี) -> ต้องไม่แจ้งเตือน
            self.service.issue("WIRE01", 5)
        finally:
            sys.stdout = old_stdout

        output = captured_output.getvalue()
        self.assertEqual(output.strip(), "")

    # -------------------------------------------------------------
    # US-03: รายงานมูลค่าสต็อกแยกตามหมวดหมู่
    # -------------------------------------------------------------
    def test_us03_get_category_valuation(self):
        """คำนวณมูลค่าสต็อกแยกหมวดหมู่ได้ถูกต้อง"""
        # หมวดไฟฟ้า: (20 * 50) + (5 * 200) = 1,000 + 1,000 = 2,000 บาท
        # หมวดประปา: (50 * 80) = 4,000 บาท
        valuation = self.service.get_category_valuation()
        self.assertEqual(valuation["ไฟฟ้า"], 2000.0)
        self.assertEqual(valuation["ประปา"], 4000.0)

    # -------------------------------------------------------------
    # US-04: ตั้งค่า Threshold แยกตามสินค้า
    # -------------------------------------------------------------
    def test_us04_set_threshold(self):
        """ตั้งค่า threshold ใหม่สำเร็จ"""
        self.service.set_threshold("PIPE01", 25)
        self.assertEqual(self.p3.threshold, 25)

    # -------------------------------------------------------------
    # US-05: Observer Dynamic Attach/Detach
    # -------------------------------------------------------------
    def test_us05_observer_detach(self):
        """ยกเลิก Observer แล้วต้องไม่ได้รับแจ้งเตือน"""
        self.service.detach_observer(self.sms_notifier)
        captured_output = StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            self.service.issue("WIRE01", 8)
        finally:
            sys.stdout = old_stdout

        output = captured_output.getvalue()
        self.assertIn("[Email: admin@eng-shop.com]", output)
        self.assertNotIn("[SMS:", output)


if __name__ == "__main__":
    unittest.main()
