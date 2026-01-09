import time
import random
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Tắt failsafe của pyautogui
pyautogui.FAILSAFE = False

# --- CẤU HÌNH ---
TIEU_DE = "Hair growth serum"
NOI_DUNG_GOC = "I represent StrongBody(.AI)  Provider Shop Platform — a global marketplace system.You can build your own shop for health and medical products or services today.International payments, personal profile, and a professional storefront — all for $15/month."

def is_driver_alive(driver):
    """Kiểm tra driver còn hoạt động không"""
    try:
        driver.current_url
        return True
    except:
        return False

def safe_screenshot(driver, filename):
    """Chụp screenshot an toàn"""
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
    print("   ⚠️  CẦN ĐĂNG NHẬP GOOGLE THỦ CÔNG!")
    print("="*60)
    print("\n[ACTION] Vui lòng đăng nhập Google trong cửa sổ Cốc Cốc.")
    print("[*] Sau khi đăng nhập xong, nhấn ENTER tại đây để tiếp tục...")
    print("")
    input(">>> Nhấn ENTER khi đã đăng nhập xong: ")
    print("[OK] Tiếp tục script...")
    time.sleep(2)

def find_and_click(driver, xpaths, timeout=10, description="element"):
    """Tìm và click element với nhiều XPath fallback"""
    for xpath in xpaths:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            if element:
                element.click()
                print(f"[OK] Đã click {description}")
                return True
        except TimeoutException:
            continue
        except Exception as e:
            continue
    return False

def click_5_stars(driver):
    """Click 5 sao bằng nhiều phương pháp, cuối cùng là pyautogui"""
    from selenium.webdriver.common.action_chains import ActionChains
    
    print("[*] Đang tìm và click 5 sao...")
    time.sleep(2)
    
    # Phương pháp 1: Tìm element sao và lấy tọa độ để dùng pyautogui
    try:
        stars = driver.find_elements(By.CSS_SELECTOR, 
            "span[aria-label*='sao'], span[role='img'], button[aria-label*='sao']")
        print(f"[DEBUG] Tìm thấy {len(stars)} elements sao")
        
        if len(stars) >= 5:
            star5 = stars[4]
            # Lấy vị trí element trên màn hình
            location = star5.location
            size = star5.size
            
            # Tính tọa độ trung tâm
            # Cần offset vì Selenium trả về tọa độ relative to viewport
            x = location['x'] + size['width'] / 2
            y = location['y'] + size['height'] / 2
            
            # Scroll element vào view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", star5)
            time.sleep(0.5)
            
            # Dùng ActionChains click trước
            actions = ActionChains(driver)
            actions.move_to_element(star5).click().perform()
            print("[OK] Đã click 5 sao (ActionChains)")
            return True
    except Exception as e:
        print(f"[DEBUG] Method 1 failed: {str(e)[:100]}")
    
    # Phương pháp 2: Dùng pyautogui click theo tọa độ tuyệt đối
    try:
        # Lấy vị trí cửa sổ Chrome
        window_rect = driver.get_window_rect()
        window_x = window_rect['x']
        window_y = window_rect['y']
        
        # Tìm lại element
        stars = driver.find_elements(By.CSS_SELECTOR, 
            "span[aria-label*='sao'], span[role='img'], button[aria-label*='sao']")
        
        if len(stars) >= 5:
            star5 = stars[4]
            location = star5.location
            size = star5.size
            
            # Tính tọa độ absolute trên màn hình
            # Cộng thêm offset cho toolbar của Chrome (~80px)
            abs_x = window_x + location['x'] + size['width'] / 2
            abs_y = window_y + location['y'] + size['height'] / 2 + 80
            
            print(f"[DEBUG] Clicking at ({abs_x}, {abs_y})")
            pyautogui.click(int(abs_x), int(abs_y))
            print("[OK] Đã click 5 sao (pyautogui)")
            return True
    except Exception as e:
        print(f"[DEBUG] PyAutoGUI failed: {str(e)[:100]}")
    
    # Phương pháp 3: JavaScript với MouseEvent
    try:
        result = driver.execute_script("""
            var stars = document.querySelectorAll('[aria-label*="sao"], [aria-label*="star"]');
            if (stars.length >= 5) {
                var star5 = stars[4];
                star5.scrollIntoView({block: 'center'});
                var event = new MouseEvent('click', {
                    view: window, bubbles: true, cancelable: true
                });
                star5.dispatchEvent(event);
                return 'clicked';
            }
            return 'not_found';
        """)
        if result == 'clicked':
            print("[OK] Đã click 5 sao (JavaScript)")
            return True
    except Exception as e:
        print(f"[DEBUG] JS failed: {str(e)[:100]}")
    
    # Fallback: Yêu cầu user click thủ công
    print("[WARNING] Không thể tự động click 5 sao.")
    print("[ACTION] Vui lòng CLICK VÀO NGÔI SAO THỨ 5 trong trình duyệt.")
    input(">>> Nhấn ENTER sau khi đã chọn 5 sao: ")
    return True

