# inventory_no_context.py
# โค้ดที่สร้างขึ้นจาก Spec โดย "ไม่มี Context / .ai-rules.md"
# สังเกตปัญหา: รวมทุกอย่างในไฟล์เดียว, hardcode การแจ้งเตือน, ไม่มี protocol/interface, ละเมิด SOLID (SRP/OCP/DIP)

class InventorySystem:
    def __init__(self):
        self.products = {}
        self.categories = {}
        self.email_admin = "admin@store.com"
        self.sms_phone = "081-234-5678"

    def add_product(self, code, name, category, qty, price, threshold=10):
        self.products[code] = {
            "name": name,
            "category": category,
            "qty": qty,
            "price": price,
            "threshold": threshold
        }
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(code)

    def issue(self, code, amount):
        if code not in self.products:
            print("Error: Product not found")
            return False

        item = self.products[code]
        if item["qty"] < amount:
            print("Error: Insufficient stock")
            return False

        item["qty"] -= amount
        print(f"Issued {amount} of {item['name']}. Remaining: {item['qty']}")

        # Hardcoded notification logic (ละเมิด SRP และ OCP)
        if item["qty"] < item["threshold"]:
            print(f"[Email to {self.email_admin}] Alert: Stock for {item['name']} is low ({item['qty']} left)")
            print(f"[SMS to {self.sms_phone}] Alert: Stock for {item['name']} is low ({item['qty']} left)")

        return True

    def receive(self, code, amount):
        if code not in self.products:
            return False
        self.products[code]["qty"] += amount
        return True

    def get_category_valuation(self):
        # รวมการคำนวณและการ print ไว้ด้วยกัน
        report = {}
        for cat, codes in self.categories.items():
            total = 0
            for c in codes:
                p = self.products[c]
                total += p["qty"] * p["price"]
            report[cat] = total
            print(f"Category: {cat} -> Total Valuation: {total:,.2f} THB")
        return report
