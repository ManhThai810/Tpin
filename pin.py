import time
import random
import pyautogui
import pyperclip
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

# Từ khóa tìm kiếm trên Pinterest
TU_KHOA = "Anti-hair fall shampoo"

# Nội dung comment (đã bỏ ký tự đặc biệt để tránh lỗi nhập)
NOI_DUNG_GOC = """Hello, I’m from StrongBody(.AI), the Product Shop BD team.
Are you a professional or vendor in the health or medical field?
Now you can launch your global shop instantly – no developers, no web design.
Everything’s ready. Just $15/month to start selling worldwide.
https://strongbody.ai/become-seller
"""

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

def safe_screenshot(driver, filename):
    """Chụp ảnh an toàn"""
    try:
        if is_driver_alive(driver):
            driver.save_screenshot(filename)
            print(f"[OK] Đã chụp ảnh: {filename}")
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
    
    # Fallback: Yêu cầu user
    print("[WARNING] Không tìm thấy nút đăng.")
    print("[ACTION] Vui lòng CLICK NÚT ĐĂNG trong trình duyệt.")
    input(">>> Nhấn ENTER sau khi đã đăng: ")
    return True

# ========== HÀM CHÍNH ==========

def run_pinterest_auto(so_lan):
    """Chạy tự động comment trên Pinterest"""
    
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
                    pin_title = driver.find_element(By.CSS_SELECTOR, "h1, [data-test-id='pin-title']").text[:50]
                    print(f"[INFO] Tiêu đề: {pin_title}...")
                except:
                    pin_title = "Unknown"
                
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
                click_post_button(driver)
                time.sleep(6)  # Đợi 6 giây trước khi chụp màn hình
                
                # Lưu pin vào danh sách đã comment
                commented_pins.add(pin_url)
                success_count += 1
                
                # Chụp ảnh bằng chứng
                safe_screenshot(driver, f"pinterest_comment_{success_count}.png")
                
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
