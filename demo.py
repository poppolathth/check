from playwright.sync_api import sync_playwright


def run_form_filler():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # เปิดแบบฟอร์ม
        page.goto("https://forms.gle/7XhH7HpNVgCQ3Neo7", timeout=60000)

        # คลิกปุ่ม "ถัดไป" ถ้ามีหน้า intro
        try:
            next_button = page.locator("text=ถัดไป")
            if next_button.is_visible():
                next_button.click()
        except:
            pass

        # สร้างฟังก์ชันสำหรับการกรอกคำถามตามประเภทต่าง ๆ
        def fill_text_input(question):
            ans = input("ตอบ (Enter เพื่อข้าม): ").strip()
            if ans != "":
                input_box = question.locator("input[type='text']").first
                input_box.scroll_into_view_if_needed()
                input_box.fill(ans)


        def fill_radio():
            labels = page.locator(
                "div[role='listitem'] div[role='radiogroup'] label")
            count = labels.count()
            for i in range(count):
                print(f"{i + 1}. {labels.nth(i).inner_text()}")
            ans = input("เลือก (ตัวเลข / Enter เพื่อข้าม): ").strip()
            if ans != "":
                try:
                    index = int(ans) - 1
                    labels.nth(index).click()
                    if "อื่น" in labels.nth(index).inner_text():
                        other_input = page.locator("input[type='text']").last
                        other_text = input("กรอกคำตอบเพิ่มเติม: ")
                        other_input.fill(other_text)
                except:
                    print("ตัวเลือกไม่ถูกต้อง")

        def fill_checkbox():
            labels = page.locator(
                "div[role='listitem'] div[role='checkboxgroup'] label")
            count = labels.count()
            for i in range(count):
                print(f"{i + 1}. {labels.nth(i).inner_text()}")
            ans = input(
                "เลือก (ใช้ . แบ่ง เช่น 1.3.5 หรือ Enter เพื่อข้าม): ").strip()
            if ans != "":
                indices = [int(x) - 1 for x in ans.split('.')
                           if x.strip().isdigit()]
                for i in indices:
                    labels.nth(i).click()
                    if "อื่น" in labels.nth(i).inner_text():
                        other_input = page.locator("input[type='text']").last
                        other_text = input("กรอกคำตอบเพิ่มเติม: ")
                        other_input.fill(other_text)

        def fill_grid():
            rows = page.locator("div[role='radiogroup']")
            row_count = rows.count()
            print(
                "ตอบแต่ละแถวด้วยตัวเลข (เช่น 1.2.3... ตามจำนวนแถว) หรือ Enter เพื่อข้ามทั้งหมด")
            for i in range(row_count):
                row_label = rows.nth(i).locator(
                    "div[role='heading']").inner_text()
                print(f"{row_label} (1=มากที่สุด ... 5=น้อยที่สุด): ", end="")
                ans = input().strip()
                if ans.isdigit() and 1 <= int(ans) <= 5:
                    radios = rows.nth(i).locator("label")
                    radios.nth(int(ans) - 1).click()

        # ดำเนินการกรอกคำถามตามลำดับหน้า
        while True:
            page.wait_for_selector("form", timeout=10000)

            # ตรวจสอบประเภทคำถาม
            questions = page.locator("div[role='listitem']")
            count = questions.count()

            for i in range(count):
                question_text = questions.nth(i).inner_text()
                print(f"\nคำถาม: {question_text}")

                # ตรวจสอบประเภท
                if questions.nth(i).locator("input[type='text']").count() > 0:
                    fill_text_input(questions.nth(i))
                elif questions.nth(i).locator("div[role='radiogroup']").count() > 0:
                    fill_radio()
                elif questions.nth(i).locator("div[role='checkboxgroup']").count() > 0:
                    fill_checkbox()
                elif questions.nth(i).locator("div[role='radiogroup']").count() > 2:
                    fill_grid()
                else:
                    input("ไม่สามารถระบุประเภทคำถามนี้ได้ กด Enter เพื่อข้าม")

            # คลิกปุ่มถัดไปหรือส่งแบบฟอร์ม
            submit_btn = page.locator('div[role="button"]:has-text("ส่ง")')
            next_btn = page.locator('div[role="button"]:has-text("ถัดไป")')


            # ตรวจสอบว่ามีปุ่มส่ง
            try:
                is_submit_visible = submit_btn.evaluate("el => el.offsetParent !== null")
            except:
                is_submit_visible = False

            if is_submit_visible:
                input("\n>> พร้อมส่งฟอร์มหรือยัง? กด Enter เพื่อส่ง")
                submit_btn.scroll_into_view_if_needed()
                submit_btn.click(force=True)
                print("📨 กำลังส่งแบบฟอร์ม...")
                try:
                    page.wait_for_selector("text=คำตอบของคุณ", timeout=10000)
                    print("✅ ส่งแบบฟอร์มเรียบร้อยแล้ว")
                except:
                    print("⚠️ ไม่พบหน้าขอบคุณ อาจส่งฟอร์มไม่สำเร็จหรือโหลดไม่ทัน")
                break
            elif next_btn.is_visible():
                input("\n>> พร้อมไปหน้าถัดไปหรือยัง? กด Enter เพื่อไปต่อ")
                next_btn.scroll_into_view_if_needed()
                next_btn.click(force=True)
            else:
                print("⚠️ ไม่พบปุ่ม 'ถัดไป' หรือ 'ส่ง' - อาจโหลดไม่สมบูรณ์")




            browser.close()

run_form_filler()
