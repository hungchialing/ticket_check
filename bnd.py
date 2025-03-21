import requests
from bs4 import BeautifulSoup
import time
import sys
from datetime import datetime
import webbrowser
import configparser
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TixCraftMonitor:
    def __init__(self, url, check_interval=60, keyword="立即訂購", use_selenium=True, 
                 min_interval_factor=0.7, max_interval_factor=1.5):
        self.url = url
        self.check_interval = check_interval  # 檢查間隔（秒）
        self.keyword = keyword
        self.use_selenium = use_selenium
        # 新增隨機間隔因子
        self.min_interval_factor = min_interval_factor  # 最小間隔因子
        self.max_interval_factor = max_interval_factor  # 最大間隔因子
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.driver = None
        if use_selenium:
            self.setup_driver()
    
    def setup_driver(self):
        """設置Chrome瀏覽器，啟用無頭模式"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 無頭模式
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Selenium WebDriver 初始化成功")
        except Exception as e:
            print(f"初始化 Selenium WebDriver 失敗: {str(e)}")
            print("將使用 requests + BeautifulSoup 方法")
            self.use_selenium = False
    
    def send_notification(self):
        """發送通知並開啟網頁"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{current_time}] 發現「{self.keyword}」在網頁上！可以購票了：{self.url}"
        
        print(message)
        
        # 自動開啟瀏覽器
        try:
            webbrowser.open(self.url)
            print("已自動開啟購票網頁")
        except Exception as e:
            print(f"開啟瀏覽器時出錯: {e}")
        
        # 提示音效
        try:
            import winsound
            for _ in range(5):  # 連續發出5次提示音
                winsound.Beep(1000, 500)  # 頻率1000Hz，持續500毫秒
                time.sleep(0.3)
        except:
            # 如果不是Windows或沒有winsound，使用ANSI蜂鳴聲
            for _ in range(5):
                print('\a')
                time.sleep(0.5)
    
    def check_website_bs4(self):
        """使用BeautifulSoup檢查網站是否包含關鍵字"""
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 方法1：直接搜尋文本
            if self.keyword in response.text:
                print(f"在網頁文本中找到關鍵字 '{self.keyword}'")
                return True
            
            # 方法2：搜尋按鈕或特定元素
            buy_buttons = soup.find_all(['button', 'a', 'input', 'div'], 
                                      string=lambda text: text and self.keyword in text)
            if buy_buttons:
                print(f"在HTML元素中找到關鍵字 '{self.keyword}'")
                return True
                
            # 方法3：檢查常見的購票按鈕區域
            ticket_area = soup.find('div', {'class': 'buy'}) or soup.find('div', {'id': 'buyTicket'})
            if ticket_area and self.keyword in ticket_area.text:
                print(f"在購票區域找到關鍵字 '{self.keyword}'")
                return True
                
            return False
        except Exception as e:
            print(f"使用 BeautifulSoup 檢查網站時出錯: {e}")
            return False
    
    def check_website_selenium(self):
        """使用Selenium檢查網站是否包含關鍵字"""
        try:
            print(f"正在訪問 {self.url}")
            self.driver.get(self.url)
            
            # 等待頁面加載
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待JavaScript執行完畢
            time.sleep(3)
            
            # 查找按鈕，使用多種方式
            buttons = []
            
            # 1. 查找包含指定文字的按鈕
            buttons.extend(self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{self.keyword}')]"))
            
            # 2. 查找包含指定文字的a標籤
            buttons.extend(self.driver.find_elements(By.XPATH, f"//a[contains(text(), '{self.keyword}')]"))
            
            # 3. 查找包含指定文字的div標籤
            buttons.extend(self.driver.find_elements(By.XPATH, f"//div[contains(text(), '{self.keyword}')]"))
            
            # 4. 查找可能的class或id特徵
            buttons.extend(self.driver.find_elements(By.CSS_SELECTOR, ".btn-buy, .buy-ticket, .ticket-button"))
            
            if buttons:
                print(f"使用Selenium找到'{self.keyword}'按鈕！總共 {len(buttons)} 個")
                return True
            
            # 5. 檢查頁面源碼
            page_source = self.driver.page_source
            if self.keyword in page_source:
                print(f"在頁面源碼中找到關鍵字 '{self.keyword}'")
                return True
            
            return False
            
        except Exception as e:
            print(f"使用 Selenium 檢查網站時出錯: {e}")
            return False
    
    def check_website(self):
        """檢查網站是否包含關鍵字"""
        if self.use_selenium and self.driver:
            return self.check_website_selenium()
        else:
            return self.check_website_bs4()
    
    def get_random_interval(self):
        """獲取隨機間隔時間"""
        # 使用配置的最小和最大間隔因子生成隨機間隔
        factor = random.uniform(self.min_interval_factor, self.max_interval_factor)
        interval = self.check_interval * factor
        
        # 確保間隔不會太短，至少5秒
        return max(5, round(interval))
    
    def start_monitoring(self):
        """開始監控網站"""
        print(f"開始監控 {self.url}")
        print(f"尋找關鍵字: '{self.keyword}'")
        print(f"基本檢查間隔: {self.check_interval} 秒")
        print(f"隨機間隔範圍: {self.check_interval * self.min_interval_factor:.1f} - {self.check_interval * self.max_interval_factor:.1f} 秒")
        print(f"使用 {'Selenium' if self.use_selenium else 'BeautifulSoup'} 分析網頁")
        print("按 Ctrl+C 停止監控")
        print("-" * 50)
        
        try:
            attempts = 1
            while True:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{current_time}] 第 {attempts} 次檢查...")
                
                if self.check_website():
                    self.send_notification()
                    
                    # 發現關鍵字後，詢問用戶是否繼續監控
                    continue_monitoring = input("已發現購票關鍵字！是否繼續監控？(y/n): ").lower()
                    if continue_monitoring != 'y':
                        break
                else:
                    # 獲取隨機間隔時間
                    wait_time = self.get_random_interval()
                    print(f"未找到 '{self.keyword}'，將在 {wait_time} 秒後再次檢查")
                    
                    # 使用隨機間隔時間
                    time.sleep(wait_time)
                attempts += 1
                
        except KeyboardInterrupt:
            print("\n監控已停止")
        finally:
            if self.use_selenium and self.driver:
                self.driver.quit()
                print("Selenium WebDriver 已關閉")


