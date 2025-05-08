from playwright.sync_api import sync_playwright

def fill_google_form():
    with sync_playwright() as p:
        # เปิดเบราว์เซอร์
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # URL ของ Google Form
        form_url = "https://forms.gle/7XhH7HpNVgCQ3Neo7"
        page.goto(form_url)

        def get_questions():
            try:
                elements = page.query_selector_all("div[role='listitem']")
                questions = []
                for element in elements:
                    question_text_el = element.query_selector("div[data-params] span")
                    question_text = question_text_el.inner_text().strip() if question_text_el else "ส่วนที่ไม่มีชื่อ"

                    # ตรวจสอบว่าคำถามมีคำถามย่อย (เช่นแบบกริด)
                    sub_question_elements = element.query_selector_all("div[role='gridcell']")
                    if sub_question_elements:
                        sub_questions = []
                        for sub_element in sub_question_elements:
                            sub_text_el = sub_element.query_selector("span")
                            sub_text = sub_text_el.inner_text().strip() if sub_text_el else "(ไม่มีข้อความ)"

                            # หา choices สำหรับคำถามย่อย
                            choice_els = sub_element.query_selector_all("div[role='radio'], div[role='checkbox']")
                            choices = []
                            for choice_el in choice_els:
                                label_text = choice_el.get_attribute("aria-label") or "(ไม่มีข้อความ)"
                                choices.append({
                                    "element": choice_el,
                                    "label": label_text,
                                })

                            sub_questions.append({
                                "element": sub_element,
                                "text": sub_text,
                                "choices": choices
                            })

                        questions.append({
                            "element": element,
                            "text": question_text,
                            "type": "grid",
                            "sub_questions": sub_questions
                        })
                    else:
                        # กรณีคำถามปกติ
                        choice_els = element.query_selector_all("div[role='radio'], div[role='checkbox']")
                        choices = []
                        for choice_el in choice_els:
                            label_text = choice_el.get_attribute("aria-label") or "(ไม่มีข้อความ)"
                            choices.append({
                                "element": choice_el,
                                "label": label_text,
                            })

                        questions.append({
                            "element": element,
                            "text": question_text,
                            "choices": choices,
                            "type": "single"
                        })
                return questions
            except Exception as e:
                print(f"Error while fetching questions: {e}")
                return []



        def fill_question(question):
            try:
                print(f"{question['text']}")

                if question["type"] == "grid":
                    # จัดการคำถามแบบกริด
                    for sub_question in question["sub_questions"]:
                        print(f"  {sub_question['text']}")
                        if sub_question["choices"]:
                            for i, choice in enumerate(sub_question["choices"], start=1):
                                print(f"    {i}. {choice['label']}")

                            choice_input = input("→ ใส่คะแนน (1-5): ").strip()
                            if choice_input.isdigit():
                                index = int(choice_input) - 1
                                if 0 <= index < len(sub_question["choices"]):
                                    selected = sub_question["choices"][index]
                                    selected["element"].click(force=True)
                elif question["type"] == "single" and question["choices"]:
                    # จัดการคำถามปกติ
                    for i, choice in enumerate(question["choices"], start=1):
                        print(f"  {i}. {choice['label']}")

                    choice_input = input("→ ใส่คะแนน (1-5): ").strip()
                    if choice_input.isdigit():
                        index = int(choice_input) - 1
                        if 0 <= index < len(question["choices"]):
                            selected = question["choices"][index]
                            selected["element"].click(force=True)
                else:
                    # กรอกคำตอบแบบข้อความ
                    answer = input("กรอกคำตอบ (Enter เพื่อข้าม): ").strip()
                    if answer:
                        text_input = question["element"].query_selector("input[type='text']")
                        if text_input:
                            text_input.fill(answer)
            except Exception as e:
                print(f"Error while filling question: {e}")


        def click_next_or_submit(page):
            try:
                # กำหนดตัวเลือกของปุ่มต่างๆ
                next_button_selector = "div[role='button'] span.NPEfkd.RveJvd.snByac:has-text('ถัดไป')"
                submit_button_selector = "div[role='button'] span.NPEfkd.RveJvd.snByac:has-text('ส่ง')"
                back_button_selector = "div[role='button'] span.NPEfkd.RveJvd.snByac:has-text('กลับ')"

                # รอให้หน้าเว็บโหลดเสร็จ
                page.wait_for_load_state("networkidle", timeout=20000)  # เพิ่มเวลาให้พอสำหรับหน้าเว็บโหลด
                print("หน้าเว็บโหลดเสร็จแล้ว")

                # ลูปตรวจสอบปุ่ม "ถัดไป" หรือ "ส่ง" หรือ "กลับ"
                for button_selector in [next_button_selector, submit_button_selector, back_button_selector]:
                    button = page.locator(button_selector)
                    if button.is_visible():
                        print(f"พบปุ่ม {button_selector} จะคลิก")
                        button.click(force=True)
                        page.wait_for_load_state("networkidle")  # รอให้หน้าใหม่โหลด
                        if button_selector == submit_button_selector:
                            print("คลิกปุ่มส่งแล้ว")
                            return False
                        return True
                
                print("ไม่พบปุ่มที่ต้องการ")
                return False

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการคลิกปุ่ม: {e}")
                return False




        try:
            # Loop ผ่านคำถามในแต่ละหน้า
            while True:
                questions = get_questions()
                if not questions:
                    print("ไม่มีคำถามในหน้านี้ หรือหน้าฟอร์มโหลดไม่สำเร็จ")
                    break

                for question in questions:
                    fill_question(question)

                if not click_next_or_submit(page):
                    break
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            # ปิดเบราว์เซอร์
            print("ปิดเบราว์เซอร์")
            browser.close()

if __name__ == "__main__":
    fill_google_form()