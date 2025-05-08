from playwright.sync_api import sync_playwright
import time
from datetime import datetime

def fill_google_form():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        form_url = "https://forms.gle/7XhH7HpNVgCQ3Neo7"
        page.goto(form_url)

        def safe_click(element, max_retries=3):
            """Improved click handling with retries"""
            for attempt in range(max_retries):
                try:
                    element.click(force=True)
                    time.sleep(0.5)
                    return True
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"คลิกไม่สำเร็จหลังจากพยายาม {max_retries} ครั้ง: {e}")
                        return False
                    time.sleep(1)
            return False

        def get_questions():
            """
            ดึงข้อมูลคำถามทั้งหมดจากแบบฟอร์ม Google Form
            รองรับคำถามประเภท: grid, radio, checkbox, และ text
            """
            try:
                elements = page.query_selector_all("div[role='listitem']")
                questions = []
                
                def is_grid_question(element):
                    """ตรวจสอบว่าเป็นคำถามแบบตารางกริดหรือไม่"""
                    choices = element.query_selector_all("div[role='radio']")
                    if not choices:
                        return False
                    first_choice = choices[0].get_attribute("aria-label")
                    return first_choice and "เป็นคำตอบสำหรับ" in first_choice

                def is_checkbox_question(element):
                    """ตรวจสอบว่าเป็นคำถามแบบเลือกได้หลายข้อหรือไม่"""
                    return bool(element.query_selector("div[role='checkbox']"))

                def extract_question_from_choice(choice_text):
                    """แยกข้อความคำถามจากตัวเลือกในคำถามแบบกริด"""
                    if "เป็นคำตอบสำหรับ" in choice_text:
                        return choice_text.split("เป็นคำตอบสำหรับ")[1].strip()
                    return None

                def group_choices_by_question(choices):
                    """จัดกลุ่มตัวเลือกตามคำถามย่อยในคำถามแบบกริด"""
                    question_groups = {}
                    for choice in choices:
                        question_text = extract_question_from_choice(choice["label"])
                        if question_text:
                            if question_text not in question_groups:
                                question_groups[question_text] = []
                            question_groups[question_text].append(choice)
                    return question_groups

                def get_choice_label(container):
                    """ดึงข้อความของตัวเลือกจาก container"""
                    label_elements = [
                        container.query_selector("span.aDTYNe"),
                        container.query_selector("div.YEVVod"),
                        container.query_selector("div.ulDsOb")
                    ]
                    for label_el in label_elements:
                        if label_el:
                            label_text = label_el.inner_text().strip()
                            if label_text:
                                return label_text
                    return "(ไม่มีข้อความ)"

                def get_other_option(element, role):
                    """ดึงข้อมูลตัวเลือก "อื่นๆ" """
                    other_container = element.query_selector("div.nWQGrd.zfdaxb")
                    if other_container:
                        other_element = other_container.query_selector(f"div[role='{role}']")
                        if other_element:
                            return {
                                "element": other_element,
                                "label": "อื่นๆ",
                                "is_other": True,
                                "text_input": element.query_selector("input[type='text']")
                            }
                    return None

                def get_choices(element, role):
                    """ดึงข้อมูลตัวเลือกทั้งหมดของคำถาม"""
                    choices = []
                    
                    # ดึงตัวเลือกปกติ (ไม่รวม "อื่นๆ")
                    containers = element.query_selector_all(f"div.nWQGrd:not(.zfdaxb)")
                    for container in containers:
                        choice_el = container.query_selector(f"div[role='{role}']")
                        if choice_el:
                            label = get_choice_label(container)
                            choices.append({
                                "element": choice_el,
                                "label": label,
                                "is_other": False
                            })

                    # ดึงตัวเลือก "อื่นๆ"
                    other_option = get_other_option(element, role)
                    if other_option:
                        choices.append(other_option)

                    return choices

                for element in elements:
                    try:
                        # ดึงข้อความคำถาม
                        question_text_el = (
                            element.query_selector("div[role='heading']") or 
                            element.query_selector("span.M7eMe") or
                            element.query_selector("div.M7eMe")
                        )
                        question_text = question_text_el.inner_text().strip() if question_text_el else "ส่วนที่ไม่มีชื่อ"

                        if is_grid_question(element):
                            # จัดการกับคำถามแบบกริด
                            choice_elements = element.query_selector_all("div[role='radio']")
                            all_choices = []
                            
                            for choice_el in choice_elements:
                                label = choice_el.get_attribute("aria-label")
                                if label:
                                    all_choices.append({
                                        "element": choice_el,
                                        "label": label
                                    })

                            question_groups = group_choices_by_question(all_choices)

                            for sub_question, choices in question_groups.items():
                                questions.append({
                                    "type": "grid",
                                    "text": sub_question,
                                    "choices": sorted(choices, key=lambda x: "มากที่สุด" in x["label"], reverse=True),
                                    "element": element
                                })

                        elif is_checkbox_question(element):
                            # จัดการกับคำถามแบบเลือกได้หลายข้อ
                            choices = get_choices(element, 'checkbox')
                            if choices:  # เพิ่มคำถามเฉพาะเมื่อมีตัวเลือก
                                questions.append({
                                    "type": "checkbox",
                                    "text": question_text,
                                    "element": element,
                                    "choices": choices
                                })

                        else:
                            # จัดการกับคำถามแบบเลือกได้ข้อเดียวและข้อความ
                            radio_choices = get_choices(element, 'radio')
                            
                            if radio_choices:
                                questions.append({
                                    "type": "radio",
                                    "text": question_text,
                                    "element": element,
                                    "choices": radio_choices
                                })
                            else:
                                # ตรวจสอบ text input
                                text_input = element.query_selector("input[type='text']")
                                if text_input:
                                    questions.append({
                                        "type": "text",
                                        "text": question_text,
                                        "element": element,
                                        "choices": []
                                    })

                    except Exception as e:
                        print(f"ข้อผิดพลาดในการประมวลผลคำถาม: {e}")
                        continue

                # Debug information
                if not questions:
                    print("ไม่พบคำถามในฟอร์ม")
                else:
                    print(f"พบคำถามทั้งหมด {len(questions)} ข้อ")
                    for i, q in enumerate(questions, 1):
                        print(f"{i}. ประเภท: {q['type']}, คำถาม: {q['text']}, ตัวเลือก: {len(q.get('choices', []))}")

                return questions

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการดึงคำถาม: {e}")
                return []        
        
        
        def fill_checkbox_question(question):
            try:
                print(f"\nคำถาม: {question['text']}")
                
                if not question['choices']:
                    print("ไม่พบตัวเลือกสำหรับคำถามนี้")
                    return
                    
                print("\nตัวเลือก:")
                for i, choice in enumerate(question["choices"], 1):
                    print(f"  {i}. {choice['label']}")
                
                print("\nวิธีการตอบ:")
                print("- ใส่ตัวเลขเดียวเพื่อเลือก 1 ตัวเลือก เช่น: 1")
                print("- ใส่ตัวเลขคั่นด้วยจุดเพื่อเลือกหลายตัวเลือก เช่น: 1.2.4")
                
                while True:
                    choice_input = input(f"\n→ เลือกตัวเลือก (1-{len(question['choices'])}) หรือกด Enter เพื่อข้าม: ").strip()
                    
                    if choice_input == "":
                        print("ข้ามไปข้อถัดไป...")
                        break

                    choices = choice_input.split('.')
                    valid_choices = True
                    
                    for choice in choices:
                        if not choice.isdigit() or not (1 <= int(choice) <= len(question["choices"])):
                            valid_choices = False
                            print(f"กรุณาเลือกตัวเลขระหว่าง 1-{len(question['choices'])}")
                            break

                    if valid_choices:
                        for choice_num in choices:
                            selected = question["choices"][int(choice_num) - 1]
                            
                            if safe_click(selected["element"]):
                                print(f"เลือกตัวเลือกที่ {choice_num} สำเร็จ")
                                
                                if selected.get("is_other"):
                                    # รอให้ช่องกรอกข้อความปรากฏ
                                    time.sleep(0.5)
                                    other_text = input("→ กรุณากรอกข้อความสำหรับ 'อื่นๆ': ").strip()
                                    if other_text and selected.get("text_input"):
                                        selected["text_input"].fill(other_text)
                                        print("กรอกข้อความสำหรับ 'อื่นๆ' สำเร็จ")
                        break

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการกรอกคำถามแบบหลายตัวเลือก: {e}")

        def validate_rating_input(input_text):
            """Validate rating input"""
            if not input_text.strip():
                return None
            try:
                score = int(input_text)
                if 1 <= score <= 5:
                    return score
                print("กรุณาใส่คะแนนระหว่าง 1-5 เท่านั้น")
            except ValueError:
                print("กรุณาใส่ตัวเลขเท่านั้น")
            return None

        def fill_grid_question(question):
            try:
                print(f"\nคำถาม: {question['text']}")
                print("\nตัวเลือก:")
                for i, choice in enumerate(question['choices'], 1):
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
                    
                    score = validate_rating_input(choice_input)
                    if score:
                        score_text = {
                            5: "มากที่สุด (5)",
                            4: "มาก (4)",
                            3: "ปานกลาง (3)",
                            2: "น้อย (2)",
                            1: "น้อยที่สุด (1)"
                        }
                        
                        for choice in question["choices"]:
                            if score_text[score] in choice["label"]:
                                if safe_click(choice["element"]):
                                    print(f"เลือกคะแนน {score} สำเร็จ")
                                    time.sleep(0.5)
                                    break
                                else:
                                    print(f"ไม่สามารถเลือกคะแนน {score} ได้")
                        break

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการกรอกคำถามแบบกริด: {e}")

        def fill_radio_question(question):
            try:
                print(f"\nคำถาม: {question['text']}")
                print("\nตัวเลือก:")
                for i, choice in enumerate(question['choices'], 1):
                    print(f"  {i}. {choice['label']}")
                
                while True:
                    choice_input = input(f"\n→ เลือกตัวเลือก (1-{len(question['choices'])}) หรือกด Enter เพื่อข้าม: ").strip()
                    
                    if choice_input == "":
                        print("ข้ามไปข้อถัดไป...")
                        break
                    
                    if choice_input.isdigit():
                        choice_num = int(choice_input)
                        if 1 <= choice_num <= len(question['choices']):
                            selected = question['choices'][choice_num - 1]
                            
                            # คลิกที่ตัวเลือก
                            if safe_click(selected["element"]):
                                print(f"เลือกตัวเลือกที่ {choice_num} สำเร็จ")
                                
                                # ตรวจสอบว่าเป็นตัวเลือก "อื่นๆ" หรือไม่
                                if "อื่น" in selected["label"].lower():
                                    # รอสักครู่เพื่อให้ช่องกรอกข้อความปรากฏ
                                    time.sleep(0.5)
                                    
                                    # ค้นหาช่องกรอกข้อความสำหรับ "อื่นๆ"
                                    other_input = question["element"].query_selector("input[type='text']")
                                    if other_input:
                                        other_text = input("→ กรุณากรอกข้อความสำหรับ 'อื่นๆ': ").strip()
                                        if other_text:
                                            other_input.fill(other_text)
                                            print("กรอกข้อความสำหรับ 'อื่นๆ' สำเร็จ")
                                break
                        else:
                            print(f"กรุณาเลือกตัวเลขระหว่าง 1-{len(question['choices'])}")
                    else:
                        print("กรุณาใส่ตัวเลขเท่านั้น")

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการกรอกคำถามแบบตัวเลือก: {e}")

        def fill_text_question(question):
            try:
                print(f"\nคำถาม: {question['text']}")
                answer = input("→ กรอกคำตอบ หรือกด Enter เพื่อข้าม: ").strip()
                
                if answer:
                    text_input = question["element"].query_selector("input[type='text']")
                    if text_input:
                        text_input.fill(answer)
                        print("กรอกคำตอบสำเร็จ")
                    else:
                        print("ไม่พบช่องกรอกข้อความ")
                else:
                    print("ข้ามไปข้อถัดไป...")

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการกรอกคำถามแบบข้อความ: {e}")

        def fill_question(question):
            try:
                print("-" * 50)
                if question["type"] == "grid":
                    fill_grid_question(question)
                elif question["type"] == "radio":
                    fill_radio_question(question)
                elif question["type"] == "checkbox":
                    fill_checkbox_question(question)
                elif question["type"] == "text":
                    fill_text_question(question)
                print("-" * 50)

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการกรอกคำถาม: {e}")

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
                        print(f"พบปุ่ม {button_selector}")
                        if safe_click(button):
                            print("คลิกปุ่มสำเร็จ")
                            page.wait_for_load_state("networkidle")
                            if button_selector == submit_button_selector:
                                print("ส่งแบบฟอร์มเรียบร้อยแล้ว")
                                return False
                            return True
                
                print("ไม่พบปุ่มที่ต้องการ")
                return False

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการคลิกปุ่ม: {e}")
                return False

        try:
            print(f"\nเริ่มต้นกรอกแบบฟอร์มที่: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            while True:
                questions = get_questions()
                if not questions:
                    print("ไม่พบคำถามในหน้านี้ หรือหน้าฟอร์มโหลดไม่สำเร็จ")
                    break

                for question in questions:
                    fill_question(question)

                if not click_next_or_submit(page):
                    break

        except Exception as e:
            print(f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
        finally:
            print("\nปิดเบราว์เซอร์")
            browser.close()

if __name__ == "__main__":
    fill_google_form()