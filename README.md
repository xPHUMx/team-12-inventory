# team-12-inventory (ระบบสต็อกร้านเขียนดี)

ระบบจัดการสต็อกสินค้าสำหรับร้านเครื่องเขียนแบบ Command-Line Interface (CLI) พัฒนาตามใบงาน Lab 2 (Software Engineering in AI Era)

## 📋 ฟีเจอร์ที่รองรับ (User Stories & Acceptance Criteria)
- **US-01 (Must Have):** แสดงรายการสินค้าทั้งหมด (`list`)
  - แสดงชื่อ รหัส และจำนวนคงเหลือครบทุกรายการ
  - แจ้งเตือนเมื่อยังไม่มีสินค้าในระบบ
- **US-02 (Must Have):** เพิ่มสินค้าใหม่เข้าระบบ (`add`)
  - บันทึกรหัส ชื่อ และจำนวนเริ่มต้น (>= 0)
  - ป้องกันการเพิ่มรหัสสินค้าซ้ำ
- **US-03 (Must Have):** แก้ไข/ปรับปรุงจำนวนสินค้า (`adjust`)
  - ปรับยอดรับเข้า (บวก) หรือจ่ายออก (ลบ) ได้ทันที
  - ป้องกันไม่ให้ยอดคงเหลือติดลบ
- **US-04 (Should Have):** ค้นหาสินค้า (`search`)
  - ค้นหาด้วยรหัสสินค้าหรือชื่อสินค้าบางส่วน
- **US-05 (Could Have):** ส่งออกรายงานสต็อกเป็นไฟล์ CSV (`export`)
  - ส่งออกข้อมูลเป็นไฟล์ CSV พร้อมหัวคอลัมน์ (รหัส, ชื่อ, จำนวนคงเหลือ)

---

## 🚀 วิธีการติดตั้งและใช้งาน

### ข้อกำหนดเบื้องต้น
- Python 3.8 ขึ้นไป

### คำสั่งการใช้งาน CLI
```bash
# แสดงรายการสินค้าทั้งหมด
python inventory.py list

# เพิ่มสินค้าใหม่ (รหัส ชื่อ จำนวนเริ่มต้น)
python inventory.py add ITEM01 "สมุดโน้ต A5" 50

# ปรับจำนวนสินค้า (รับเข้า +20 หรือ จ่ายออก -10)
python inventory.py adjust ITEM01 20
python inventory.py adjust ITEM01 -10

# ค้นหาสินค้าด้วยรหัสหรือชื่อ
python inventory.py search สมุด
python inventory.py search ITEM01

# ส่งออกรายงานสต็อกเป็นไฟล์ CSV
python inventory.py export stock_report.csv
```

### การทดสอบ Unit Test
```bash
# ทดสอบฟังก์ชันของ Lab 2
py -m unittest test_inventory.py

# ทดสอบฟังก์ชันของ Lab 3 (Spec-Driven Development & SOLID & Observer Pattern)
py -m unittest test_service.py

# ทดสอบ Unit Test ทั้งหมดในโปรเจกต์
py -m unittest discover -v
```

---

## 🏛️ Lab 3: Spec-Driven Development (SDD) & Context Engineering

### โครงสร้างไฟล์ของ Lab 3:
- **`specs/spec.md`**: เอกสารข้อกำหนด (User Stories, Acceptance Criteria แบบ Given-When-Then, FR, NFR)
- **`.ai-rules.md`**: ไฟล์ Context / Rules สำหรับ AI ควบคุมคุณภาพสถาปัตยกรรม (SOLID, Type Hints, Observer, Factory)
- **`src/models.py`**: Domain Entities (`Product`, `Category`, `StockTransaction`)
- **`src/notifiers.py`**: Notifier Protocol, `EmailNotifier`, `SMSNotifier`, และ `NotifierFactory`
- **`src/service.py`**: `InventoryService` (Subject ใน Observer Pattern จัดการ Business Logic รับ/จ่าย และคำนวณ Valuation)
- **`src/inventory_no_context.py`**: โค้ดตัวอย่างก่อนมี Context เพื่อเปรียบเทียบสถาปัตยกรรม
- **`AI_ITERATION_LOG.md`**: บันทึกการเปรียบเทียบและรอบการ Iterate ปรับปรุง Spec/Context
- **`diagrams/`**: Mermaid Class Diagram (`class.md`) และ Sequence Diagram (`sequence.md`)
- **`design_review.md`**: ตารางประเมิน SOLID Design Review 5 ข้อ