def enter_review_text(driver, text):
    """Nhập nội dung đánh giá vào textarea"""
    from selenium.webdriver.common.action_chains import ActionChains
    
    print("[*] Đang tìm và nhập nội dung...")
    time.sleep(1)
    
    # Phương pháp 1: Tìm textarea và dùng Selenium send_keys
    try:
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        print(f"[DEBUG] Tìm thấy {len(textareas)} textarea")
        
        for ta in textareas:
            try:
                if ta.is_displayed() and ta.is_enabled():
                    # Dùng ActionChains để click rồi type
                    actions = ActionChains(driver)
                    actions.move_to_element(ta)
                    actions.click()
                    actions.perform()
                    time.sleep(0.5)
                    
                    ta.clear()
                    ta.send_keys(text)
                    print("[OK] Đã nhập nội dung (Selenium)")
                    return True
            except:
                continue
    except Exception as e:
        print(f"[DEBUG] Method 1 failed: {str(e)[:100]}")
    
    # Phương pháp 2: JavaScript trực tiếp
    try:
        result = driver.execute_script("""
            var text = arguments[0];
            
            // Tìm textarea
            var textareas = document.querySelectorAll('textarea');
            for (var i = 0; i < textareas.length; i++) {
                var ta = textareas[i];
                if (ta.offsetParent !== null) { // Visible
                    ta.scrollIntoView({block: 'center'});
                    ta.focus();
                    ta.value = text;
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    ta.dispatchEvent(new Event('change', { bubbles: true }));
                    return 'textarea_success';
                }
            }
            
            // Tìm contenteditable
            var editables = document.querySelectorAll('[contenteditable="true"]');
            for (var i = 0; i < editables.length; i++) {
                var ed = editables[i];
                if (ed.offsetParent !== null) {
                    ed.scrollIntoView({block: 'center'});
                    ed.focus();
                    ed.innerText = text;
                    ed.dispatchEvent(new Event('input', { bubbles: true }));
                    return 'contenteditable_success';
                }
            }
            
            return 'not_found';
        """, text)
        
        print(f"[DEBUG] JS result: {result}")
        if result and 'success' in result:
            print(f"[OK] Đã nhập nội dung ({result})")
            return True
    except Exception as e:
        print(f"[DEBUG] Method 2 failed: {str(e)[:100]}")
    
    # Phương pháp 3: Dùng keyboard Tab để focus và type
    try:
        from selenium.webdriver.common.keys import Keys
        body = driver.find_element(By.TAG_NAME, "body")
        # Tab nhiều lần để focus vào textarea
        for _ in range(15):
            body.send_keys(Keys.TAB)
            time.sleep(0.1)
        # Gửi text
        body.send_keys(text)
        print("[OK] Đã nhập nội dung (Keyboard)")
        return True
    except Exception as e:
        print(f"[DEBUG] Keyboard method failed: {str(e)[:100]}")
    
    # Fallback: Yêu cầu user nhập thủ công
    print("[WARNING] Không thể tự động nhập nội dung.")
    print(f"[ACTION] Vui lòng NHẬP NỘI DUNG sau vào ô trống:")
    print(f"        \"{text[:80]}...\"")
    input(">>> Nhấn ENTER sau khi đã nhập nội dung: ")
    return True

