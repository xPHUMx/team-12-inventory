"""
โมดูลคำนวณราคาและส่วนลดของระบบ Inventory (ฉบับ Refactored สำหรับ Lab 05)
แก้ปัญหา Code Smells จาก pricing_legacy.py โดยแยกฟังก์ชันตามความรับผิดชอบ (SRP),
กำจัด Magic Numbers และคงพฤติกรรมเดิมไว้ 100%
"""
import datetime
from collections.abc import Sequence
from dataclasses import dataclass

# --- ค่าคงที่ระบบ (Named Constants) ---
TAX_RATE: float = 0.07

BULK_TIER_1_THRESHOLD: int = 50
BULK_TIER_1_RATE: float = 0.95   # ลด 5%

BULK_TIER_2_THRESHOLD: int = 100
BULK_TIER_2_RATE: float = 0.90   # ลด 10%

MEMBER_DISCOUNT_RATE: float = 0.95  # สมาชิกลด 5%
POINTS_EARN_DIVISOR: int = 100      # 1 แต้มต่อทุก 100 บาท

# รักษาสถานะสำหรับ Backwards Compatibility ตาม Characterization Tests
member_points: dict[str, int] = {}
LOG: list[tuple[str | None, float]] = []


@dataclass(frozen=True)
class PricingItem:
    """โครงสร้างข้อมูลตัวแทนสินค้าสำหรับการคำนวณราคา"""
    name: str
    quantity: int
    unit_price: float


def _calculate_item_subtotal(quantity: int, unit_price: float) -> float:
    """คำนวณราคารายการสินค้าพร้อมคิดส่วนลดการซื้อจำนวนมาก (Bulk Discount)"""
    if quantity <= 0:
        return 0.0

    subtotal = float(quantity * unit_price)

    # คิดส่วนลดตามปริมาณการสั่งซื้อ
    if quantity >= BULK_TIER_2_THRESHOLD:
        subtotal *= BULK_TIER_2_RATE
    elif quantity >= BULK_TIER_1_THRESHOLD:
        subtotal *= BULK_TIER_1_RATE

    return subtotal


def _apply_member_benefit(subtotal: float, member: str | None) -> float:
    """คำนวณส่วนลดสมาชิกและสะสมคะแนน Loyalty Points"""
    if member is None:
        return subtotal

    if member not in member_points:
        member_points[member] = 0

    # สมาชิกลด 5%
    discounted = subtotal * MEMBER_DISCOUNT_RATE

    # สะสมแต้ม 1 แต้มต่อ 100 บาท (คำนวณจากยอดหลังลดสมาชิก)
    points_earned = int(discounted / POINTS_EARN_DIVISOR)
    member_points[member] += points_earned

    return discounted


def _apply_coupon_benefit(
    subtotal: float, coupon: str | None, today: datetime.date | None
) -> float:
    """ตรวจสอบและคำนวณส่วนลดจากคูปอง (SAVE50, HALF, NEWYEAR)"""
    if coupon is None:
        return subtotal

    total = subtotal
    if coupon == "SAVE50":
        total -= 50.0
    elif coupon == "HALF":
        total *= 0.5
    elif coupon == "NEWYEAR":
        check_date = today if today is not None else datetime.date.today()
        if check_date.month == 1:
            total *= 0.8

    return total


def _apply_tax_and_round(amount: float) -> float:
    """คิดภาษีมูลค่าเพิ่มและปัดเศษทศนิยม 2 ตำแหน่ง"""
    tax_amount = amount * TAX_RATE
    return round(amount + tax_amount, 2)


def calc(
    items: Sequence[tuple[str, int, float]],
    member: str | None = None,
    coupon: str | None = None,
    today: datetime.date | None = None,
) -> float:
    """
    ฟังก์ชันหลักสำหรับคำนวณราคาสุทธิของสินค้า
    - คำนวณส่วนลดซื้อเหมา
    - คำนวณส่วนลดสมาชิกและแต้มสะสม
    - คำนวณส่วนลดคูปอง
    - ป้องกันยอดติดลบ (Clamp to zero)
    - บวกภาษีมูลค่าเพิ่มและบันทึกประวัติ (LOG)
    """
    # 1. คำนวณยอดรวมสินค้าพร้อมส่วนลดซื้อจำนวนมาก
    subtotal = 0.0
    for item in items:
        qty = item[1]
        price = item[2]
        subtotal += _calculate_item_subtotal(qty, price)

    # 2. คิดส่วนลดสมาชิก
    subtotal = _apply_member_benefit(subtotal, member)

    # 3. คิดส่วนลดคูปอง
    subtotal = _apply_coupon_benefit(subtotal, coupon, today)

    # 4. ป้องกันยอดติดลบ
    if subtotal < 0.0:
        subtotal = 0.0

    # 5. บวกภาษีมูลค่าเพิ่มและปัดเศษ
    final_total = _apply_tax_and_round(subtotal)

    # 6. บันทึกประวัติการคำนวณลง LOG
    LOG.append((member, final_total))

    return final_total
