# การประเมินหลักการออกแบบ (SOLID Design Review)

เอกสารนี้จัดทำขึ้นเพื่อวิเคราะห์และตรวจสอบการปฏิบัติตามหลักการออกแบบ SOLID ของระบบคลังสินค้า (Lab 3)

---

## ตารางประเมินหลักการ SOLID 5 ข้อ

| หลัก SOLID | ละเมิดหรือไม่ (ในดีไซน์เริ่มต้น vs ดีไซน์ปัจจุบัน) | จุดที่เกี่ยวข้อง (Class / Method) | อธิบายและผลกระทบ | ข้อเสนอแนะและการปรับปรุงที่นำมาใช้ |
|---|---|---|---|---|
| **S (Single Responsibility Principle)** | • เริ่มต้น: **ละเมิด**<br>• ปัจจุบัน: **ผ่าน** | `InventorySystem` (เดิม) vs `InventoryService`, `Product`, `EmailNotifier` | เดิม `InventorySystem` ทำหน้าที่หลายอย่างพร้อมกัน ทั้งคำนวณสต็อก, จัดการ I/O print, คำนวณมูลค่า และส่งการแจ้งเตือน หากมีการเปลี่ยนรูปแบบแจ้งเตือนจะกระทบ Business Logic | แยกหน้าที่ออกเป็นคลาสเฉพาะ:<br>• `Product`: จัดการ State และ Valuation ของสินค้า<br>• `InventoryService`: ดูแล Workflow และ Business Logic รับ-จ่าย<br>• `EmailNotifier` / `SMSNotifier`: ดูแลการส่งข้อความแจ้งเตือน |
| **O (Open-Closed Principle)** | • เริ่มต้น: **ละเมิด**<br>• ปัจจุบัน: **ผ่าน** | `InventoryService._notify_low_stock` และ `Notifier` Protocol | เดิมหากต้องการเพิ่มช่องทางแจ้งเตือนใหม่ (เช่น Line หรือ Telegram) ต้องเปิดไฟล์ Service เพื่อแก้คำสั่ง `print` หรือเพิ่ม `elif channel == 'line'` | ใช้ **Observer Pattern** และ `Notifier` Protocol ทำให้ `InventoryService` เปิดกว้างต่อการขยาย (Open for Extension) โดยการ Attach Observer ใหม่ แต่ปิดต่อการแก้ไขโค้ดเดิม (Closed for Modification) |
| **L (Liskov Substitution Principle)** | • เริ่มต้น: **ไม่พบ**<br>• ปัจจุบัน: **ผ่าน** | `Notifier` Protocol, `EmailNotifier`, `SMSNotifier` | อ็อบเจกต์ของคลาสแจ้งเตือนทุกตัว (`EmailNotifier`, `SMSNotifier`) มี Signature ของเมธอด `send(message, product)` ตรงตาม Protocol และสามารถใช้แทนที่กันได้อย่างสมบูรณ์โดยไม่ทำให้การทำงานของ `InventoryService` ผิดพลาด | ออกแบบ Notifier ทุกตัวให้รับและคืนค่าชนิดเดียวกัน ไม่โยน Exception ที่ไม่คาดคิด และทำงานสอดคล้องกับพฤติกรรมของ Protocol หลัก |
| **I (Interface Segregation Principle)** | • เริ่มต้น: **ไม่พบ**<br>• ปัจจุบัน: **ผ่าน** | `Notifier` Protocol | `Notifier` Protocol มีเฉพาะเมธอด `send()` ที่จำเป็นสำหรับการรับแจ้งเตือนเท่านั้น ไม่บังคับให้ Client ต้อง Implement เมธอดที่ไม่จำเป็น เช่น การเชื่อมต่อ Network หรือการยืนยันตัวตน | แยก Interface ให้มีขนาดเล็กและเฉพาะเจาะจง (Cohesive Interface) เหมาะสำหรับการเป็น Observer |
| **D (Dependency Inversion Principle)** | • เริ่มต้น: **ละเมิด**<br>• ปัจจุบัน: **ผ่าน** | `InventoryService.__init__` และ `NotifierFactory` | เดิม `InventorySystem` พึ่งพาช่องทาง Email/SMS โดยตรง (High-level module พึ่งพา Low-level module) | ให้ `InventoryService` พึ่งพา Abstraction (`Notifier` Protocol) และรับ Observers ผ่าน Constructor (Dependency Injection) โดยใช้ `NotifierFactory` เป็นตัวจัดการสร้าง Concrete Instances |

---

## สรุปผลการตรวจทาน
- สถาปัตยกรรมปัจจุบันหลังการ Refactor ด้วย **Observer Pattern + Factory Pattern + Dependency Injection** สอดคล้องกับหลักการ SOLID ครบทั้ง 5 ข้อ
- โค้ดมีความเป็น Modular สูง ง่ายต่อการทดสอบด้วย Unit Test (Testability) และง่ายต่อการบำรุงรักษาในระยะยาว (Maintainability)
