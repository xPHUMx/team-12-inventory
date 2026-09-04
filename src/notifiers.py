"""
โมดูล Notification สำหรับส่งการแจ้งเตือนตามหลัก SOLID (OCP, DIP) และ Factory Pattern
"""
from typing import Protocol, runtime_checkable
from src.models import Product


@runtime_checkable
class Notifier(Protocol):
    """
    Protocol (Interface) สำหรับผู้รับการแจ้งเตือน (Observer)
    """
    def send(self, message: str, product: Product) -> None:
        """
        ส่งข้อความแจ้งเตือน
        :param message: ข้อความแจ้งเตือน
        :param product: อ็อบเจกต์สินค้าที่เกี่ยวข้อง
        """
        ...


class EmailNotifier:
    """
    การแจ้งเตือนผ่านช่องทาง Email (จำลองการส่งด้วยการ print)
    """
    def __init__(self, recipient_email: str) -> None:
        self.recipient_email = recipient_email

    def send(self, message: str, product: Product) -> None:
        """ส่งการแจ้งเตือนทาง Email"""
        print(f"[Email: {self.recipient_email}] แจ้งเตือนสต็อกต่ำ: สินค้า {product.name} (รหัส {product.code}) เหลือ {product.quantity} ชิ้น (เกณฑ์เตือน: {product.threshold}) - {message}")


class SMSNotifier:
    """
    การแจ้งเตือนผ่านช่องทาง SMS (จำลองการส่งด้วยการ print)
    """
    def __init__(self, phone_number: str) -> None:
        self.phone_number = phone_number

    def send(self, message: str, product: Product) -> None:
        """ส่งการแจ้งเตือนทาง SMS"""
        print(f"[SMS: {self.phone_number}] ด่วน! สต็อกต่ำ: [{product.code}] {product.name} คงเหลือ {product.quantity} - {message}")


class NotifierFactory:
    """
    Factory Class สำหรับสร้าง Notifier ตาม Channel ที่ต้องการ
    """
    @staticmethod
    def create(channel: str, **kwargs) -> Notifier:
        """
        สร้างและคืนค่า Instance ของ Notifier ตามช่องทางที่ระบุ
        :param channel: ชื่อช่องทาง ("email", "sms")
        :param kwargs: ค่า config เช่น recipient_email, phone_number
        :return: อ็อบเจกต์ที่สอดคล้องกับ Notifier protocol
        """
        normalized_channel = channel.strip().lower()
        if normalized_channel == "email":
            email = kwargs.get("recipient_email", "manager@store.com")
            return EmailNotifier(recipient_email=email)
        elif normalized_channel == "sms":
            phone = kwargs.get("phone_number", "081-000-0000")
            return SMSNotifier(phone_number=phone)
        else:
            raise ValueError(f"ไม่รองรับช่องทางการแจ้งเตือน: {channel}")
