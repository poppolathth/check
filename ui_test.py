import json
from datetime import date

# กรอกข้อมูลจากผู้ใช้
name = input("ชื่อฟอร์ม: ") or "test"
answer1 = input("กรอกคำตอบข้อ 1: ")
answer2 = input("กรอกคำตอบข้อ 2 (ตัวเลข): ")

commands = [
    {
        "Command": "open",
        "Target": "https://forms.gle/7XhH7HpNVgCQ3Neo7",
        "Value": "",
        "Description": ""
    },
    {
        "Command": "click",
        "Target": "xpath=//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/input",
        "Value": "",
        "Targets": [
            "xpath=//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/input"
        ],
        "Description": ""
    },
    {
        "Command": "type",
        "Target": "xpath=//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/input",
        "Value": answer1,
        "Targets": [],
        "Description": ""
    },
    {
        "Command": "click",
        "Target": "xpath=//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/input",
        "Value": "",
        "Targets": [],
        "Description": ""
    },
    {
        "Command": "type",
        "Target": "xpath=//*[@id=\"mG61Hd\"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/input",
        "Value": answer2,
        "Targets": [],
        "Description": ""
    },
    {
        "Command": "clickAndWait",
        "Target": "xpath=//*[@id=\"mG61Hd\"]/div[2]/div/div[3]/div/div/div[2]/span/span",
        "Value": "",
        "Targets": [],
        "Description": ""
    }
]

output = {
    "Name": name,
    "CreationDate": str(date.today()),
    "Commands": commands
}

with open("form_script.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("✅ สร้างไฟล์ form_script.json สำเร็จ")