def load_config():
    """從config.ini載入設定"""
    config = configparser.ConfigParser()
    config_path = 'config.ini'
    
    # 如果配置文件不存在，創建默認配置
    if not os.path.exists(config_path):
        config['Monitor'] = {
            'url': 'https://tixcraft.com/activity/game/25_bnd',
            'check_interval': '20',
            'keyword': '立即訂購',
            'use_selenium': 'true',
            'min_interval_factor': '0.7',
            'max_interval_factor': '1.5'
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
            
        print(f"已創建配置文件: {config_path}")
        print("請編輯配置文件後重新啟動程式")
        
        # 等待用戶按下任意鍵
        input("按任意鍵退出...")
        sys.exit(0)
    
    # 讀取配置
    config.read(config_path, encoding='utf-8')
    return config


if __name__ == "__main__":
    try:
        # 載入設定
        config = load_config()
        
        # 監控設定
        url = config['Monitor']['url']
        check_interval = int(config['Monitor']['check_interval'])
        keyword = config['Monitor']['keyword']
        use_selenium = config['Monitor'].getboolean('use_selenium', True)
        
        # 新增隨機間隔因子設定
        min_interval_factor = config['Monitor'].getfloat('min_interval_factor', 0.7)
        max_interval_factor = config['Monitor'].getfloat('max_interval_factor', 1.5)
        
        # 啟動監控
        monitor = TixCraftMonitor(url, check_interval, keyword, use_selenium, 
                                min_interval_factor, max_interval_factor)
        monitor.start_monitoring()
        
    except Exception as e:
        print(f"程式執行時發生錯誤: {e}")
        input("按任意鍵退出...")