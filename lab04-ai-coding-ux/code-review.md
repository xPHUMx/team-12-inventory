# Code Review: Pull Request - `inventory_service.py`

เอกสารการตรวจสอบโค้ด (Code Review) ฉบับละเอียดสำหรับไฟล์ `inventory_service.py` ซึ่งเป็น Pull Request ที่สร้างโดย AI โดยวิเคราะห์ตามหลัก 4 มิติ (ความถูกต้องตาม Docstring, State Consistency/Error Recovery, Concurrency/Thread-safety, และ Boundary/Zero-division)

---

## 1. รายละเอียดการรีวิวรายเมธอด (Review Comments)

### จุดที่ 1: ขาด Atomicity และเสี่ยงต่อ State ตกค้างใน `sell_batch`
- **ชื่อเมธอดและบรรทัด:** เมธอด `sell_batch` (บรรทัดที่ 16-22)
- **ทำไมถึงผิด:** ไม่มีความเป็น Atomic (All-or-Nothing Transaction) ในการขายแบบกลุ่ม หากการขายสินค้าตัวแรกสำเร็จ แต่สินค้าตัวถัดมาสต็อกไม่พอ จะเกิด `ValueError` หลุดออกไปทันที โดยที่สินค้าตัวแรกถูกตัดสต็อกไปแล้วและไม่มีกลไก Rollback คืนสต็อก ทำให้เกิด Partial Failure และข้อมูลสต็อกในคลังไม่ตรงกับยอดขายจริง
- **กรณีที่จะพัง (Test Case ตัวอย่าง):**
  - มีสินค้าในคลัง: `"ปากกา"` (มี 5 ด้าม), `"สมุด"` (มี 2 เล่ม)
  - มีคำสั่งซื้อเข้ามา: `orders = {"ปากกา": 3, "สมุด": 5}`
  - **ผลลัพธ์:** ปากกาถูกตัดยอดเหลือ 2 ด้าม แต่พอถึงสมุด ระบบพังด้วย `ValueError` เพราะของไม่พอ ทำให้ลูกค้าไม่ได้ของ แต่อีเมลหรือสต็อกปากกาหายไป 3 ด้ามเรียบร้อยแล้ว
- **ข้อเสนอแนะในการแก้ไข:**
  - ทำการตรวจสอบความพร้อมของสินค้าทุกรายการก่อนเริ่มตัดสต็อก (Two-phase validation) หรือเก็บประวัติรายการที่ตัดแล้วเพื่อ Rollback คืนหากมีรายการใดรายการหนึ่งล้มเหลว
  ```python
  def sell_batch(self, orders: dict[str, int]) -> dict[str, int]:
      # Phase 1: ตรวจสอบว่าสินค้าทุกรายการมีพอหรือไม่
      for name, amount in orders.items():
          if name not in self._inv._items:
              raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
          if self._inv._items[name].quantity < amount:
              raise ValueError(f"สินค้า '{name}' มีไม่พอสำหรับการขายทั้งชุด")
      
      # Phase 2: ตัดสต็อกจริงเมื่อทุกรายการพร้อม
      result = {}
      for name, amount in orders.items():
          result[name] = self._inv.sell(name, amount)
      return result
  ```

---

### จุดที่ 2: เกิด KeyError เมื่อของไม่พอจอง และไม่ดักจับสินค้าที่ไม่มีอยู่จริงใน `reserve`
- **ชื่อเมธอดและบรรทัด:** เมธอด `reserve` (บรรทัดที่ 25-32)
- **ทำไมถึงผิด:**
  1. เข้าถึง `self._inv._items[name]` โดยตรงที่บรรทัด 27 หากไม่มีสินค้านี้ในระบบจะเกิด `KeyError` ทันที
  2. ที่บรรทัด 29 หาก `amount` มากกว่าสต็อกที่เหลือให้จอง บล็อก `if` จะไม่ทำงาน ทำให้ `self._reserved[name]` ยังไม่ถูกสร้างขึ้น แต่ในบรรทัด 31 มีการเรียก `self._reserved[name]` ทันที ส่งผลให้เกิด `KeyError` ในเคสที่ของไม่พอจอง!
- **กรณีที่จะพัง (Test Case ตัวอย่าง):**
  - มีสินค้า `"โต๊ะ"` ในคลัง 5 ตัว, ยังไม่เคยมีการจองมาก่อน (`_reserved` ว่างเปล่า)
  - ลูกค้าขอจอง 10 ตัว: `reserve("โต๊ะ", 10)`
  - เงื่อนไข `10 <= 5 - 0` เป็น False (ไม่เข้า if บรรทัด 30)
  - บรรทัด 31 รัน `return item.quantity - self._reserved["โต๊ะ"]` เกิด `KeyError: 'โต๊ะ'` ระบบ Crash ทันที