def run_auto_review(so_lan):
    # === KHỞI TẠO CỐC CỐC ===
    print("\n[STEP 1] Khởi động Cốc Cốc...")
    options = webdriver.ChromeOptions()
    options.binary_location = r"C:\Users\manhd\AppData\Local\CocCoc\Browser\Application\browser.exe"
    options.add_argument(r"--user-data-dir=C:\Users\manhd\AppData\Local\CocCoc\Browser\User Data\SeleniumProfile")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--lang=vi")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"[ERROR] Không thể khởi động Cốc Cốc: {e}")
        return
    
    wait = WebDriverWait(driver, 30)

    try:
        # === VÀO GOOGLE MAPS ===
        print("\n[STEP 2] Truy cập Google Maps...")
        driver.get("https://www.google.com/maps")
        time.sleep(3)
        
        # === TÌM KIẾM ===
        print(f"\n[STEP 3] Tìm kiếm: {TIEU_DE}")
        search_box = wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.clear()
        search_box.send_keys(TIEU_DE)
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)
        
        # === LẶP LẠI ĐÁNH GIÁ ===
        for i in range(so_lan):
            print(f"\n{'='*50}")
            print(f"   LẦN ĐÁNH GIÁ {i+1}/{so_lan}")
            print(f"{'='*50}")
            
            if not is_driver_alive(driver):
                print("[ERROR] Chrome đã đóng!")
                break
            
            try:
                # BƯỚC 1: Click vào kết quả đầu tiên trong danh sách
                print("\n[*] Click vào kết quả tìm kiếm đầu tiên...")
                
                # Dùng JavaScript để tìm và click vào LINK bên trong kết quả
                clicked = driver.execute_script("""
                    // Tìm kết quả đầu tiên
                    var result = document.querySelector('div.Nv2PK');
                    
                    if (result) {
                        // Tìm link bên trong
                        var link = result.querySelector('a');
                        if (link) {
                            link.scrollIntoView({block: 'center'});
                            link.click();
                            return 'link_clicked';
                        }
                        
                        // Nếu không có link, tìm element có jsaction
                        var clickable = result.querySelector('[jsaction]');
                        if (clickable) {
                            clickable.scrollIntoView({block: 'center'});
                            clickable.click();
                            return 'jsaction_clicked';
                        }
                        
                        // Cuối cùng click vào div
                        result.scrollIntoView({block: 'center'});
                        result.click();
                        return 'div_clicked';
                    }
                    
                    // Fallback: tìm link trực tiếp
                    var links = document.querySelectorAll('a[href*="/maps/place"]');
                    if (links.length > 0) {
                        links[0].scrollIntoView({block: 'center'});
                        links[0].click();
                        return 'direct_link_clicked';
                    }
                    
                    return null;
                """)
                
                if clicked:
                    print(f"[OK] Đã click kết quả ({clicked})")
                else:
                    print("[WARNING] Không click được bằng JS, thử Selenium...")
                    # Fallback với Selenium
                    first_result_clicked = find_and_click(driver, [
                        "(//div[contains(@class, 'Nv2PK')]//a)[1]",
                        "(//a[contains(@href, '/maps/place')])[1]",
                        "(//div[@role='article']//a)[1]",
                    ], timeout=5, description="kết quả tìm kiếm")
                
                time.sleep(5)  # Đợi lâu hơn để trang chi tiết load
                
                # BƯỚC 2: Click tab Đánh giá
                print("[*] Tìm tab Đánh giá...")
                review_tab_clicked = find_and_click(driver, [
                    "//button[contains(@aria-label, 'Đánh giá về')]",
                    "//button[contains(@aria-label, 'Reviews for')]",
                    "//button[@data-tab-index='1']",
                    "//button[contains(., 'Đánh giá')]",
                    "//button[contains(., 'Reviews')]"
                ], timeout=10, description="tab Đánh giá")
                
                if not review_tab_clicked:
                    print("[WARNING] Không tìm thấy tab. Thử tiếp tục...")
                time.sleep(3)
                
                # Click nút Viết đánh giá
                print("[*] Tìm nút Viết bài đánh giá...")
                write_btn_clicked = find_and_click(driver, [
                    "//button[contains(., 'Viết bài đánh giá')]",
                    "//button[contains(., 'Write a review')]",
                    "//span[contains(., 'Viết bài đánh giá')]/ancestor::button",
                    "//span[contains(., 'Write a review')]/ancestor::button"
                ], timeout=10, description="nút Viết đánh giá")
                
                if not write_btn_clicked:
                    # Có thể cần đăng nhập
                    print("\n[INFO] Không tìm thấy nút Viết đánh giá.")
                    print("[INFO] Có thể bạn chưa đăng nhập Google.")
                    safe_screenshot(driver, f"need_login_{i+1}.png")
                    wait_for_user_login(driver)
                    # Thử lại sau khi đăng nhập
                    print("[*] Thử lại sau khi đăng nhập...")
                    driver.refresh()
                    time.sleep(3)
                    continue
                
                time.sleep(4)
                
                # Chọn 5 sao
                print("[*] Chọn 5 sao...")
                click_5_stars(driver)
                time.sleep(1)
                
                # Nhập nội dung
                print("[*] Nhập nội dung đánh giá...")
                comment = f"{NOI_DUNG_GOC} ({random.randint(100, 999)})"
                enter_review_text(driver, comment)
                time.sleep(1)
                
                # Click nút ĐĂNG
                print("[*] Click nút Đăng...")
                post_clicked = False
                
                # Thử JavaScript trước
                try:
                    result = driver.execute_script("""
                        // Tìm nút Đăng/Post
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].innerText || '';
                            if (text.includes('Đăng') || text.includes('Post')) {
                                buttons[i].click();
                                return 'clicked_' + text;
                            }
                        }
                        return 'not_found';
                    """)
                    if result and 'clicked' in result:
                        print(f"[OK] Đã click nút Đăng ({result})")
                        post_clicked = True
                except:
                    pass
                
                # Fallback với Selenium
                if not post_clicked:
                    post_clicked = find_and_click(driver, [
                        "//button[contains(., 'Đăng')]",
                        "//button[contains(., 'Post')]",
                        "//button[@aria-label='Đăng']",
                        "//button[@aria-label='Post']",
                    ], timeout=5, description="nút Đăng")
                
                # Nếu vẫn không được, yêu cầu user click thủ công
                if not post_clicked:
                    print("[WARNING] Không thể tự động click nút Đăng.")
                    print("[ACTION] Vui lòng CLICK NÚT ĐĂNG trong trình duyệt.")
                    input(">>> Nhấn ENTER sau khi đã đăng bài: ")
                
                time.sleep(3)  # Đợi đăng xong
                
                # Chụp ảnh bằng chứng SAU KHI ĐĂNG
                safe_screenshot(driver, f"review_posted_{i+1}.png")
                
                print(f"\n[SUCCESS] ✅ Hoàn thành lần {i+1}!")
                
                # Đóng popup để quay lại
                try:
                    driver.find_element(By.XPATH, "//button[@aria-label='Đóng' or @aria-label='Close']").click()
                except:
                    driver.back()
                
                if i < so_lan - 1:
                    wait_time = random.randint(5, 15)
                    print(f"[*] Nghỉ {wait_time} giây...")
                    time.sleep(wait_time)
                
            except Exception as e:
                print(f"[ERROR] Lỗi: {type(e).__name__}")
                safe_screenshot(driver, f"error_{i+1}.png")
                
                # Hỏi người dùng có muốn đăng nhập không
                print("\n[?] Có thể cần đăng nhập. Bạn có muốn đăng nhập thủ công?")
                answer = input(">>> Nhập 'y' để đăng nhập, hoặc nhấn ENTER để bỏ qua: ")
                if answer.lower() == 'y':
                    wait_for_user_login(driver)
                    driver.refresh()
                continue

    except Exception as e:
        print(f"[ERROR] Lỗi nghiêm trọng: {e}")
        safe_screenshot(driver, "fatal_error.png")
    finally:
        print("\n" + "="*50)
        print("   HOÀN TẤT SCRIPT")
        print("="*50)
        if is_driver_alive(driver):
            input("\n>>> Nhấn ENTER để đóng Cốc Cốc: ")
            driver.quit()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("   🚀 GOOGLE MAPS AUTO REVIEW TOOL")
    print("="*50)
    print(f"\n[INFO] Tiêu đề tìm kiếm: {TIEU_DE}")
    print("[INFO] Nếu cần đăng nhập, script sẽ dừng để bạn đăng nhập thủ công.")
    print("")
    
    try:
        so_lan = int(input("Nhập số lần muốn đánh giá: "))
        if so_lan <= 0:
            print("[ERROR] Số lần phải lớn hơn 0")
        else:
            run_auto_review(so_lan)
    except ValueError:
        print("[ERROR] Vui lòng nhập số nguyên hợp lệ")