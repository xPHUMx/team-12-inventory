# Prompt Engineering vs Context Engineering - Lab 04

เอกสารเปรียบเทียบการสั่งงาน AI Coding Assistant ระหว่างการใช้ **Prompt สั้น ๆ (ไม่มี Context)** กับการใช้ **Prompt ที่แนบ Context ครบถ้วน (Context Engineering)** ในโจทย์เดียวกัน คือ *"การเขียนฟังก์ชันตัดจ่ายสต็อกสินค้า (Deduct/Sell Stock)"*

---

## 1. การทดลองรอบที่ 1: Prompt สั้น ๆ (No Context)

### Prompt ที่ใช้
```text
เขียน function ภาษา Python สำหรับลดสต็อกสินค้าในคลัง
```

### ผลลัพธ์โค้ดที่ AI สร้างให้
```python
def reduce_stock(inventory, item_id, qty):
    inventory[item_id] -= qty
    return inventory[item_id]
```

### การวิเคราะห์ผลลัพธ์รอบที่ 1
- **ปัญหาที่พบ:**
  1. ไม่สอดคล้องกับสถาปัตยกรรมของโปรเจกต์เดิม: โปรเจกต์เราใช้คลาส `Inventory` และ `InventoryItem` แต่ AI เดาว่าเป็น Dictionary ธรรมดา (`inventory[item_id]`)
  2. ไม่มี Data Validation: ไม่มีการตรวจสอบว่า `qty` เป็นค่าติดลบหรือไม่, ไม่ตรวจว่ามี `item_id` อยู่จริงหรือไม่ (เสี่ยงเกิด `KeyError`)
  3. ไม่มีการป้องกันสต็อกติดลบ: ถ้ายอดคงเหลือมี 5 ชิ้น แต่สั่งตัด 10 ชิ้น ค่าสต็อกจะกลายเป็น -5 ทันที
  4. ขาด Type Hints และ Docstring

---

## 2. การทดลองรอบที่ 2: Prompt ที่แนบ Context ครบถ้วน (Context Engineering)

### Prompt และ Context ที่แนบ
```text
คุณคือ Senior Python Developer สำหรับระบบคลังสินค้า (Team 12 Inventory)
กรุณาเขียนเมธอดสำหรับตัดจ่ายสต็อกสินค้า (sell) เพิ่มเติมในคลาส Inventory โดยต้องปฏิบัติตามบริบทและข้อกำหนดด้านล่างนี้อย่างเคร่งครัด:

[Context 1: โค้ดเดิมของระบบ inventory.py]
class InventoryItem:
    def __init__(self, name: str, quantity: int, price: float):
        self.name = name.strip()
        self.quantity = quantity
        self.price = price

class Inventory:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}

[Context 2: เกณฑ์ที่ Output ต้องผ่าน (Acceptance Criteria)]
1. ถ้าไม่พบชื่อสินค้าใน self._items ให้ raise KeyError พร้อมข้อความว่า "ไม่พบสินค้า '<name>' ในระบบ"
2. ถ้าจำนวนที่ขาย (amount) <= 0 ให้ raise ValueError ว่า "จำนวนที่ขายต้องมากกว่าศูนย์"
3. ถ้าจำนวนคงเหลือไม่พอขาย ให้ raise ValueError พร้อมระบุจำนวนคงเหลือและจำนวนที่ต้องการขาย
4. ลดจำนวนสินค้าลงตามจริง และคืนค่าจำนวนคงเหลือใหม่ (int)

[Context 3: ข้อจำกัดทางเทคนิค (Constraints)]
- ห้ามใช้ External Library (ใช้เฉพาะ Built-in Python)
- ต้องมี Type Hint ครบทุก Parameter และ Return Type
- มี Docstring ภาษาไทยอธิบายการทำงาน
```

### ผลลัพธ์โค้ดที่ AI สร้างให้
```python
    def sell(self, name: str, amount: int) -> int:
        """
        ตัดจ่ายสินค้าออกจากสต็อก
        :param name: ชื่อสินค้าที่ต้องการขาย
        :param amount: จำนวนสินค้าที่ขาย (ต้องเป็นจำนวนเต็มบวก)
        :return: จำนวนสต็อกคงเหลือล่าสุด
        :raises KeyError: เมื่อไม่พบสินค้าในระบบ
        :raises ValueError: เมื่อจำนวนที่ขาย <= 0 หรือสต็อกไม่เพียงพอ
        """
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
        
        item = self._items[name]
        if item.quantity < amount:
            raise ValueError(
                f"สินค้า '{name}' คงเหลือ {item.quantity} ชิ้น "
                f"ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
            )
        
        item.quantity -= amount
        return item.quantity
```

---

## 3. สรุปการเปรียบเทียบ: อะไรทำให้ผลลัพธ์ต่างกัน?

| มิติการเปรียบเทียบ | รอบที่ 1: Prompt สั้น | รอบที่ 2: Prompt + Context Engineering |
|---|---|---|
| **ความเข้ากันได้กับโค้ดเดิม** | ไม่สามารถนำไปใช้ได้จริง ต้องแก้ใหม่หมดเพราะ Interface ผิด | นำไปวางในคลาส `Inventory` ได้ทันทีแบบ Plug & Play 100% |
| **การจัดการ Edge Cases** | สต็อกติดลบได้, ไม่ดักค่าแปลกปลอม, พังง่าย | ดักจับ Exception ครบทุกกรณี (รหัสซ้ำ, ข้อมูลไม่พอ, ค่าติดลบ) |
| **ความปลอดภัยของข้อมูล** | ต่ำมาก (เกิด Race Condition และ Data Corruption ได้ง่าย) | สูง มีการตรวจเช็ค Pre-condition ก่อนแก้ไข State |
| **ความชัดเจนของโค้ด** | ไม่มี Type hint หรือคำอธิบาย | มี Type hint และ Docstring ภาษาไทยตาม Coding Standards |

### สรุปบทเรียนสำคัญ
> **"Prompt สั่งว่าต้องการอะไร แต่ Context บอกว่าต้องทำในสภาพแวดล้อมแบบไหน"**  
> การให้ AI เขียนโค้ดโดยไม่มี Context จะทำให้ AI "เดาสภาพแวดล้อมเอาเอง" ซึ่งมักจะเลือกโครงสร้างที่ง่ายและหละหลวมที่สุด แต่เมื่อเราใส่ **โค้ดเดิม (Interface) + Acceptance Criteria (Testable rules) + Constraints (ข้อจำกัด)** AI จะทำงานได้แม่นยำเทียบเท่ากับ Senior Engineer โดยแทบไม่ต้องแก้ไขโค้ดด้วยมือเลย