- **ข้อเสนอแนะในการแก้ไข:**
  ```python
  def reserve(self, name: str, amount: int) -> int:
      if name not in self._inv._items:
          raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
      if amount <= 0:
          raise ValueError("จำนวนที่จองต้องมากกว่าศูนย์")
          
      item = self._inv._items[name]
      already = self._reserved.get(name, 0)
      available = item.quantity - already
      
      if amount > available:
          raise ValueError(f"สินค้า '{name}' เหลือให้จองเพียง {available} ชิ้น")
          
      self._reserved[name] = already + amount
      return item.quantity - self._reserved[name]
  ```

---

### จุดที่ 3: เงื่อนไขช่วงราคาไม่ครอบคลุมจุดขอบ (Boundary Condition) ใน `items_in_price_range`
- **ชื่อเมธอดและบรรทัด:** เมธอด `items_in_price_range` (บรรทัดที่ 34-40)
- **ทำไมถึงผิด:** Docstring ระบุชัดเจนว่า *"อยู่ในช่วง [low, high]"* ซึ่งเครื่องหมายก้ามปูทางคณิตศาสตร์หมายถึงการนับรวมจุดขอบ (Inclusive) แต่โค้ดที่บรรทัด 38 ใช้ `low < item.price < high` (Exclusive) ทำให้สินค้าที่มีราคาเท่ากับ `low` หรือ `high` พอดีตกหล่นไป
- **กรณีที่จะพัง (Test Case ตัวอย่าง):**
  - สินค้า `"ปากกา"` ราคา 100.0 บาท, สินค้า `"สมุด"` ราคา 200.0 บาท
  - เรียกค้นหา: `items_in_price_range(100.0, 200.0)`
  - ผลลัพธ์ที่ได้: `[]` (ไม่พบสินค้าใดเลย ทั้งที่ทั้งสองชิ้นอยู่ในช่วง [100.0, 200.0])
- **ข้อเสนอแนะในการแก้ไข:** เปลี่ยนเครื่องหมายเปรียบเทียบเป็น `<=`:
  ```python
  if low <= item.price <= high:
      names.append(name)
  ```

---

### จุดที่ 4: ไม่นับสินค้าที่สต็อกแตะเกณฑ์พอดีใน `low_stock_report`
- **ชื่อเมธอดและบรรทัด:** เมธอด `low_stock_report` (บรรทัดที่ 43-49)
- **ทำไมถึงผิด:** Docstring ระบุว่า *"คืนรายชื่อสินค้าที่ stock ต่ำกว่าหรือเท่ากับเกณฑ์"* แต่เงื่อนไขในบรรทัด 47 เขียนเพียง `if item.quantity < self.LOW_STOCK_THRESHOLD:`
- **กรณีที่จะพัง (Test Case ตัวอย่าง):**
  - กำหนดเกณฑ์เตือน `LOW_STOCK_THRESHOLD = 5`
  - มีสินค้า `"หลอดไฟ"` เหลืออยู่ในคลัง 5 ชิ้นพอดี
  - ผลลัพธ์: รายงานไม่แสดงชื่อ `"หลอดไฟ"` ทำให้ผู้จัดการไม่ทราบว่าสต็อกถึงเกณฑ์วิกฤตแล้ว
- **ข้อเสนอแนะในการแก้ไข:** เปลี่ยนเป็น `item.quantity <= self.LOW_STOCK_THRESHOLD`

---

### จุดที่ 5: Race Condition จากการอ่านค่านอก Lock ใน `concurrent_restock`
- **ชื่อเมธอดและบรรทัด:** เมธอด `concurrent_restock` (บรรทัดที่ 52-57)
- **ทำไมถึงผิด:** เกิดข้อผิดพลาดด้าน Concurrency (TOCTOU: Time-of-check to time-of-use) บรรทัด 54 อ่านค่า `current = self._inv._items[name].quantity` **ก่อนที่จะเข้าบล็อก `with self._lock:`** หากมี 2 Thread เรียกพร้อมกัน ทั้งคู่จะได้ค่า `current` เดียวกัน แล้วเข้าไปบวกทับกัน ทำให้เกิดปัญหา Lost Update (ยอดที่เติมหายไป)
- **กรณีที่จะพัง (Test Case ตัวอย่าง):**
  - มีสินค้าในคลัง 10 ชิ้น
  - Thread 1 เติม 5 ชิ้น, Thread 2 เติม 5 ชิ้น
  - ทั้ง Thread 1 และ 2 อ่าน `current = 10`
  - Thread 1 เข้า Lock บันทึกยอด `10 + 5 = 15`
  - Thread 2 เข้า Lock บันทึกยอด `10 + 5 = 15` ทับค่าเดิม
  - **ผลลัพธ์:** สต็อกกลายเป็น 15 ชิ้น แทนที่จะเป็น 20 ชิ้น (ของหายไป 5 ชิ้นในระบบ)
