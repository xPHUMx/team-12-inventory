# TEAM_CHARTER.md

## สมาชิกและบทบาท

| ชื่อ | GitHub Username | บทบาท |
|---|---|---|
| Phumiphat (Solo Developer) | (รอระบุ) | Product Owner / Scrum Master / Developer |

## Branching Strategy

ทีมใช้ GitHub Flow:
- main branch ต้อง deploy ได้เสมอ ห้าม commit โดยตรง (ยกเว้น initial setup)
- ทุก feature ใหม่ต้องสร้าง branch ชื่อ `feat/<issue-number>-<short-name>`
- ทุก PR ต้องมีคนอื่นในทีมอย่างน้อย 1 คน review และ approve ก่อน merge (กรณีทำเดี่ยว สามารถใช้ AI ช่วย review ตรวจสอบ diff หรือ self-review อย่างละเอียด)

## เพดานงานที่ทำพร้อมกัน (WIP limit)

- คอลัมน์ In Progress มีการ์ดพร้อมกันได้ไม่เกิน 1-2 ใบ (สำหรับ 1 คนทำเดี่ยว)
- เมื่อชนเพดาน ห้ามลากการ์ดใหม่เข้ามา ให้ช่วยกันปิดของเดิมหรือรีวิว PR ที่ค้างใน In Review ก่อน
- ปรับเพดานระหว่าง sprint ได้ แต่ต้องเขียนเหตุผลกำกับไว้ท้ายหัวข้อนี้ ไม่ใช่ปรับเพราะการ์ดล้น

## Sprint Goal (Sprint 1)

sprint นี้ทีมจะส่งมอบระบบสต็อกร้านเขียนดีที่รองรับ US-01, US-02, US-03, US-04, US-05 ที่รันได้จริงบน Command-line และผ่าน acceptance criteria ครบถ้วนพร้อม Unit Test

## AI Usage Policy

- ใช้ AI ช่วยเขียน draft code และ draft commit message ได้
- ทุก commit message ที่ AI generate ต้องอ่านและแก้ให้ตรงกับ diff จริงก่อน commit
- ห้าม copy code จาก AI โดยไม่อ่านและทำความเข้าใจก่อน
- ใช้เฉพาะ AI ที่ไม่มีค่าใช้จ่าย ไม่บังคับซื้อ subscription
