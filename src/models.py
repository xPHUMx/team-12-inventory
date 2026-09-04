"""
โมดูล Domain Models สำหรับระบบจัดการสต็อกสินค้า
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Category:
    """
    เอนทิตีหมวดหมู่สินค้า
    """
    id: str
    name: str


@dataclass
class Product:
    """
    เอนทิตีสินค้าในคลัง
    """
    code: str
    name: str
    category: str
    quantity: int
    unit_price: float
    threshold: int = 10

    def is_low_stock(self) -> bool:
        """
        ตรวจสอบว่าสินค้ามีสต็อกต่ำกว่า threshold หรือไม่
        (ตาม Acceptance Criteria: สต็อกต้องน้อยกว่า threshold เท่านั้น)
        """
        return self.quantity < self.threshold

    def calculate_valuation(self) -> float:
        """
        คำนวณมูลค่ารวมของสินค้าในสต็อก
        """
        return self.quantity * self.unit_price


@dataclass
class StockTransaction:
    """
    ประวัติการทำรายการรับ-จ่ายสินค้า
    """
    transaction_id: str
    product_code: str
    action: Literal["RECEIVE", "ISSUE"]
    amount: int
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