- **ข้อเสนอแนะในการแก้ไข:** ย้ายคำสั่งการอ่านค่าและบวกเพิ่มเข้าไปใน Lock หรือเรียกใช้ `self._inv.restock`
  ```python
  def concurrent_restock(self, name: str, amount: int) -> int:
      with self._lock:
          return self._inv.restock(name, amount)
  ```

---

### จุดที่ 6: ZeroDivisionError และสูตรหารผิดความหมายใน `average_unit_value`
- **ชื่อเมธอดและบรรทัด:** เมธอด `average_unit_value` (บรรทัดที่ 60-64)
- **ทำไมถึงผิด:**
  1. หากคลังสินค้ายังว่างเปล่า (`len(self._inv._items) == 0`) จะเกิด `ZeroDivisionError` ทำให้ระบบพัง
  2. สูตรผิดความหมาย: Docstring ระบุว่า *"มูลค่าเฉลี่ยต่อชิ้นของสินค้าทั้งคลัง"* แต่นำ `total_value` ไปหารด้วยจำนวนชนิดสินค้า (`len(_items)`) ไม่ใช่จำนวนชิ้นสินค้าทั้งหมดในคลัง
- **กรณีที่จะพัง (Test Case ตัวอย่าง):**
  - **เคสที่ 1 (Crash):** คลังเปิดใหม่ไม่มีสินค้า เรียก `average_unit_value()` -> Crash ทันทีด้วย `ZeroDivisionError: division by zero`
  - **เคสที่ 2 (สูตรเพี้ยน):** มีสายไฟ 100 เมตร (เมตรละ 10 บาท = 1,000 บาท) และเครื่องตัดหญ้า 1 เครื่อง (ราคา 5,000 บาท). มูลค่ารวม = 6,000 บาท มีของ 101 ชิ้น มูลค่าเฉลี่ยต่อชิ้นที่แท้จริงคือ 6,000 / 101 = 59.40 บาท แต่โค้ดนี้คำนวณ 6,000 / 2 = 3,000 บาท!
- **ข้อเสนอแนะในการแก้ไข:**
  ```python
  def average_unit_value(self) -> float:
      total_pieces = sum(item.quantity for item in self._inv._items.values())
      if total_pieces == 0:
          return 0.0
      return self._inv.get_total_value() / total_pieces
  ```

---

## 2. ตารางสรุปการจัดหมวดหมู่และระดับความรุนแรงของ Bug ทั้งหมด

| # | เมธอด | หมวด (Category) | ระดับ (Severity) | สรุปปัญหา | กรณีที่ทำให้พัง |
|---|---|---|---|---|---|
| 1 | `sell_batch` | correctness | **high** | ขาด Atomicity เกิด Partial Failure ตัดของสำเร็จบางรายการแต่ทิ้ง error ค้างไว้ | สั่งซื้อ 2 รายการ ชิ้นแรกพอแต่ชิ้นสองไม่พอ ชิ้นแรกถูกตัดฟรีแต่ลูกค้าไม่ได้ของ |
| 2 | `reserve` | correctness | **high** | เกิด KeyError ทันทีเมื่อของไม่พอจอง เพราะพยายามอ่าน key ที่ยังไม่ถูกสร้าง | จองเกินจำนวนสต็อกที่มีอยู่จริง ระบบ Crash ด้วย `KeyError` |
| 3 | `items_in_price_range` | correctness | **medium** | ใช้เครื่องหมาย `<` แทน `<=` ไม่รวมราคาสินค้าที่อยู่ตรงจุดขอบพอดี | ค้นหาช่วง [100, 200] แล้วสินค้าที่มีราคา 100 หรือ 200 หายไปจากผลลัพธ์ |
| 4 | `low_stock_report` | correctness | **medium** | ไม่นับสินค้าที่สต็อกเท่ากับ threshold พอดี ทำให้เตือนช้ากว่าที่ระบุใน docstring | สินค้าเหลือเท่ากับเกณฑ์ 5 ชิ้นพอดี ไม่ถูกแจ้งเตือน |
| 5 | `concurrent_restock` | concurrency | **high** | อ่านค่านอก Thread Lock เกิด Race Condition ข้อมูลถูกเขียนทับ (Lost Update) | เติมของพร้อมกัน 2 เธรด ยอดของหายไปเพราะเขียนทับค่าเก่า |
| 6 | `average_unit_value` | correctness | **high** | เกิด ZeroDivisionError เมื่อคลังว่าง และหารด้วยจำนวนชนิดแทนที่จะเป็นจำนวนชิ้น | เรียกใช้งานขณะคลังสินค้ายังว่างเปล่า ทำให้โปรแกรม Crash ทันที |
