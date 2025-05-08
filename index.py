from playwright.sync_api import sync_playwright


def fill_google_form():
    # ชุดคำถาม
    questions = [
        {"type": "text", "question": "ชื่อชุมชน/ชุดที่:"},
        {"type": "radio", "question": "เพศ",
            "options": ["หญิง", "ชาย", "อื่นๆ"]},
        {"type": "text", "question": "อายุ:"},
        {"type": "radio", "question": "ท่านอาศัยอยู่ในเขตใดของเทศบาลนครนครศรีธรรมราช",
            "options": ["เขต 1", "เขต 2", "เขต 3", "เขตอื่นๆ"]},
        {"type": "radio", "question": "ระดับการศึกษา", "options": [
            "ประถม", "มัธยม", "ปริญญาตรี", "ปริญญาโท", "ปริญญาเอก"]},
        {"type": "radio", "question": "อาชีพ", "options": [
            "พนักงานบริษัท", "เจ้าของกิจการ", "นักเรียน", "อื่นๆ"]},

        {"type": "radio", "question": "ท่านอาศัยในเทศบาลนครนครศรีธรรมราชมานานเท่าใด",
            "options": ["น้อยกว่า 5 ปี", "5-10 ปี", "มากกว่า 10 ปี"]},
        {"type": "radio", "question": "ท่านเคยเข้าร่วมกิจกรรมของเทศบาลนครนครศรีธรรมราชมากน้อยเพียงใด",
            "options": ["ไม่เคย", "1-5 ครั้ง", "6-10 ครั้ง", "มากกว่า 10 ครั้ง"]},
        {"type": "checkbox", "question": "ประเภทกิจกรรมที่ท่านเคยเข้าร่วม (ถ้าเคย)", 
         "options": [ "โครงการของเทศบาล (เช่น NakhonCity LineOA, โครงการถนนปลอดขยะ)", "กิจกรรมของภาคเอกชน", "กิจกรรมของสถานศึกษา"]},
        {"type": "checkbox", "question": "ช่องทางที่ท่านรับข่าวสารเกี่ยวกับโครงการของเทศบาล",
            "options": ["โซเชียลมีเดีย (Facebook, Line)", "เว็บไซต์ของเทศบาล", "การบอกต่อจากคนในชุมชน"]},


        {"type": "grid", "question": "ส่วนที่ 3.1 เมืองน่าอยู่ที่ชาญฉลาด มีทั้งหมด 12 ข้อ", "rows": [
            f"ข้อ {i}" for i in range(1, 13)], "columns": ["มากที่สุด", "มาก", "ปานกลาง", "น้อย", "น้อยที่สุด"]},
        {"type": "grid", "question": "ส่วนที่ 3.2 ความเป็นผู้นำและวิสัยทัศน์ของผู้บริหารเทศบาลนครนครศรีธรรมราช", "rows": [
            f"ข้อ {i}" for i in range(1, 10)], "columns": ["มากที่สุด", "มาก", "ปานกลาง", "น้อย", "น้อยที่สุด"]},
        {"type": "grid", "question": "ส่วนที่ 3.3 การนำแนวคิด นโยบาย และกลไกการขับเคลื่อนเมืองน่าอยู่ที่ชาญฉลาด", "rows": [
            f"ข้อ {i}" for i in range(1, 11)], "columns": ["มากที่สุด", "มาก", "ปานกลาง", "น้อย", "น้อยที่สุด"]},
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://forms.gle/7XhH7HpNVgCQ3Neo7")
        page.wait_for_load_state("networkidle")  # รอให้ฟอร์มโหลดเสร็จ

        # ตรวจสอบจำนวนคำถามในฟอร์ม
        question_blocks = page.query_selector_all('div[role="listitem"]')
        print(f"จำนวนคำถามที่โหลดในฟอร์ม: {len(question_blocks)}")

        # เริ่มกรอกคำถาม
        i = 0
        while i < len(questions):
            page.wait_for_load_state("networkidle")  # รอให้คำถามโหลดเสร็จ

            # ตรวจสอบจำนวนคำถามที่โหลดใหม่หลังจากคลิก "ถัดไป"
            question_blocks = page.query_selector_all('div[role="listitem"]')
            print(f"จำนวนคำถามที่โหลดในฟอร์ม: {len(question_blocks)}")

            if len(question_blocks) > i:  # ให้มั่นใจว่าเรากำลังกรอกคำถามที่มีอยู่
                q = questions[i]
                block = question_blocks[i]

                try:
                    print(f"กำลังถามคำถาม: {q['question']}")

                    if q["type"] == "text":
                        input_box = block.query_selector('input[type="text"]')
                        if input_box:
                            user_input = input(
                                f"{q['question']} (Enter เพื่อข้าม): ").strip()
                            if user_input != "":  # ถ้าผู้ใช้กรอกคำตอบ
                                input_box.fill(user_input)

                    elif q["type"] == "radio":
                        radios = block.query_selector_all('div[role="radio"]')
                        if radios:
                            print(f"คำถาม: {q['question']}")
                            for idx, r in enumerate(radios):
                                print(f"{idx+1}. {r.inner_text().strip()}")
                            ans = input("เลือก (ตัวเลข): ").strip()
                            if ans.isdigit():
                                idx = int(ans) - 1
                                if 0 <= idx < len(radios):
                                    radios[idx].click()

                    elif q["type"] == "checkbox":
                        checkboxes = block.query_selector_all(
                            'div[role="checkbox"]')
                        if checkboxes:
                            print(f"คำถาม: {q['question']}")
                            for idx, c in enumerate(checkboxes):
                                print(f"{idx+1}. {c.inner_text().strip()}")
                            ans = input("เลือกหลายตัว (1,3,...): ").strip()
                            if ans:
                                for s in ans.split(","):
                                    if s.strip().isdigit():
                                        idx = int(s.strip()) - 1
                                        if 0 <= idx < len(checkboxes):
                                            checkboxes[idx].click()

                    elif q["type"] == "grid":
                        rows = block.query_selector_all('div[role="row"]')
                        if rows:
                            print(f"คำถาม: {q['question']}")
                            for row_idx, row in enumerate(rows):
                                print(f"แถว {row_idx+1}:")
                                columns = row.query_selector_all(
                                    'div[role="cell"]')
                                for col_idx, col in enumerate(columns):
                                    print(
                                        f"{col_idx+1}. {col.inner_text().strip()}")
                                ans = input(
                                    f"เลือกสำหรับแถว {row_idx+1}: (ใส่ตัวเลข): ").strip()
                                if ans.isdigit():
                                    col_idx = int(ans) - 1
                                    if 0 <= col_idx < len(columns):
                                        columns[col_idx].click()

                    # รอการตอบจากผู้ใช้ก่อนที่จะคลิกปุ่มถัดไปหรือส่ง
                    input("กด Enter เพื่อไปยังคำถามถัดไป...")

                    # คลิกถัดไปหรือส่ง
                    wait_and_click_next_or_submit(page)
                    i += 1

                except Exception as e:
                    print(f"❌ ข้อผิดพลาดในคำถาม {i+1}: {e}")
                    break
            else:
                print(f"คำถามที่ {i+1} ยังไม่ได้โหลดครบ")
                break

        print("✅ เสร็จสิ้น")
        page.wait_for_timeout(2000)
        browser.close()


def wait_and_click_next_or_submit(page):
    try:
        # หาปุ่มถัดไป
        next_button = page.query_selector(
            'div[role="button"]:has-text("ถัดไป")')
        if next_button:
            next_button.click()
            print("คลิกปุ่มถัดไป")
        else:
            # หาปุ่มส่งหากไม่มีปุ่มถัดไป
            submit_button = page.query_selector(
                'div[role="button"]:has-text("ส่ง")')
            if submit_button:
                submit_button.click()
                print("คลิกปุ่มส่ง")
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการคลิกถัดไป/ส่ง: {e}")


if __name__ == "__main__":
    fill_google_form()
