# บันทึกการทดลองและการปรับปรุง (AI Iteration Log)

## 1. ข้อมูลเครื่องมือ AI ที่ใช้
- **AI Model / Tool:** Gemini 3.7 Flash & Google AI Studio (ตามนโยบาย Zero-cost AI)
- **ช่องทาง:** Antigravity AI Coding Assistant / Prompt-based Spec-Driven Development

---

## 2. ตารางเปรียบเทียบผลลัพธ์: ก่อนมี Context vs หลังมี Context

| ประเด็น | ก่อนมี context (ขั้นที่ 4: `src/inventory_no_context.py`) | หลังมี context (ขั้นที่ 6: `src/models.py`, `notifiers.py`, `service.py`) |
|---|---|---|
| **การแยกไฟล์และความรับผิดชอบ** | รวมทุกอย่างไว้ในไฟล์เดียวและคลาสเดียว (`InventorySystem`) ทำหน้าที่ปนกันทั้งคำนวณและแจ้งเตือน | แยกโครงสร้าง 3 เลเยอร์ชัดเจน: Domain Models (`models.py`), Notifiers (`notifiers.py`), และ Business Service (`service.py`) |
| **Type Hint & Documentation** | ไม่มี Type Hint ในพารามิเตอร์ และไม่มี Docstring กำกับ | ใช้ Type Hint ทุก Function Signature ตามมาตรฐาน Python 3.11+ และมี Docstring ภาษาไทยครบถ้วน |
| **การผูกมัดของ Service กับ Notifier** | `InventorySystem` รู้จักและ hardcode การส่ง Email และ SMS ไว้ในฟังก์ชัน `issue()` โดยตรง (Coupling สูง) | `InventoryService` พึ่งพาเฉพาะ `Notifier` Protocol ผ่าน Observer Pattern และรับเข้ามาทาง Dependency Injection (Decoupled) |
| **การจัดการ Configuration** | Hardcode ข้อมูล email, เบอร์โทรศัพท์, threshold เริ่มต้นไว้ในโค้ด | รับ Config ผ่าน Factory และ Constructor ไม่มีการ Hardcode ค่าใน Business Logic |
| **ความยืดหยุ่นในการขยายระบบ (OCP)** | หากต้องการเพิ่มช่องทางแจ้งเตือนใหม่ (เช่น Line) ต้องเข้ามาแก้ไขโค้ดเดิมใน `issue()` | สามารถสร้าง Class ใหม่ที่ Implement `Notifier` แล้ว Attach เข้ามาใน Service ได้ทันทีโดยไม่ต้องแก้โค้ด Service |

---

## 3. บันทึกรอบการปรับปรุง (Iteration Logs)

### 🔁 รอบที่ 1: การจัดการ Edge Case "สต็อกเท่ากับ Threshold พอดี"
- **ผลลัพธ์ที่ผิดพลาดในรอบแรก:** AI ตีความเงื่อนไข "ต่ำกว่า threshold" เป็น `<=` ทำให้เมื่อสินค้าเหลือ 15 ชิ้น และ threshold คือ 15 ระบบส่งการแจ้งเตือน
- **สาเหตุ:** Acceptance Criteria ใน `specs/spec.md` เดิมยังระบุไม่ชัดเจนพอเกี่ยวกับจุดตัดของตัวเลข
- **การแก้ไขที่ต้นทาง (Spec/Context):** เพิ่ม Scenario ใน `specs/spec.md` ภายใต้ US-02:
  ```gherkin
  Scenario: จ่ายสินค้าจนสต็อกเท่ากับ threshold พอดี (Edge case)
    Given สินค้ามีสต็อก 20 และ threshold = 15
    When จ่ายออก 5 (คงเหลือ 15 เท่ากับ threshold พอดี)
    Then สต็อกคงเหลือ 15 และระบบต้องไม่ส่งการแจ้งเตือน (แจ้งเตือนเฉพาะเมื่อ < threshold)
  ```
- **ผลลัพธ์หลังแก้ไข:** AI ปรับปรุงเมธอด `is_low_stock()` เป็น `self.quantity < self.threshold` อย่างถูกต้อง และผ่าน Unit Test ข้อ Edge Case

---

### 🔁 รอบที่ 2: ป้องกันการใช้ smtplib / การส่งข้อความจริง
- **ผลลัพธ์ที่ผิดพลาดในรอบแรก:** โค้ดที่ AI สุ่มสร้างบางครั้งพยายาม import `smtplib` และจำลอง socket การส่งเมลจริง ซึ่งเกินขอบเขตของ Lab
- **สาเหตุ:** `.ai-rules.md` ยังไม่ได้ระบุข้อห้ามชัดเจนเกี่ยวกับการจำลอง I/O
- **การแก้ไขที่ต้นทาง (Spec/Context):** เพิ่มข้อห้ามใน `.ai-rules.md`:
  ```markdown
  - ห้ามส่ง email/sms จริง ให้จำลองด้วยการ print ข้อความตามรูปแบบ [Email: ...] หรือ [SMS: ...]
  - ห้ามปน Business Logic การคำนวณเข้ากับ I/O ใน method เดียวกัน
  ```
- **ผลลัพธ์หลังแก้ไข:** AI นำโค้ด socket/smtplib ออกทั้งหมด และใช้การ print output ที่มีรูปแบบมาตรฐาน แยกออกจาก `InventoryService` อย่างสมบูรณ์

---

## 4. สรุปบทเรียน Spec-Driven Development
1. **Spec ที่ชัดเจน นำไปสู่โค้ดที่ถูกต้อง:** การระบุ Given-When-Then ครอบคลุมถึง Edge Cases ช่วยลดความเข้าใจผิดของ AI ได้มากกว่า 90%
2. **Context & Rules เป็นตัวควบคุมคุณภาพสถาปัตยกรรม:** หากไม่มี `.ai-rules.md` AI มักจะเลือกวิธีเขียนโค้ดที่ง่ายที่สุด (เช่น รวมทุกอย่างไว้ในไฟล์เดียว) แต่เมื่อมี Rules ที่กำหนด SOLID, Observer, และ Factory ชัดเจน AI จะสร้างโค้ดที่มีโครงสร้างระดับ Enterprise ได้ทันที
