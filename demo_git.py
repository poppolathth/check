from playwright.sync_api import sync_playwright
import time

def fill_google_form():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        form_url = "https://forms.gle/7XhH7HpNVgCQ3Neo7"
        page.goto(form_url)

        def get_questions():
            try:
                elements = page.query_selector_all("div[role='listitem']")
                questions = []
                
                # สร้างฟังก์ชันช่วยในการแยกคำถามและตัวเลือก
                def extract_question_from_choice(choice_text):
                    # แยกส่วนที่เป็นคำถามออกจากตัวเลือก
                    if "เป็นคำตอบสำหรับ" in choice_text:
                        return choice_text.split("เป็นคำตอบสำหรับ")[1].strip()
                    return None

                def group_choices_by_question(choices):
                    # จัดกลุ่มตัวเลือกตามคำถาม
                    question_groups = {}
                    for choice in choices:
                        question_text = extract_question_from_choice(choice["label"])
                        if question_text:
                            if question_text not in question_groups:
                                question_groups[question_text] = []
                            question_groups[question_text].append(choice)
                    return question_groups

                for element in elements:
                    section_title = element.query_selector("div[role='heading']")
                    if section_title:
                        print(f"\n=== {section_title.inner_text().strip()} ===\n")

                    # ดึงตัวเลือกทั้งหมดในส่วนนี้
                    choice_elements = element.query_selector_all("div[role='radio']")
                    all_choices = []
                    
                    for choice_el in choice_elements:
                        label = choice_el.get_attribute("aria-label")
                        if label:
                            all_choices.append({
                                "element": choice_el,
                                "label": label
                            })

                    # จัดกลุ่มตัวเลือกตามคำถาม
                    question_groups = group_choices_by_question(all_choices)

                    # สร้างคำถามจากกลุ่มตัวเลือก
                    for question_text, choices in question_groups.items():
                        questions.append({
                            "text": question_text,
                            "choices": sorted(choices, key=lambda x: "มากที่สุด" in x["label"], reverse=True)
                        })

                return questions

            except Exception as e:
                print(f"Error while fetching questions: {e}")
                return []

        def fill_question(question):
            try:
                print(f"\nคำถาม: {question['text']}")
                print("\nตัวเลือก:")
                for i, choice in enumerate(question['choices'], 1):
                    # แสดงเฉพาะระดับคะแนน
                    level = ""
                    if "มากที่สุด (5)" in choice["label"]: level = "5 - มากที่สุด"
                    elif "มาก (4)" in choice["label"]: level = "4 - มาก"
                    elif "ปานกลาง (3)" in choice["label"]: level = "3 - ปานกลาง"
                    elif "น้อย (2)" in choice["label"]: level = "2 - น้อย"
                    elif "น้อยที่สุด (1)" in choice["label"]: level = "1 - น้อยที่สุด"
                    print(f"  {level}")

                while True:
                    choice_input = input("\n→ กรุณาใส่คะแนน (1-5) หรือกด Enter เพื่อข้าม: ").strip()
                    
                    if choice_input == "":
                        print("ข้ามไปข้อถัดไป...")
                        break
                    
                    if choice_input.isdigit():
                        score = int(choice_input)
                        if 1 <= score <= 5:
                            # หาตัวเลือกที่ตรงกับคะแนนที่เลือก
                            score_text = {
                                5: "มากที่สุด (5)",
                                4: "มาก (4)",
                                3: "ปานกลาง (3)",
                                2: "น้อย (2)",
                                1: "น้อยที่สุด (1)"
                            }
                            
                            for choice in question["choices"]:
                                if score_text[score] in choice["label"]:
                                    try:
                                        choice["element"].click(force=True)
                                        print(f"เลือกคะแนน {score} สำเร็จ")
                                        time.sleep(0.5)
                                        break
                                    except Exception as click_error:
                                        print(f"ไม่สามารถคลิกตัวเลือกได้: {click_error}")
                            break
                        else:
                            print("กรุณาใส่คะแนนระหว่าง 1-5 เท่านั้น")
                    else:
                        print("กรุณาใส่ตัวเลขเท่านั้น")

                print("-" * 50)  # เส้นแบ่งระหว่างคำถาม

            except Exception as e:
                print(f"Error while filling question: {e}")


        def click_next_or_submit(page):
            try:
                next_button_selector = "div[role='button'] span.NPEfkd.RveJvd.snByac:has-text('ถัดไป')"
                submit_button_selector = "div[role='button'] span.NPEfkd.RveJvd.snByac:has-text('ส่ง')"
                back_button_selector = "div[role='button'] span.NPEfkd.RveJvd.snByac:has-text('กลับ')"

                page.wait_for_load_state("networkidle", timeout=20000)
                print("หน้าเว็บโหลดเสร็จแล้ว")

                for button_selector in [next_button_selector, submit_button_selector, back_button_selector]:
                    button = page.locator(button_selector)
                    if button.is_visible():
                        print(f"พบปุ่ม {button_selector} จะคลิก")
                        button.click(force=True)
                        page.wait_for_load_state("networkidle")
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
            print("ปิดเบราว์เซอร์")
            browser.close()

if __name__ == "__main__":
    fill_google_form()