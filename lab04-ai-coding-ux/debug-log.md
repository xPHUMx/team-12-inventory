# Evidence-Based Debugging Log - Lab 04

บันทึกการไล่หาและแก้ไข Bug ในโมดูล `discount.py` อย่างเป็นระบบตามระเบียบวิธี 5 ขั้นตอน (Reproduce -> Traceback -> Hypothesis -> Verify -> Fix)

---

## จุดที่ 1: Test ที่ไม่ผ่าน: `test_apply_discount_basic` (และส่งผลต่อ `test_bulk_total`)

### 1. Reproduce
- **คำสั่งที่รัน:** `python -m pytest tests/test_discount.py -k "test_apply_discount_basic or test_bulk_total" -v`
- **Assertion ที่ Fail:**
  ```text
  assert apply_discount(100.0, 10) == 90.0
  E assert 99.9 == 90.0
  E  + where 99.9 = apply_discount(100.0, 10)
  ```

### 2. Traceback
- **ไฟล์และบรรทัดที่เกิดปัญหา:** `discount.py` บรรทัดที่ 5 ในฟังก์ชัน `apply_discount`
  ```python
  def apply_discount(price: float, percent: float) -> float:
      return price - percent / 100  # <--- บรรทัดที่คำนวณผิด
  ```

### 3. สมมติฐาน (Hypothesis)
- สูตรคำนวณการคิดส่วนลดผิดพลาด โดยนำราคาตั้งต้นไปลบด้วยสัดส่วนทศนิยมของเปอร์เซ็นต์โดยตรง (`10 / 100 = 0.1` กลายเป็น `100.0 - 0.1 = 99.9`) แทนที่จะนำเปอร์เซ็นต์ไปคูณกับราคาตั้งต้นก่อนแล้วจึงนำมาหักลบ (`100.0 * 10 / 100 = 10.0` เพื่อให้เหลือ `90.0`)

### 4. การยืนยัน (Verification)
- ทดสอบพิมพ์ค่าออกมาดู:
  ```python
  price = 100.0
  percent = 10.0
  print("Current:", price - percent / 100)           # แสดงผล: 99.9
  print("Expected:", price * (1.0 - percent / 100))  # แสดงผล: 90.0
  ```
- ยืนยันได้ชัดเจนว่าสูตรเดิมขาดการคูณด้วย `price`

### 5. Root Cause และการแก้ (Fix)
- **Root Cause:** ผู้เขียนโค้ดเขียนสมการตกหล่น ลืมคูณฐานราคา (`price`) เข้ากับอัตราส่วนลด ทำให้การลด 10% กลายเป็นการลดเงินแค่ 0.10 บาทในทุกกรณี (และกับดักคือ `test_apply_discount_zero` ผ่านเพราะ `250.0 - 0/100 = 250.0` พอดี)
- **การแก้ไข:** แก้สมการใน `discount.py` บรรทัดที่ 5 เป็น:
  ```python
  def apply_discount(price: float, percent: float) -> float:
      """ลดราคาตาม percent (0-100) คืนราคาหลังลด"""
      return price * (1.0 - percent / 100.0)
  ```
- **ผลหลัง Re-run:** ทั้ง `test_apply_discount_basic` และ `test_bulk_total` ผ่าน (PASSED) ทันที

---

## จุดที่ 2: Test ที่ไม่ผ่าน: `test_average_price_empty`

### 1. Reproduce
- **คำสั่งที่รัน:** `python -m pytest tests/test_discount.py -k test_average_price_empty -v`
- **Assertion / Exception ที่ Fail:**
  ```text
  assert average_price([]) == 0.0
  ZeroDivisionError: division by zero
  ```

### 2. Traceback
- **ไฟล์และบรรทัดที่เกิดปัญหา:** `discount.py` บรรทัดที่ 18 ในฟังก์ชัน `average_price`
  ```python
  def average_price(prices: list) -> float:
      return sum(prices) / len(prices)  # <--- len([]) มีค่าเป็น 0 เกิด ZeroDivisionError
  ```

### 3. สมมติฐาน (Hypothesis)
- ฟังก์ชันไม่ได้ตรวจสอบกรณีขอบเขต (Boundary / Edge Case) เมื่อลิสต์ `prices` ว่างเปล่า (`len(prices) == 0`) ตัวหารจึงเป็นศูนย์ ส่งผลให้เกิด Exception `ZeroDivisionError` แทนที่จะคืนค่า `0.0` ตามที่โจทย์และ Test คาดหวัง

### 4. การยืนยัน (Verification)
- ทดสอบทดลองรัน:
  ```python
  prices = []
  print("Length:", len(prices))  # แสดงผล: 0
  # บรรทัด sum(prices) / len(prices) โยน ZeroDivisionError
  ```
