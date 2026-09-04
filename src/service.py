"""
โมดูล Service สำหรับจัดการ Business Logic ของคลังสินค้า (ทำหน้าที่เป็น Subject ใน Observer Pattern)
"""
from typing import Sequence
import uuid
from src.models import Product, StockTransaction
from src.notifiers import Notifier


class InventoryService:
    """
    Service หลักสำหรับจัดการสต็อกสินค้า
    - ทำหน้าที่เป็น Subject คอยแจ้งเตือน Observers (Notifiers) เมื่อสต็อกต่ำ
    - ยึดหลัก Single Responsibility Principle (ดูแลเฉพาะ Business Logic)
    - ยึดหลัก Dependency Inversion Principle (พึ่งพา Notifier Protocol ไม่ผูกกับ Concrete Class)
    """
    def __init__(self, observers: Sequence[Notifier] | None = None) -> None:
        """
        กำหนดค่าเริ่มต้นของ InventoryService พร้อมรับ Dependency ผ่าน Constructor
        :param observers: ลิสต์ของ Notifier observers
        """
        self._products: dict[str, Product] = {}
        self._categories: set[str] = set()
        self._transactions: list[StockTransaction] = []
        self._observers: list[Notifier] = list(observers) if observers else []

    def attach_observer(self, observer: Notifier) -> None:
        """
        ลงทะเบียนผู้รับแจ้งเตือนใหม่ (Attach Observer)
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer: Notifier) -> None:
        """
        ยกเลิกการลงทะเบียนผู้รับแจ้งเตือน (Detach Observer)
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_low_stock(self, product: Product) -> None:
        """
        แจ้งเตือนไปยังทุก Observer ที่ลงทะเบียนไว้เมื่อสินค้ามีสต็อกต่ำกว่า threshold
        """
        message = f"สต็อกคงเหลือ {product.quantity} ชิ้น ซึ่งต่ำกว่าเกณฑ์ขั้นต่ำ ({product.threshold} ชิ้น)"
        for observer in self._observers:
            observer.send(message=message, product=product)

    def add_product(self, product: Product) -> None:
        """
        เพิ่มสินค้าใหม่เข้าสู่ระบบ
        """
        if product.code in self._products:
            raise ValueError(f"รหัสสินค้าซ้ำ: {product.code}")
        self._products[product.code] = product
        self._categories.add(product.category)

    def get_product(self, code: str) -> Product | None:
        """
        ดึงข้อมูลสินค้าตามรหัส
        """
        return self._products.get(code)

    def list_products(self) -> list[Product]:
        """
        คืนรายการสินค้าทั้งหมด
        """
        return list(self._products.values())

    def receive(self, code: str, amount: int) -> int:
        """
        US-01: บันทึกการรับสินค้าเข้าสต็อก
        :param code: รหัสสินค้า
        :param amount: จำนวนที่รับเข้า (ต้องมากกว่า 0)
        :return: ยอดคงเหลือใหม่
        """
        if amount <= 0:
            raise ValueError("จำนวนรับเข้าต้องมากกว่า 0")

        product = self._products.get(code)
        if not product:
            raise KeyError(f"ไม่พบสินค้าที่มีรหัส: {code}")

        product.quantity += amount

        # บันทึก Transaction
        self._transactions.append(
            StockTransaction(
                transaction_id=str(uuid.uuid4()),
                product_code=code,
                action="RECEIVE",
                amount=amount
            )
        )
        return product.quantity

    def issue(self, code: str, amount: int) -> int:
        """
        US-01 & US-02: บันทึกการจ่ายสินค้าออกจากสต็อก พร้อมแจ้งเตือนเมื่อสต็อกต่ำ
        :param code: รหัสสินค้า
        :param amount: จำนวนที่จ่ายออก (ต้องมากกว่า 0 และไม่เกินยอดคงเหลือ)
        :return: ยอดคงเหลือใหม่
        """
        if amount <= 0:
            raise ValueError("จำนวนจ่ายออกต้องมากกว่า 0")

        product = self._products.get(code)
        if not product:
            raise KeyError(f"ไม่พบสินค้าที่มีรหัส: {code}")

        if product.quantity < amount:
            raise ValueError(f"จำนวนสินค้าไม่เพียงพอ (คงเหลือ {product.quantity}, ต้องการจ่าย {amount})")

        product.quantity -= amount

        # บันทึก Transaction
        self._transactions.append(
            StockTransaction(
                transaction_id=str(uuid.uuid4()),
                product_code=code,
                action="ISSUE",
                amount=amount
            )
        )

        # US-02: ตรวจสอบและแจ้งเตือนถ้าสต็อกต่ำกว่า threshold (< threshold)
        if product.is_low_stock():
            self._notify_low_stock(product)

        return product.quantity

    def set_threshold(self, code: str, new_threshold: int) -> None:
        """
        US-04: ตั้งค่า threshold เตือนสต็อกต่ำแยกตามสินค้า
        """
        if new_threshold < 0:
            raise ValueError("เกณฑ์สต็อกต่ำ (threshold) ต้องไม่ติดลบ")

        product = self._products.get(code)
        if not product:
            raise KeyError(f"ไม่พบสินค้าที่มีรหัส: {code}")

        product.threshold = new_threshold

    def get_category_valuation(self) -> dict[str, float]:
        """
        US-03: สรุปรายงานมูลค่าสต็อกรวมแยกตามแต่ละหมวดหมู่
        :return: Dictionary ที่มี key เป็นชื่อหมวดหมู่ และ value เป็นมูลค่ารวม (บาท)
        """
        valuation_by_category: dict[str, float] = {cat: 0.0 for cat in self._categories}

        for product in self._products.values():
            cat = product.category
            if cat not in valuation_by_category:
                valuation_by_category[cat] = 0.0
            valuation_by_category[cat] += product.calculate_valuation()

        return valuation_by_category
