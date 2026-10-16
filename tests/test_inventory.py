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


class TestSellMethodAndTestGap:
    """
    ชุดการทดสอบสำหรับเมธอด sell ของคลาส Inventory
    เปรียบเทียบกรณีทั่วไปที่ AI สร้างให้ vs กรณีขอบเขตและ Error Path ที่เขียนเสริม (ขั้นที่ 4)
    """

    # --- กรณีพื้นฐานที่ AI สร้างให้ (Happy Path ผ่านง่ายเกินไป) ---
    def test_sell_basic_happy_path_from_ai(self):
        """กรณีที่ AI มักเขียนให้: ขายจำนวนปกติที่มีพอ สต็อกลดลงถูกต้อง"""
        inv = Inventory()
        inv.add_item("ปากกา", 10, 15.0)
        remaining = inv.sell("ปากกา", 3)
        assert remaining == 7
        assert inv._items["ปากกา"].quantity == 7

    # --- กรณีที่ 1 (ค่าขอบ): ขายเท่ากับจำนวนคงเหลือทั้งหมดพอดี ---
    def test_sell_exact_remaining_quantity_becomes_zero(self):
        """กรณีค่าขอบ: มี 10 ชิ้น ขาย 10 ชิ้นพอดี -> ต้องขายได้และเหลือ 0 ชิ้น"""
        inv = Inventory()
        inv.add_item("สมุด", 10, 25.0)
        remaining = inv.sell("สมุด", 10)
        assert remaining == 0
        assert inv._items["สมุด"].quantity == 0

    # --- กรณีที่ 2 (ค่าที่ไม่ควรรับ): ขายจำนวน 0 ชิ้น ---
    def test_sell_zero_amount_raises_value_error(self):
        """กรณีค่าที่ไม่ควรรับ: ขายจำนวน 0 ชิ้น -> ต้อง raise ValueError"""
        inv = Inventory()
        inv.add_item("ดินสอ", 10, 5.0)
        with pytest.raises(ValueError, match="จำนวนที่ขายต้องมากกว่าศูนย์"):
            inv.sell("ดินสอ", 0)

    # --- กรณีที่ 3 (ค่าที่ไม่ควรรับ): ขายจำนวนติดลบ ---
    def test_sell_negative_amount_raises_value_error(self):
        """กรณีค่าที่ไม่ควรรับ: ขายจำนวนติดลบ (-5) -> ต้อง raise ValueError ไม่ใช่เพิ่มสต็อก"""
        inv = Inventory()
        inv.add_item("ยางลบ", 10, 8.0)
        with pytest.raises(ValueError, match="จำนวนที่ขายต้องมากกว่าศูนย์"):
            inv.sell("ยางลบ", -5)

    # --- กรณีที่ 4 (ค่าที่ไม่ควรรับ): ขายเกินจำนวนคงเหลือในคลัง ---
    def test_sell_more_than_available_raises_value_error(self):
        """กรณีค่าที่ไม่ควรรับ: สต็อกมี 5 ชิ้น แต่สั่งขาย 10 ชิ้น -> ต้องปฏิเสธและยอดคงเดิม"""
        inv = Inventory()
        inv.add_item("ไม้บรรทัด", 5, 12.0)
        with pytest.raises(ValueError, match="ไม่เพียงพอสำหรับการขาย"):
            inv.sell("ไม้บรรทัด", 10)
        assert inv._items["ไม้บรรทัด"].quantity == 5

    # --- กรณีที่ 5 (เส้นทาง Error): สินค้าไม่มีในคลัง ---
    def test_sell_non_existent_item_raises_key_error(self):
        """กรณีเส้นทาง Error: พยายามขายสินค้าที่ไม่มีในระบบ -> ต้อง raise KeyError"""
        inv = Inventory()
        with pytest.raises(KeyError, match="ไม่พบสินค้า 'สินค้าผี' ในระบบ"):
            inv.sell("สินค้าผี", 1)


class TestInventoryCoreOperationsAndValidation:
    """
    ชุดการทดสอบเพิ่มเติมสำหรับเมธอดพื้นฐานของ Inventory และ InventoryItem เพื่อความครอบคลุม
    """

    def test_item_validation_empty_name(self):
        with pytest.raises(ValueError, match="ชื่อสินค้าต้องไม่ว่างเปล่า"):
            InventoryItem("", 10, 100.0)

    def test_item_validation_negative_quantity(self):
        with pytest.raises(ValueError, match="จำนวนสินค้าต้องไม่ติดลบ"):
            InventoryItem("ทดสอบ", -1, 100.0)

    def test_item_validation_negative_or_zero_price(self):
        with pytest.raises(ValueError, match="ราคาต้องมากกว่าศูนย์"):
            InventoryItem("ทดสอบ", 10, 0.0)

    def test_add_duplicate_item_raises_value_error(self):
        inv = Inventory()
        inv.add_item("สินค้า A", 10, 100.0)
        with pytest.raises(ValueError, match="มีอยู่ในระบบแล้ว"):
            inv.add_item("สินค้า A", 5, 120.0)

    def test_restock_success(self):
        inv = Inventory()
        inv.add_item("สายไฟ", 10, 50.0)
        new_qty = inv.restock("สายไฟ", 15)
        assert new_qty == 25
        assert inv._items["สายไฟ"].quantity == 25

    def test_restock_negative_or_zero_raises_value_error(self):
        inv = Inventory()
        inv.add_item("สายไฟ", 10, 50.0)
        with pytest.raises(ValueError, match="จำนวนที่เติมต้องมากกว่าศูนย์"):
            inv.restock("สายไฟ", 0)

    def test_restock_non_existent_item_raises_key_error(self):
        inv = Inventory()
        with pytest.raises(KeyError, match="ไม่พบสินค้า"):
            inv.restock("ไม่มีจริง", 5)

    def test_get_total_value(self):
        inv = Inventory()
        inv.add_item("สินค้า 1", 10, 20.0)  # 200
        inv.add_item("สินค้า 2", 5, 100.0)  # 500
        assert inv.get_total_value() == 700.0