- ยืนยันได้ว่าจำเป็นต้องมี Guard Clause ตรวจสอบ `if not prices:` ก่อนทำการหาร

### 5. Root Cause และการแก้ (Fix)
- **Root Cause:** ขาด Guard Clause ป้องกันการหารด้วยศูนย์เมื่อคลังสินค้าว่างหรือไม่มีรายการราคา
- **การแก้ไข:** เพิ่มการตรวจสอบ `if not prices:` คืนค่า `0.0` ก่อนทำการหาร:
  ```python
  def average_price(prices: list) -> float:
      """คืนราคาเฉลี่ยของรายการสินค้า"""
      if not prices:
          return 0.0
      return sum(prices) / len(prices)
  ```
- **ผลหลัง Re-run:** `test_average_price_empty` ผ่าน (PASSED)

---

## จุดที่ 3: Test ที่ไม่ผ่าน: `test_cheapest_n`

### 1. Reproduce
- **คำสั่งที่รัน:** `python -m pytest tests/test_discount.py -k test_cheapest_n -v`
- **Assertion ที่ Fail:**
  ```text
  assert cheapest_n([50.0, 10.0, 30.0, 20.0], 2) == [10.0, 20.0]
  E assert [20.0] == [10.0, 20.0]
  E   At index 0 diff: 20.0 != 10.0
  E   Right contains one more item: 20.0
  ```

### 2. Traceback
- **ไฟล์และบรรทัดที่เกิดปัญหา:** `discount.py` บรรทัดที่ 24 ในฟังก์ชัน `cheapest_n`
  ```python
  def cheapest_n(prices: list, n: int) -> list:
      ordered = sorted(prices)
      return ordered[1:n]  # <--- เริ่ม Slice ที่ดัชนี 1 แทนที่จะเป็น 0
  ```

### 3. สมมติฐาน (Hypothesis)
- มีข้อผิดพลาดแบบ Off-by-one Error จากการระบุ Index เริ่มต้นของ Slice เป็น `1:n` ซึ่งการระบุเลข 1 ทำให้ตัดข้อมูลตัวแรกสุด (Index 0 ซึ่งเป็นสินค้าที่ราคาถูกที่สุด) ทิ้งไป และการตัดช่วง `1:2` จะได้สมาชิกเพียง 1 ตัวคือตัวที่สอง (ได้ `[20.0]` แทนที่จะได้ 2 ตัวแรก `[10.0, 20.0]`)

### 4. การยืนยัน (Verification)
- ทดสอบพิมพ์ค่าออกมาดู:
  ```python
  ordered = sorted([50.0, 10.0, 30.0, 20.0])  # [10.0, 20.0, 30.0, 50.0]
  print("Slice [1:2]:", ordered[1:2])        # แสดงผล: [20.0]  (หลุดตัว 10.0 ไป)
  print("Slice [:2] :", ordered[:2])         # แสดงผล: [10.0, 20.0] (ถูกต้อง)
  ```
- ยืนยันได้ชัดเจนว่า Slice ผิดช่วง ต้องเริ่มจาก Index 0

### 5. Root Cause และการแก้ (Fix)
- **Root Cause:** ผู้เขียนโค้ดเข้าใจผิดเรื่อง Zero-based Indexing ใน Python หรือพิมพ์เลข 1 เกินมา ทำให้ไม่รวมตัวแรกในลิสต์ และหาก `n <= 0` ควรคืนลิสต์ว่าง
- **การแก้ไข:** แก้ไขการ Slice เป็น `ordered[:n]` พร้อมทั้งดักกรณี `n <= 0`:
  ```python
  def cheapest_n(prices: list, n: int) -> list:
      """คืน n รายการที่ราคาถูกที่สุด เรียงจากถูกไปแพง"""
      if n <= 0:
          return []
      ordered = sorted(prices)
      return ordered[:n]
  ```
- **ผลหลัง Re-run:** `test_cheapest_n` ผ่าน (PASSED)

---

## 4. ผลสรุปการทดสอบรวมทั้งหมดหลังแก้ครบทุกจุด

```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
collected 6 items

tests/test_discount.py::test_apply_discount_basic PASSED                 [ 16%]
tests/test_discount.py::test_apply_discount_zero PASSED                  [ 33%]
tests/test_discount.py::test_bulk_total PASSED                           [ 50%]
tests/test_discount.py::test_average_price PASSED                        [ 66%]
tests/test_discount.py::test_average_price_empty PASSED                  [ 83%]
tests/test_discount.py::test_cheapest_n PASSED                           [100%]

============================== 6 passed in 0.07s ==============================
```
- ทุกฟังก์ชันผ่านการทดสอบ 100% ครบทั้ง 6 ข้อ
- ไม่มีการ Crash หรือ ZeroDivisionError
