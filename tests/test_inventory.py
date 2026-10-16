import pytest
from inventory import Inventory, InventoryItem


class TestLowStockItemsTDD:
    """
    ชุดการทดสอบแบบ TDD สำหรับเมธอด low_stock_items(threshold)
    ตามข้อกำหนด 6 กรณีในใบงาน Lab 5 ขั้นที่ 2
    """

    def test_all_items_above_threshold_returns_empty_list(self):
        """กรณีที่ 1: สินค้าทุกรายการมีจำนวนมากกว่า threshold -> คืน list ว่าง"""
        inv = Inventory()
        inv.add_item("สายไฟ A", 50, 20.0)
        inv.add_item("ท่อ PVC", 25, 45.0)

        result = inv.low_stock_items(threshold=10)
        assert result == []

    def test_item_exact_threshold_is_included(self):
        """กรณีที่ 2: มีสินค้าที่จำนวนเท่ากับ threshold พอดี -> ต้องถูกนับรวมด้วย (<= threshold)"""
        inv = Inventory()
        inv.add_item("เบรกเกอร์", 10, 150.0)
        inv.add_item("ปลั๊กไฟ", 15, 30.0)

        result = inv.low_stock_items(threshold=10)
        assert result == ["เบรกเกอร์"]

    def test_multiple_matching_items_sorted_by_name(self):
        """กรณีที่ 3: มีสินค้าเข้าเกณฑ์หลายรายการ -> ผลลัพธ์ต้องเรียงตามชื่อ (A-Z / ก-ฮ) ไม่ใช่ตามลำดับที่เพิ่ม"""
        inv = Inventory()
        # เพิ่มโดยไม่เรียงชื่อ: ฮ, ก, ข
        inv.add_item("ฮาร์ดดิสก์", 3, 2000.0)
        inv.add_item("กรรไกรตัดสาย", 5, 120.0)
        inv.add_item("ขั้วหลอดไฟ", 2, 25.0)
        inv.add_item("สายไฟใหญ่", 50, 80.0)  # เกิน threshold

        result = inv.low_stock_items(threshold=5)
        # ต้องเรียงตามชื่อสินค้า: กรรไกรตัดสาย, ขั้วหลอดไฟ, ฮาร์ดดิสก์
        assert result == ["กรรไกรตัดสาย", "ขั้วหลอดไฟ", "ฮาร์ดดิสก์"]

    def test_empty_inventory_returns_empty_list(self):
        """กรณีที่ 4: คลังว่างเปล่า -> คืน list ว่าง ไม่ใช่โยน Error"""
        inv = Inventory()
        result = inv.low_stock_items(threshold=10)
        assert result == []

    def test_threshold_zero_returns_only_out_of_stock_items(self):
        """กรณีที่ 5: threshold เป็น 0 -> คืนเฉพาะสินค้าที่มีสต็อกเหลือ 0 ชิ้น"""
        inv = Inventory()
        inv.add_item("น็อตตัวเมีย", 0, 1.0)
        inv.add_item("ตะปู", 5, 2.0)
        inv.add_item("พุกพลาสติก", 0, 0.5)

        result = inv.low_stock_items(threshold=0)
        assert result == ["น็อตตัวเมีย", "พุกพลาสติก"]

    def test_negative_threshold_returns_empty_list(self):
        """กรณีที่ 6: threshold ติดลบ -> คืน list ว่าง เพราะจำนวนสินค้าในระบบไม่สามารถติดลบได้"""
        inv = Inventory()
        inv.add_item("หลอด LED", 0, 80.0)
        inv.add_item("สวิตช์ไฟ", 10, 60.0)

        result = inv.low_stock_items(threshold=-1)
        assert result == []
