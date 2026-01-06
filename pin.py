import time
import random
import pyautogui
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
TU_KHOA = "Herbal hair oil"

# Nội dung comment (đã bỏ ký tự đặc biệt để tránh lỗi nhập)
NOI_DUNG_GOC = """I represent StrongBody AI Provider Shop Platform - a global marketplace system.
You can build your own shop for health and medical products or services today.
International payments, personal profile, and a professional storefront - all for 15 USD per month."""

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
    """Nhập comment vào ô textarea"""
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
                actions = ActionChains(driver)
                actions.move_to_element(comment_box).click().perform()
                time.sleep(0.5)
                
                # Nhập nội dung
                comment_box.clear()
                comment_box.send_keys(text)
                print("[OK] Đã nhập comment")
                return True
        except:
            continue
    
    # Fallback: JavaScript
    try:
        result = driver.execute_script("""
            var text = arguments[0];
            var inputs = document.querySelectorAll('textarea, [contenteditable="true"]');
            for (var i = 0; i < inputs.length; i++) {
                if (inputs[i].offsetParent !== null) {
                    inputs[i].focus();
                    inputs[i].value = text;
                    inputs[i].innerText = text;
                    inputs[i].dispatchEvent(new Event('input', {bubbles: true}));
                    return 'success';
                }
            }
            return 'not_found';
        """, text)
        
        if result == 'success':
            print("[OK] Đã nhập comment (JavaScript)")
            return True
    except:
        pass
    
    # Fallback cuối: Yêu cầu user nhập thủ công
    print("[WARNING] Không thể tự động nhập comment.")
    print(f"[ACTION] Vui lòng nhập nội dung sau vào ô comment:")
    print(f"        \"{text[:80]}...\"")
    input(">>> Nhấn ENTER sau khi đã nhập: ")
    return True

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
        try:
            # Tìm ô search
            search_box = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "input[name='searchBoxInput'], input[placeholder*='Search'], input[data-test-id='search-box-input']"
            )))
            search_box.clear()
            search_box.send_keys(TU_KHOA)
            search_box.send_keys(Keys.ENTER)
            time.sleep(5)
        except Exception as e:
            print(f"[ERROR] Không tìm thấy ô search: {e}")
            safe_screenshot(driver, "error_search.png")
            return
        
        # === LẶP LẠI COMMENT ===
        for i in range(so_lan):
            print(f"\n{'='*50}")
            print(f"   LẦN COMMENT {i+1}/{so_lan}")
            print(f"{'='*50}")
            
            if not is_driver_alive(driver):
                print("[ERROR] Trình duyệt đã đóng!")
                break
            
            try:
                # Click vào pin thứ i+1
                print(f"\n[*] Click vào pin thứ {i+1}...")
                pins = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='pin'], div[data-grid-item], a[href*='/pin/']")
                
                if len(pins) > i:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pins[i])
                    time.sleep(0.5)
                    pins[i].click()
                    print(f"[OK] Đã click pin thứ {i+1}")
                else:
                    print(f"[WARNING] Không đủ pin (chỉ có {len(pins)})")
                    # Scroll xuống để load thêm
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(2)
                    continue
                
                time.sleep(3)  # Đợi pin mở ra
                
                # Nhập comment
                comment_text = f"{NOI_DUNG_GOC} ({random.randint(100, 999)})"
                enter_comment(driver, comment_text)
                time.sleep(1)
                
                # Click nút đăng
                click_post_button(driver)
                time.sleep(2)
                
                # Chụp ảnh bằng chứng
                safe_screenshot(driver, f"pinterest_comment_{i+1}.png")
                
                print(f"\n[SUCCESS] ✅ Hoàn thành comment lần {i+1}!")
                
                # Đóng pin và quay lại kết quả tìm kiếm
                try:
                    close_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close'], button[aria-label='Đóng'], [data-test-id='closeup-close-button']")
                    close_btn.click()
                except:
                    driver.back()
                
                time.sleep(2)
                
                # Nghỉ ngẫu nhiên
                if i < so_lan - 1:
                    wait_time = random.randint(5, 15)
                    print(f"[*] Nghỉ {wait_time} giây...")
                    time.sleep(wait_time)
                
            except Exception as e:
                print(f"[ERROR] Lỗi: {type(e).__name__}: {str(e)[:100]}")
                safe_screenshot(driver, f"error_pinterest_{i+1}.png")
                
                # Thử quay lại trang tìm kiếm
                try:
                    driver.back()
                    time.sleep(2)
                except:
                    pass
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
