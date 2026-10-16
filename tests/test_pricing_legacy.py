import datetime

import pytest

import pricing as pl


@pytest.fixture(autouse=True)
def clean_global_state():
    """
    Fixture เพื่อล้างค่าตัวแปร Global (member_points และ LOG) ก่อนเริ่มรันแต่ละ Test
    เพื่อป้องกันปัญหา Test Pollution ทำให้ Test ผ่านครบทั้งรันเดี่ยวและรันทั้งไฟล์
    """
    pl.member_points.clear()
    pl.LOG.clear()
    yield
    pl.member_points.clear()
    pl.LOG.clear()


class TestPricingCharacterization:
    """
    Characterization Tests เพื่อบันทึกพฤติกรรมจริงของโมดูล pricing_legacy.py
    (อ้างอิงจากผลลัพธ์การรันจริงในระบบ)
    """

    # --- 1. กลุ่มราคาปกติ (Normal Pricing) ---
    def test_normal_pricing_single_item(self):
        """สินค้า 1 รายการ 2 ชิ้น ชิ้นละ 100 บาท (ยอด 200 + ภาษี 7% = 214.0 บาท)"""
        items = [("สายไฟ", 2, 100.0)]
        total = pl.calc(items)
        assert total == 214.0

    # --- 2. กลุ่มซื้อจำนวนมาก (Bulk Discount Thresholds) ---
    def test_bulk_discount_exact_threshold_50(self):
        """ซื้อจำนวน 50 ชิ้นพอดี (เกณฑ์ลด 5%): 50 * 10 = 500 * 0.95 = 475 + ภาษี 7% = 508.25"""
        items = [("ขั้วไฟ", 50, 10.0)]
        total = pl.calc(items)
        assert total == 508.25

    def test_bulk_discount_below_threshold_50(self):
        """ซื้อจำนวน 49 ชิ้น (ยังไม่ถึงเกณฑ์ 50 ไม่ลด): 49 * 10 = 490 + ภาษี 7% = 524.3"""
        items = [("ขั้วไฟ", 49, 10.0)]
        total = pl.calc(items)
        assert total == 524.3

    def test_bulk_discount_exact_threshold_100(self):
        """ซื้อจำนวน 100 ชิ้นพอดี (เกณฑ์ลด 10%): 100 * 10 = 1000 * 0.9 = 900 + ภาษี 7% = 963.0"""
        items = [("ขั้วไฟ", 100, 10.0)]
        total = pl.calc(items)
        assert total == 963.0

    def test_bulk_discount_below_threshold_100(self):
        """ซื้อจำนวน 99 ชิ้น (ยังไม่ถึงเกณฑ์ 100 ได้ลด 5%): 99*10=990 * 0.95 = 940.5 + ภาษี = 1006.34"""
        items = [("ขั้วไฟ", 99, 10.0)]
        total = pl.calc(items)
        assert total == 1006.34

    # --- 3. กลุ่มจำนวนเป็นศูนย์ (Zero Quantity) ---
    def test_zero_quantity_item(self):
        """สินค้าจำนวน 0 ชิ้น ข้ามการคำนวณและคืนค่า 0.0"""
        items = [("ปลั๊กไฟ", 0, 100.0)]
        total = pl.calc(items)
        assert total == 0.0

    # --- 4. กลุ่มสมาชิกและการสะสมแต้ม (Member Discount & Loyalty Points) ---
    def test_member_discount_and_points_accumulation(self):
        """สมาชิก 'Alice' ซื้อของ 1,000 บาท ได้ลด 5% เหลือ 950 + ภาษี 7% = 1016.5 บาท และได้แต้ม 9 แต้ม"""
        items = [("หม้อแปลง", 10, 100.0)]
        total = pl.calc(items, member="Alice")
        assert total == 1016.5
        assert pl.member_points["Alice"] == 9

    def test_member_multiple_purchases_accumulates_points(self):
        """สมาชิก 'Bob' ซื้อครั้งแรกได้ 9 แต้ม ซื้อครั้งที่สองได้เพิ่มอีก 9 แต้ม รวมเป็น 18 แต้ม"""
        items = [("หม้อแปลง", 10, 100.0)]
        pl.calc(items, member="Bob")
        assert pl.member_points["Bob"] == 9
        pl.calc(items, member="Bob")
        assert pl.member_points["Bob"] == 18

    # --- 5. กลุ่มคูปอง (Coupons: SAVE50, HALF, NEWYEAR) ---
    def test_coupon_save50(self):
        """คูปอง SAVE50: ยอด 100 หัก 50 เหลือ 50 + ภาษี 7% = 53.5 บาท"""
        items = [("สวิตช์", 1, 100.0)]
        total = pl.calc(items, coupon="SAVE50")
        assert total == 53.5

    def test_coupon_half(self):
        """คูปอง HALF: ยอด 100 ลด 50% เหลือ 50 + ภาษี 7% = 53.5 บาท"""
        items = [("สวิตช์", 1, 100.0)]
        total = pl.calc(items, coupon="HALF")
        assert total == 53.5

    def test_coupon_newyear_in_january(self):
        """คูปอง NEWYEAR ในเดือนมกราคม: ยอด 100 ลด 20% เหลือ 80 + ภาษี 7% = 85.6 บาท"""
        items = [("สวิตช์", 1, 100.0)]
        january_date = datetime.date(2026, 1, 15)
        total = pl.calc(items, coupon="NEWYEAR", today=january_date)
        assert total == 85.6

    def test_coupon_newyear_outside_january(self):
        """คูปอง NEWYEAR นอกเดือนมกราคม (กุมภาพันธ์): ไม่ได้ส่วนลด ยอด 100 + ภาษี 7% = 107.0 บาท"""
        items = [("สวิตช์", 1, 100.0)]
        february_date = datetime.date(2026, 2, 10)
        total = pl.calc(items, coupon="NEWYEAR", today=february_date)
        assert total == 107.0

    # --- 6. กลุ่มยอดติดลบ (Negative Subtotal Clamped to Zero) ---
    def test_discount_greater_than_subtotal_clamps_to_zero(self):
        """ยอด 20 บาท แต่ใช้คูปอง SAVE50 (20 - 50 = -30) -> ต้องถูก clamp เป็น 0.0 + ภาษี = 0.0"""
        items = [("ตะปู", 1, 20.0)]
        total = pl.calc(items, coupon="SAVE50")
        assert total == 0.0

    # --- 7. กลุ่มค่าที่ฟังก์ชันเก็บไว้ (Audit LOG) ---
    def test_function_side_effect_records_in_log(self):
        """ตรวจสอบว่าทุกครั้งที่เรียก calc() จะมีการบันทึก tuple (member, total) ลงใน LOG เสมอ"""
        items = [("เทปพันสายไฟ", 1, 50.0)]
        total = pl.calc(items, member="Somchai")
        assert len(pl.LOG) == 1
        assert pl.LOG[0] == ("Somchai", total)
