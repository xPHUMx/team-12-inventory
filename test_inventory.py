import unittest
import os
import csv
import inventory

TEST_DB = "test_inventory.json"
TEST_CSV = "test_export.csv"


class TestInventory(unittest.TestCase):
    def setUp(self):
        # Clear test files before each test
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        if os.path.exists(TEST_CSV):
            os.remove(TEST_CSV)

    def tearDown(self):
        # Clean up files after test
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        if os.path.exists(TEST_CSV):
            os.remove(TEST_CSV)

    # ==========================================
    # US-01: ดูรายการสินค้าทั้งหมด
    # ==========================================
    def test_us01_ac1_list_with_items(self):
        """AC-1: Given มีสินค้าอย่างน้อย 1 รายการ | When list | Then แสดงชื่อ รหัส และคงเหลือครบ"""
        inventory.add_item("PEN01", "ปากกาลูกลื่น", 20, filepath=TEST_DB)
        inventory.add_item("BOOK01", "สมุด A4", 10, filepath=TEST_DB)

        output = inventory.list_items(filepath=TEST_DB)
        self.assertIn("PEN01", output)
        self.assertIn("ปากกาลูกลื่น", output)
        self.assertIn("20", output)
        self.assertIn("BOOK01", output)
        self.assertIn("สมุด A4", output)
        self.assertIn("10", output)

    def test_us01_ac2_list_empty(self):
        """AC-2: Given ยังไม่มีสินค้าในระบบ | When list | Then แสดงข้อความ 'ยังไม่มีสินค้าในระบบ'"""
        output = inventory.list_items(filepath=TEST_DB)
        self.assertEqual(output, "ยังไม่มีสินค้าในระบบ")

    # ==========================================
    # US-02: เพิ่มสินค้าใหม่เข้าระบบ
    # ==========================================
    def test_us02_ac1_add_new_item_success(self):
        """AC-1: Given ยังไม่มีสินค้ารหัสนี้ | When เพิ่มสินค้า | Then บันทึกและแสดงเมื่อเรียก list"""
        success, msg = inventory.add_item("PEN01", "ปากกา", 15, filepath=TEST_DB)
        self.assertTrue(success)

        items = inventory.load_items(filepath=TEST_DB)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["code"], "PEN01")
        self.assertEqual(items[0]["name"], "ปากกา")
        self.assertEqual(items[0]["quantity"], 15)

    def test_us02_ac2_add_duplicate_code_fails(self):
        """AC-2: Given มีสินค้ารหัสนี้อยู่แล้ว | When เพิ่มรหัสเดิม | Then ปฏิเสธและแสดง 'รหัสสินค้าซ้ำ'"""
        inventory.add_item("PEN01", "ปากกา", 15, filepath=TEST_DB)
        success, msg = inventory.add_item("PEN01", "ปากกาแดง", 30, filepath=TEST_DB)

        self.assertFalse(success)
        self.assertEqual(msg, "รหัสสินค้าซ้ำ")
        # Check that original data is not overwritten
        items = inventory.load_items(filepath=TEST_DB)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "ปากกา")

    # ==========================================
    # US-03: แก้ไขจำนวนสินค้าเมื่อรับหรือจ่ายของ
    # ==========================================
    def test_us03_ac1_adjust_quantity_success(self):
        """AC-1: Given มีสินค้าคงเหลือ N | When รับเข้าหรือจ่ายออกที่ไม่ติดลบ | Then อัปเดตยอดคงเหลือถูกต้อง"""
        inventory.add_item("RULER01", "ไม้บรรทัด", 10, filepath=TEST_DB)

        # รับเข้า +5
        success, msg = inventory.adjust_quantity("RULER01", 5, filepath=TEST_DB)
        self.assertTrue(success)
        items = inventory.load_items(filepath=TEST_DB)
        self.assertEqual(items[0]["quantity"], 15)

        # จ่ายออก -8
        success, msg = inventory.adjust_quantity("RULER01", -8, filepath=TEST_DB)
        self.assertTrue(success)
        items = inventory.load_items(filepath=TEST_DB)
        self.assertEqual(items[0]["quantity"], 7)

    def test_us03_ac2_adjust_quantity_insufficient(self):
        """AC-2: Given มีสินค้าคงเหลือ N | When จ่ายออกมากกว่า N | Then ปฏิเสธ 'จำนวนคงเหลือไม่พอ' และยอดไม่เปลี่ยน"""
        inventory.add_item("RULER01", "ไม้บรรทัด", 5, filepath=TEST_DB)

        # จ่ายออก -10 (เกิน 5)
        success, msg = inventory.adjust_quantity("RULER01", -10, filepath=TEST_DB)
        self.assertFalse(success)
        self.assertEqual(msg, "จำนวนคงเหลือไม่พอ")

        items = inventory.load_items(filepath=TEST_DB)
        self.assertEqual(items[0]["quantity"], 5)  # ยอดต้องคงเดิม

    # ==========================================
    # US-04: ค้นหาสินค้าด้วยชื่อหรือรหัส
    # ==========================================
    def test_us04_ac1_search_found(self):
        """AC-1: Given มีสินค้าตรงคำค้น | When ค้นหา | Then แสดงรายการที่ตรง"""
        inventory.add_item("PEN01", "ปากกาลูกลื่น", 10, filepath=TEST_DB)
        inventory.add_item("PENCIL01", "ดินสอ 2B", 20, filepath=TEST_DB)

        output_name = inventory.search_items("ดินสอ", filepath=TEST_DB)
        self.assertIn("PENCIL01", output_name)
        self.assertIn("ดินสอ 2B", output_name)
        self.assertNotIn("ปากกาลูกลื่น", output_name)

        output_code = inventory.search_items("PEN01", filepath=TEST_DB)
        self.assertIn("PEN01", output_code)

    def test_us04_ac2_search_not_found(self):
        """AC-2: Given ไม่มีสินค้าตรงคำค้น | When ค้นหา | Then แสดง 'ไม่พบสินค้าที่ตรงกับคำค้น'"""
        inventory.add_item("PEN01", "ปากกา", 10, filepath=TEST_DB)
        output = inventory.search_items("ยางลบ", filepath=TEST_DB)
        self.assertEqual(output, "ไม่พบสินค้าที่ตรงกับคำค้น")

    # ==========================================
    # US-05: ส่งออกรายงานสต็อกเป็นไฟล์ CSV
    # ==========================================
    def test_us05_ac1_export_csv_with_items(self):
        """AC-1: Given มีสินค้าอย่างน้อย 1 รายการ | When ส่งออก CSV | Then ได้ไฟล์ CSV มีหัวคอลัมน์ครบทุกรายการ"""
        inventory.add_item("PEN01", "ปากกา", 10, filepath=TEST_DB)
        inventory.add_item("ERAS01", "ยางลบ", 25, filepath=TEST_DB)

        success, msg = inventory.export_csv(TEST_CSV, filepath=TEST_DB)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(TEST_CSV))

        with open(TEST_CSV, "r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f))
            self.assertEqual(reader[0], ["รหัส", "ชื่อ", "จำนวนคงเหลือ"])
            self.assertEqual(len(reader), 3)

    def test_us05_ac2_export_csv_empty(self):
        """AC-2: Given ยังไม่มีสินค้า | When ส่งออก CSV | Then ได้ไฟล์หัวคอลัมน์และแจ้ง 'ยังไม่มีข้อมูลสินค้า'"""
        success, msg = inventory.export_csv(TEST_CSV, filepath=TEST_DB)
        self.assertTrue(success)
        self.assertIn("ยังไม่มีข้อมูลสินค้า", msg)

        with open(TEST_CSV, "r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f))
            self.assertEqual(reader[0], ["รหัส", "ชื่อ", "จำนวนคงเหลือ"])
            self.assertEqual(len(reader), 1)


if __name__ == "__main__":
    unittest.main()
