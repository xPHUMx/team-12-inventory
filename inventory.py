import os
import json
import csv
import sys
import argparse

# Ensure standard streams use UTF-8 on Windows
if sys.version_info >= (3, 7):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_DB_FILE = "inventory.json"


def load_items(filepath=DEFAULT_DB_FILE):
    """โหลดข้อมูลสินค้าจากไฟล์ JSON"""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_items(items, filepath=DEFAULT_DB_FILE):
    """บันทึกข้อมูลสินค้าลงไฟล์ JSON"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def list_items(filepath=DEFAULT_DB_FILE):
    """
    US-01: ดูรายการสินค้าทั้งหมดพร้อมจำนวนคงเหลือ
    AC-1: แสดงชื่อ รหัส และจำนวนคงเหลือครบทุกรายการ
    AC-2: ถ้ายังไม่มีสินค้า แสดง "ยังไม่มีสินค้าในระบบ"
    """
    items = load_items(filepath)
    if not items:
        return "ยังไม่มีสินค้าในระบบ"

    lines = [f"=== รายการสินค้าในสต็อก (ทั้งหมด {len(items)} รายการ) ==="]
    for item in items:
        code = item.get("code", "")
        name = item.get("name", "")
        qty = item.get("quantity", 0)
        lines.append(f"รหัส: {code} | ชื่อ: {name} | คงเหลือ: {qty}")
    return "\n".join(lines)


def add_item(code, name, quantity, filepath=DEFAULT_DB_FILE):
    """
    US-02: เพิ่มสินค้าใหม่เข้าระบบ
    AC-1: บันทึกสินค้าใหม่ (จำนวนเริ่มต้น >= 0)
    AC-2: ถ้ามีสินค้ารหัสนี้อยู่แล้ว แสดง "รหัสสินค้าซ้ำ" โดยไม่เขียนทับ
    """
    if quantity < 0:
        return False, "จำนวนสินค้าเริ่มต้นต้องไม่ติดลบ"

    code = str(code).strip()
    name = str(name).strip()

    if not code or not name:
        return False, "รหัสและชื่อสินค้าต้องไม่เป็นค่าว่าง"

    items = load_items(filepath)
    for item in items:
        if item.get("code") == code:
            return False, "รหัสสินค้าซ้ำ"

    new_item = {
        "code": code,
        "name": name,
        "quantity": int(quantity)
    }
    items.append(new_item)
    save_items(items, filepath)
    return True, f"เพิ่มสินค้าสำเร็จ: {code} - {name} ({quantity} ชิ้น)"


def adjust_quantity(code, delta, filepath=DEFAULT_DB_FILE):
    """
    US-03: แก้ไขจำนวนสินค้าเมื่อรับหรือจ่ายของ
    AC-1: อัปเดตยอดคงเหลือและบันทึกทันที
    AC-2: ถ้าจ่ายออกมากกว่าคงเหลือ แสดง "จำนวนคงเหลือไม่พอ"
    """
    code = str(code).strip()
    items = load_items(filepath)

    found = False
    for item in items:
        if item.get("code") == code:
            found = True
            current_qty = item.get("quantity", 0)
            new_qty = current_qty + delta
            if new_qty < 0:
                return False, "จำนวนคงเหลือไม่พอ"
            item["quantity"] = new_qty
            save_items(items, filepath)
            return True, f"อัปเดตสต็อกรหัส {code} สำเร็จ: ยอดคงเหลือใหม่คือ {new_qty}"

    if not found:
        return False, f"ไม่พบสินค้ารหัส {code}"


def search_items(query, filepath=DEFAULT_DB_FILE):
    """
    US-04: ค้นหาสินค้าด้วยชื่อหรือรหัส
    AC-1: แสดงเฉพาะรายการที่ตรง พร้อมชื่อ รหัส จำนวนคงเหลือ
    AC-2: ถ้าไม่พบ แสดง "ไม่พบสินค้าที่ตรงกับคำค้น"
    """
    query = str(query).strip().lower()
    if not query:
        return "กรุณาระบุคำค้นหา"

    items = load_items(filepath)
    matched = []
    for item in items:
        code = str(item.get("code", "")).lower()
        name = str(item.get("name", "")).lower()
        if query in code or query in name:
            matched.append(item)

    if not matched:
        return "ไม่พบสินค้าที่ตรงกับคำค้น"

    lines = [f"=== ผลการค้นหาสำหรับ '{query}' ==="]
    for item in matched:
        lines.append(f"รหัส: {item.get('code')} | ชื่อ: {item.get('name')} | คงเหลือ: {item.get('quantity')}")
    return "\n".join(lines)


def export_csv(output_filepath, filepath=DEFAULT_DB_FILE):
    """
    US-05: ส่งออกรายงานสต็อกเป็นไฟล์ CSV
    AC-1: ได้ไฟล์ CSV มีหัวคอลัมน์ (รหัส, ชื่อ, จำนวนคงเหลือ) ครบทุกรายการ
    AC-2: ถ้าไม่มีสินค้า ได้ไฟล์ที่มีเฉพาะหัวคอลัมน์ และแจ้ง "ยังไม่มีข้อมูลสินค้า"
    """
    items = load_items(filepath)
    headers = ["รหัส", "ชื่อ", "จำนวนคงเหลือ"]

    with open(output_filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for item in items:
            writer.writerow([item.get("code", ""), item.get("name", ""), item.get("quantity", 0)])

    if not items:
        return True, "ยังไม่มีข้อมูลสินค้า (สร้างไฟล์ CSV เฉพาะหัวคอลัมน์แล้ว)"
    return True, f"ส่งออกรายงานสต็อกไปยัง {output_filepath} สำเร็จ ({len(items)} รายการ)"


def main():
    parser = argparse.ArgumentParser(description="ระบบจัดการสต็อกร้านเขียนดี (team-12-inventory)")
    subparsers = parser.add_subparsers(dest="command", help="คำสั่งที่ต้องการรัน")

    # Command: list
    subparsers.add_parser("list", help="แสดงรายการสินค้าทั้งหมด")

    # Command: add
    parser_add = subparsers.add_parser("add", help="เพิ่มสินค้าใหม่")
    parser_add.add_argument("code", help="รหัสสินค้า เช่น P001")
    parser_add.add_argument("name", help="ชื่อสินค้า เช่น ปากกาน้ำเงิน")
    parser_add.add_argument("quantity", type=int, help="จำนวนสินค้าเริ่มต้น")

    # Command: adjust
    parser_adj = subparsers.add_parser("adjust", help="ปรับจำนวนสต็อก (+รับเข้า / -จ่ายออก)")
    parser_adj.add_argument("code", help="รหัสสินค้า")
    parser_adj.add_argument("delta", type=int, help="จำนวนที่เปลี่ยนแปลง เช่น +10 หรือ -5")

    # Command: search
    parser_search = subparsers.add_parser("search", help="ค้นหาสินค้าด้วยรหัสหรือชื่อ")
    parser_search.add_argument("query", help="คำค้นหา")

    # Command: export
    parser_export = subparsers.add_parser("export", help="ส่งออกข้อมูลเป็น CSV")
    parser_export.add_argument("output", help="ชื่อไฟล์ปลายทาง เช่น stock.csv")

    args = parser.parse_args()

    if args.command == "list":
        print(list_items())
    elif args.command == "add":
        success, msg = add_item(args.code, args.name, args.quantity)
        print(msg)
    elif args.command == "adjust":
        success, msg = adjust_quantity(args.code, args.delta)
        print(msg)
    elif args.command == "search":
        print(search_items(args.query))
    elif args.command == "export":
        success, msg = export_csv(args.output)
        print(msg)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
