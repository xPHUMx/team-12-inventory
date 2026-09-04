# Sequence Diagram: จ่ายสินค้าและแจ้งเตือนเมื่อสต็อกต่ำ (Lab 3)

Diagram นี้แสดง Flow การทำงานตั้งแต่พนักงานเรียกจ่ายสินค้าผ่าน `InventoryService.issue()` จนถึงการตรวจสอบเงื่อนไขสต็อกต่ำ และการกระจายแจ้งเตือนไปยัง Observers ทุกตัว

```mermaid
sequenceDiagram
    autonumber
    actor Staff as พนักงานคลังสินค้า
    participant Service as InventoryService
    participant Product as Product (WIRE01)
    participant Transaction as StockTransaction
    participant Email as EmailNotifier (Observer 1)
    participant SMS as SMSNotifier (Observer 2)

    Staff->>Service: issue("WIRE01", 8)
    activate Service

    Service->>Product: ตรวจสอบจำนวนคงเหลือ (quantity >= 8)
    Product-->>Service: เพียงพอ (มี 20 ชิ้น)

    Service->>Product: ลดจำนวนสต็อก (quantity -= 8)
    Note over Product: คงเหลือ 12 ชิ้น

    Service->>Transaction: บันทึกรายการจ่ายออก (ISSUE, 8)
    activate Transaction
    Transaction-->>Service: บันทึกสำเร็จ
    deactivate Transaction

    Service->>Product: is_low_stock()
    activate Product
    Note over Product: 12 < 15 (Threshold) -> True
    Product-->>Service: True
    deactivate Product

    rect rgb(240, 248, 255)
        note over Service,SMS: Observer Pattern: กระจายการแจ้งเตือน
        Service->>Service: _notify_low_stock(Product)
        Service->>Email: send("สต็อกคงเหลือ 12 ชิ้น...", Product)
        activate Email
        Email-->>Staff: [Email: admin@...] แสดงข้อความแจ้งเตือน
        deactivate Email

        Service->>SMS: send("สต็อกคงเหลือ 12 ชิ้น...", Product)
        activate SMS
        SMS-->>Staff: [SMS: 089-...] แสดงข้อความแจ้งเตือน
        deactivate SMS
    end

    Service-->>Staff: คืนค่ายอดคงเหลือใหม่ (12 ชิ้น)
    deactivate Service
```
