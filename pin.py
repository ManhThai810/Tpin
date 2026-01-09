import time
import random
import pyautogui
import pyperclip
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# Tắt failsafe của pyautogui
pyautogui.FAILSAFE = False

# ========== CẤU HÌNH ==========
# Đường dẫn Cốc Cốc
COCCOC_PATH = r"C:\Users\manhd\AppData\Local\CocCoc\Browser\Application\browser.exe"

# Danh sách từ khóa tìm kiếm trên Pinterest
DANH_SACH_TU_KHOA = [
    "biotin hair growth capsules",
    "herbal anti-hair loss tonic",
    "caffeine scalp serum",
    "collagen hair renewal supplement",
    "keratin repair shampoo",
    "essential oil scalp treatment",
    "argan oil conditioner",
    "saw palmetto DHT blocker capsules",
    "pumpkin seed oil softgels",
    "bamboo silica beauty tablets",
    "rosemary scalp spray",
    "ginseng herbal hair serum",
    "herbal hair darkening shampoo",
    "probiotic scalp health capsules",
    "amino acid repair mask",
    "peptide strengthening drops",
    "anti-dandruff herbal lotion",
    "collagen + biotin hair beauty blend",
    "natural thickening spray",
    "nutrient hair gummies",
]

# Từ khóa ban đầu (sẽ được random từ danh sách)
TU_KHOA = random.choice(DANH_SACH_TU_KHOA)

# Nội dung comment (đã bỏ ký tự đặc biệt để tránh lỗi nhập)
NOI_DUNG_GOC = """Hi there, I’m from StrongBody AI — the global online marketplace for wellness and healthcare.
 We connect buyers from around the world with providers and product makers in the health industry.
 Instead of building an expensive website or complex payment system, you can have a ready‑to‑use global storefront for only $15 per month.
You can also post blogs and insights about your expertise or local health knowledge to attract audiences. https://strongbody.ai/become-seller"""

# Số lượng pin cần comment
SO_LAN = 5

# ========== HÀM HỖ TRỢ ==========

def is_driver_alive(driver):
    """Kiểm tra driver còn hoạt động không"""
    try:
        _ = driver.title
        return True
    except:
        return False

def safe_screenshot(driver, filename, pin_url="", output_folder="screenshots"):
    """Chụp ảnh toàn màn hình (bao gồm cả taskbar) với thời gian hiện tại và lưu link pin"""
    try:
        # Tạo folder nếu chưa có
        os.makedirs(output_folder, exist_ok=True)
        
        # Chụp toàn màn hình bằng pyautogui (bao gồm taskbar)
        screenshot = pyautogui.screenshot()
        
        # Thêm thời gian vào ảnh
        draw = ImageDraw.Draw(screenshot)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Thử dùng font Arial, nếu không có thì dùng font mặc định
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        # Vị trí: góc trên bên phải
        text_bbox = draw.textbbox((0, 0), timestamp, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = screenshot.width - text_width - 20
        y = 20
        
        # Vẽ nền đen và chữ vàng cho dễ đọc
        draw.rectangle([x-10, y-5, x+text_width+10, y+text_height+10], fill="black")
        draw.text((x, y), timestamp, fill="yellow", font=font)
        
        # Lưu ảnh vào folder
        image_path = os.path.join(output_folder, filename)
        screenshot.save(image_path)
        print(f"[OK] Đã chụp ảnh: {image_path}")
        
        # Lưu link pin vào file text cùng tên
        if pin_url:
            txt_filename = filename.rsplit('.', 1)[0] + ".txt"
            txt_path = os.path.join(output_folder, txt_filename)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Pin URL: {pin_url}\n")
                f.write(f"Thời gian: {timestamp}\n")
            print(f"[OK] Đã lưu link: {txt_path}")
        
        return True
    except Exception as e:
        print(f"[WARNING] Không thể chụp ảnh: {e}")
    return False

def wait_for_user_login(driver):
    """Đợi người dùng đăng nhập thủ công"""
    print("\n" + "="*60)
    print("   ⚠️  CẦN ĐĂNG NHẬP PINTEREST THỦ CÔNG!")
    print("="*60)
    print("\n[ACTION] Vui lòng đăng nhập Pinterest trong cửa sổ trình duyệt.")
    print("[*] Sau khi đăng nhập xong, nhấn ENTER tại đây để tiếp tục...")
    print("")
    input(">>> Nhấn ENTER khi đã đăng nhập xong: ")
    print("[OK] Tiếp tục script...")
    time.sleep(2)

def find_and_click(driver, selectors, timeout=10, description="element"):
    """Tìm và click element với nhiều selector"""
    for selector in selectors:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            element.click()
            print(f"[OK] Đã click {description}")
            return True
        except:
            continue
    
    # Thử với XPath
    for selector in selectors:
        try:
            element = WebDriverWait(driver, timeout//2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            element.click()
            print(f"[OK] Đã click {description} (XPath)")
            return True
        except:
            continue
    
    print(f"[WARNING] Không tìm thấy {description}")
    return False

def enter_comment(driver, text):
    """Nhập comment vào ô textarea sử dụng clipboard paste"""
    print("[*] Đang tìm ô nhập comment...")
    
    # Các selector có thể là ô comment
    comment_selectors = [
        "textarea[placeholder*='comment']",
        "textarea[placeholder*='Add a comment']",
        "textarea[placeholder*='Thêm nhận xét']",
        "[data-test-id='comment-input'] textarea",
        "[data-test-id='comment-text-field']",
        "div[contenteditable='true']",
        "textarea",
    ]
    
    for selector in comment_selectors:
        try:
            comment_box = driver.find_element(By.CSS_SELECTOR, selector)
            if comment_box.is_displayed():
                # Click vào ô comment
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_box)
                time.sleep(0.3)
                comment_box.click()
                time.sleep(0.5)
                
                # Xóa nội dung cũ nếu có
                comment_box.send_keys(Keys.CONTROL + "a")
                time.sleep(0.1)
                
                # Copy text vào clipboard và paste
                pyperclip.copy(text)
                comment_box.send_keys(Keys.CONTROL + "v")
                time.sleep(0.3)
                
                print("[OK] Đã nhập comment")
                return True
        except:
            continue
    
    # Fallback: Tìm bằng JavaScript và dùng pyautogui paste
    try:
        result = driver.execute_script("""
            var inputs = document.querySelectorAll('textarea, [contenteditable="true"]');
            for (var i = 0; i < inputs.length; i++) {
                if (inputs[i].offsetParent !== null) {
                    inputs[i].focus();
                    inputs[i].click();
                    return 'found';
                }
            }
            return 'not_found';
        """)
        
        if result == 'found':
            time.sleep(0.3)
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            print("[OK] Đã nhập comment (pyautogui)")
            return True
    except:
        pass
    
    # Không tìm thấy ô comment
    print("[WARNING] Không tìm thấy ô nhập comment trong pin này.")
    return False

def click_post_button(driver):
    """Click nút đăng comment"""
    print("[*] Đang tìm nút đăng...")
    
    post_selectors = [
        "button[data-test-id='comment-submit-button']",
        "button[aria-label='Post']",
        "button[aria-label='Đăng']",
        "button[type='submit']",
        "//button[contains(text(), 'Post')]",
        "//button[contains(text(), 'Đăng')]",
        "//button[contains(text(), 'Send')]",
    ]
    
    # Thử click bằng CSS selector
    for selector in post_selectors:
        try:
            if selector.startswith("//"):
                btn = driver.find_element(By.XPATH, selector)
            else:
                btn = driver.find_element(By.CSS_SELECTOR, selector)
            
            if btn.is_displayed() and btn.is_enabled():
                btn.click()
                print("[OK] Đã click nút đăng")
                return True
        except:
            continue
    
    # Fallback: JavaScript tìm và click button
    try:
        result = driver.execute_script("""
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                var text = buttons[i].innerText.toLowerCase();
                if (text.includes('post') || text.includes('đăng') || text.includes('send')) {
                    buttons[i].click();
                    return 'clicked';
                }
            }
            return 'not_found';
        """)
        if result == 'clicked':
            print("[OK] Đã click nút đăng (JavaScript)")
            return True
    except:
        pass
    
    # Không tìm thấy nút đăng
    print("[WARNING] Không tìm thấy nút đăng trong pin này.")
    return False

# ========== HÀM CHÍNH ==========

def get_random_keyword(used_titles):
    """Lấy từ khóa random không trùng với tiêu đề đã dùng"""
    available_keywords = []
    for kw in DANH_SACH_TU_KHOA:
        # Kiểm tra từ khóa không trùng với bất kỳ tiêu đề nào đã dùng
        is_duplicate = False
        for title in used_titles:
            if kw.lower() in title.lower() or title.lower() in kw.lower():
                is_duplicate = True
                break
        if not is_duplicate:
            available_keywords.append(kw)
    
    if available_keywords:
        return random.choice(available_keywords)
    else:
        # Nếu hết từ khóa mới, vẫn random từ danh sách gốc
        return random.choice(DANH_SACH_TU_KHOA)

def run_pinterest_auto(so_lan):
    """Chạy tự động comment trên Pinterest"""
    global TU_KHOA  # Để có thể thay đổi từ khóa trong quá trình chạy
    
    # === TẠO FOLDER OUTPUT ===
    output_folder = os.path.join("screenshots", datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(output_folder, exist_ok=True)
    print(f"\n[INFO] Folder output: {output_folder}")
    
    # === KHỞI TẠO CỐC CỐC ===
    print("\n[STEP 1] Khởi động Cốc Cốc...")
    
    options = Options()
    options.binary_location = COCCOC_PATH
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"[ERROR] Không thể khởi động Cốc Cốc: {e}")
        print("[TIP] Đảm bảo đường dẫn COCCOC_PATH đúng và ChromeDriver phù hợp.")
        return
    
    wait = WebDriverWait(driver, 30)
    
    try:
        # === VÀO PINTEREST ===
        print("\n[STEP 2] Truy cập Pinterest...")
        driver.get("https://www.pinterest.com")
        time.sleep(3)
        
        # Kiểm tra đăng nhập
        try:
            # Nếu thấy nút Login, cần đăng nhập
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[data-test-id='login-button'], [data-test-id='simple-login-button']")
            if login_btn:
                print("[INFO] Chưa đăng nhập Pinterest.")
                wait_for_user_login(driver)
        except:
            print("[OK] Đã đăng nhập Pinterest.")
        
        time.sleep(2)
        
        # === TÌM KIẾM ===
        print(f"\n[STEP 3] Tìm kiếm: {TU_KHOA}")
        search_success = False
        
        # Thử tìm ô search
        search_selectors = [
            "input[name='searchBoxInput']",
            "input[placeholder*='Search']", 
            "input[data-test-id='search-box-input']",
            "input[aria-label*='Search']",
        ]
        
        for selector in search_selectors:
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, selector)
                if search_box.is_displayed():
                    search_box.click()
                    time.sleep(0.5)
                    search_box.clear()
                    search_box.send_keys(TU_KHOA)
                    search_box.send_keys(Keys.ENTER)
                    print(f"[OK] Đã tìm kiếm")
                    search_success = True
                    break
            except:
                continue
        
        if not search_success:
            print("[WARNING] Không tìm được ô search tự động.")
            print(f"[ACTION] Vui lòng TÌM KIẾM '{TU_KHOA}' trong trình duyệt.")
            input(">>> Nhấn ENTER sau khi đã tìm kiếm: ")
        
        time.sleep(5)
        
        # === BỎ QUA PHẦN BẢNG NỔI BẬT ===
        print("\n[*] Scroll xuống để bỏ qua phần bảng nổi bật...")
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(2)
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)
        
        # === LẶP LẠI COMMENT ===
        commented_pins = set()  # Lưu URL các pin đã comment
        commented_titles = set()  # Lưu tiêu đề các pin đã comment (để tránh trùng từ khóa)
        success_count = 0       # Đếm số comment thành công
        pin_index = 0           # Index của pin đang xét
        max_attempts = so_lan * 3  # Giới hạn số lần thử để tránh loop vô hạn
        
        while success_count < so_lan and pin_index < max_attempts:
            print(f"\n{'='*50}")
            print(f"   LẦN COMMENT {success_count+1}/{so_lan} (đang xét pin {pin_index+1})")
            print(f"{'='*50}")
            
            if not is_driver_alive(driver):
                print("[ERROR] Trình duyệt đã đóng!")
                break
            
            try:
                # Lấy danh sách pin hiện tại
                pins = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='pin'], div[data-grid-item], a[href*='/pin/']")
                
                if len(pins) <= pin_index:
                    print(f"[INFO] Hết pin, scroll để tải thêm...")
                    driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(3)
                    pins = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='pin'], div[data-grid-item], a[href*='/pin/']")
                    if len(pins) <= pin_index:
                        print("[WARNING] Không còn pin mới!")
                        break
                
                # Lấy URL của pin để check trùng lặp
                pin_element = pins[pin_index]
                try:
                    pin_url = pin_element.get_attribute("href") or ""
                    # Nếu không có href, thử lấy từ link bên trong
                    if not pin_url:
                        link = pin_element.find_element(By.CSS_SELECTOR, "a[href*='/pin/']")
                        pin_url = link.get_attribute("href") or ""
                except:
                    pin_url = f"pin_{pin_index}"
                
                # Kiểm tra pin đã comment chưa
                if pin_url in commented_pins:
                    print(f"[SKIP] Pin này đã comment rồi, bỏ qua...")
                    pin_index += 1
                    continue
                
                # Click vào pin
                print(f"\n[*] Click vào pin {pin_index+1}...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pin_element)
                time.sleep(0.5)
                pin_element.click()
                print(f"[OK] Đã click pin")
                
                time.sleep(3)  # Đợi pin mở ra
                
                # Lấy tiêu đề pin để hiển thị
                try:
                    pin_title = driver.find_element(By.CSS_SELECTOR, "h1, [data-test-id='pin-title']").text[:100]
                    print(f"[INFO] Tiêu đề: {pin_title[:50]}...")
                except:
                    pin_title = "Unknown"
                
                # Kiểm tra xem đã có comment trùng với NOI_DUNG_GOC trong pin này chưa
                try:
                    # Lấy tất cả comment hiện có trong pin
                    existing_comments = driver.find_elements(By.CSS_SELECTOR, 
                        "[data-test-id='comment-item'], [data-test-id='comment-text'], .commentText, div[class*='comment']")
                    
                    # Lấy một phần nội dung comment gốc để so sánh (bỏ URL và ký tự đặc biệt)
                    check_text = "StrongBody AI"  # Từ khóa đặc trưng trong comment
                    
                    has_duplicate = False
                    for comment_el in existing_comments:
                        try:
                            comment_text = comment_el.text
                            if check_text.lower() in comment_text.lower():
                                has_duplicate = True
                                print(f"[DEBUG] Tìm thấy comment trùng: {comment_text[:50]}...")
                                break
                        except:
                            continue
                    
                    if has_duplicate:
                        print(f"[SKIP] Pin này đã có comment trùng với NOI_DUNG_GOC, bỏ qua...")
                        try:
                            close_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close'], button[aria-label='Đóng'], [data-test-id='closeup-close-button']")
                            close_btn.click()
                        except:
                            driver.back()
                        time.sleep(2)
                        pin_index += 1
                        continue
                except Exception as e:
                    print(f"[DEBUG] Không thể kiểm tra comment trùng: {str(e)[:50]}")
                    # Tiếp tục comment nếu không kiểm tra được
                
                # Nhập comment
                comment_text = NOI_DUNG_GOC
                comment_result = enter_comment(driver, comment_text)
                
                # Nếu không tìm thấy ô comment, bỏ qua pin này và tìm pin khác
                if not comment_result:
                    print("[SKIP] Không có ô comment, chuyển sang pin khác...")
                    try:
                        close_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close'], button[aria-label='Đóng'], [data-test-id='closeup-close-button']")
                        close_btn.click()
                    except:
                        driver.back()
                    time.sleep(2)
                    pin_index += 1
                    continue
                
                time.sleep(1)
                
                # Click nút đăng
                post_result = click_post_button(driver)
                
                # Nếu không tìm thấy nút đăng, bỏ qua pin này và tìm pin khác có cùng chủ đề
                if not post_result:
                    print(f"[SKIP] Không tìm thấy nút đăng, tìm pin khác có cùng chủ đề '{TU_KHOA}'...")
                    try:
                        close_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close'], button[aria-label='Đóng'], [data-test-id='closeup-close-button']")
                        close_btn.click()
                    except:
                        driver.back()
                    time.sleep(2)
                    pin_index += 1
                    continue
                
                time.sleep(6)  # Đợi 6 giây trước khi chụp màn hình
                
                # Lưu pin vào danh sách đã comment
                commented_pins.add(pin_url)
                commented_titles.add(pin_title)  # Lưu tiêu đề để tránh trùng
                success_count += 1
                
                # Chụp ảnh bằng chứng và lưu link pin
                safe_screenshot(driver, f"pinterest_comment_{success_count}.png", pin_url, output_folder)
                
                # === KIỂM TRA CẢNH BÁO ĐỎ (hoạt động đáng ngờ) ===
                try:
                    # Tìm element cảnh báo đỏ ở dưới màn hình
                    red_warning_selectors = [
                        "[class*='error']",
                        "[class*='warning']",
                        "[class*='alert']",
                        "[style*='red']",
                        "[style*='#ff']",
                        "[data-test-id*='error']",
                        "[data-test-id*='warning']",
                        ".Eqh.czT.iyn.Kv5.S9z.QLY.zDA.IZT.swG",  # Pinterest error class
                    ]
                    
                    found_warning = False
                    for selector in red_warning_selectors:
                        try:
                            warnings = driver.find_elements(By.CSS_SELECTOR, selector)
                            for warn in warnings:
                                if warn.is_displayed():
                                    # Kiểm tra có phải màu đỏ không
                                    bg_color = warn.value_of_css_property("background-color")
                                    text_color = warn.value_of_css_property("color")
                                    
                                    # Nếu có màu đỏ (RGB có R cao)
                                    if "255" in bg_color or "red" in bg_color.lower() or \
                                       "255" in text_color or "red" in text_color.lower():
                                        found_warning = True
                                        break
                        except:
                            continue
                        if found_warning:
                            break
                    
                    if found_warning:
                        print("\n" + "!"*60)
                        print("   ⚠️  PHÁT HIỆN CẢNH BÁO ĐỎ - HOẠT ĐỘNG ĐÁNG NGỜ!")
                        print("!"*60)
                        safe_screenshot(driver, f"suspicious_activity_{success_count}.png")
                        print("\n[ACTION] Pinterest phát hiện hoạt động đáng ngờ.")
                        print("[ACTION] Vui lòng:")
                        print("         1. ĐĂNG XUẤT tài khoản hiện tại")
                        print("         2. ĐĂNG NHẬP tài khoản khác")
                        print("         3. Nhấn ENTER để tiếp tục")
                        input("\n>>> Nhấn ENTER sau khi đã đổi tài khoản: ")
                except:
                    pass
                
                print(f"\n[SUCCESS] ✅ Hoàn thành comment lần {success_count}!")
                print(f"[INFO] Đã comment {success_count}/{so_lan} pin khác nhau")
                
                # Đóng pin và quay lại kết quả tìm kiếm
                try:
                    close_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close'], button[aria-label='Đóng'], [data-test-id='closeup-close-button']")
                    close_btn.click()
                except:
                    driver.back()
                
                time.sleep(2)
                
                # === TÌM KIẾM TỪ KHÓA MỚI SAU MỖI LẦN COMMENT THÀNH CÔNG ===
                if success_count < so_lan:
                    TU_KHOA = get_random_keyword(commented_titles)
                    print(f"\n[SEARCH] Tìm kiếm từ khóa mới: {TU_KHOA}")
                    
                    # Tìm và nhập từ khóa mới
                    search_selectors = [
                        "input[name='searchBoxInput']",
                        "input[placeholder*='Search']", 
                        "input[data-test-id='search-box-input']",
                        "input[aria-label*='Search']",
                    ]
                    
                    search_success = False
                    for selector in search_selectors:
                        try:
                            search_box = driver.find_element(By.CSS_SELECTOR, selector)
                            if search_box.is_displayed():
                                search_box.click()
                                time.sleep(0.5)
                                search_box.clear()
                                # Xóa sạch bằng Ctrl+A rồi Delete
                                search_box.send_keys(Keys.CONTROL + "a")
                                search_box.send_keys(Keys.DELETE)
                                time.sleep(0.3)
                                search_box.send_keys(TU_KHOA)
                                search_box.send_keys(Keys.ENTER)
                                print(f"[OK] Đã tìm kiếm từ khóa mới")
                                search_success = True
                                break
                        except:
                            continue
                    
                    if not search_success:
                        # Fallback: navigate to search URL
                        encoded_keyword = TU_KHOA.replace(" ", "%20")
                        driver.get(f"https://www.pinterest.com/search/pins/?q={encoded_keyword}")
                        print(f"[OK] Đã tìm kiếm bằng URL")
                    
                    time.sleep(5)
                    
                    # Scroll xuống để bỏ qua phần bảng nổi bật
                    print("\n[*] Scroll xuống để bỏ qua phần bảng nổi bật...")
                    driver.execute_script("window.scrollBy(0, 800);")
                    time.sleep(2)
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(2)
                    
                    # Reset pin_index vì đã chuyển sang từ khóa mới
                    pin_index = 0
                else:
                    pin_index += 1  # Tiếp tục với pin tiếp theo
                
                # Nghỉ ngẫu nhiên
                if success_count < so_lan:
                    wait_time = random.randint(5, 15)
                    print(f"[*] Nghỉ {wait_time} giây...")
                    time.sleep(wait_time)
                
            except Exception as e:
                print(f"[ERROR] Lỗi: {type(e).__name__}: {str(e)[:100]}")
                safe_screenshot(driver, f"error_pinterest_{pin_index+1}.png")
                
                # Thử quay lại trang tìm kiếm
                try:
                    driver.back()
                    time.sleep(2)
                except:
                    pass
                pin_index += 1  # Tiếp tục với pin tiếp theo
                continue
        
        print("\n" + "="*50)
        print("   🎉 HOÀN THÀNH TẤT CẢ!")
        print("="*50)
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {type(e).__name__}: {e}")
        safe_screenshot(driver, "critical_error.png")
    
    finally:
        print("\n[*] Đóng trình duyệt sau 10 giây...")
        time.sleep(10)
        try:
            driver.quit()
        except:
            pass

# ========== CHẠY SCRIPT ==========
if __name__ == "__main__":
    print("\n" + "="*60)
    print("   🚀 PINTEREST AUTO COMMENT - CỐC CỐC BROWSER")
    print("="*60)
    
    print(f"\n[CONFIG]")
    print(f"  - Trình duyệt: Cốc Cốc")
    print(f"  - Từ khóa: {TU_KHOA}")
    print(f"  - Số pin: {SO_LAN}")
    
    try:
        so_lan = int(input("\n>>> Nhập số pin muốn comment (Enter = mặc định): ") or SO_LAN)
    except:
        so_lan = SO_LAN
    
    run_pinterest_auto(so_lan)
