from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Chrome 옵션 설정
chrome_options = Options()
#chrome_options.add_argument('--headless')  # 헤드리스 모드 주석 처리
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')

try:
    # WebDriver 초기화
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 네이버 웹툰 페이지 로드
    print("네이버 웹툰 페이지 로딩 중...")
    driver.get("https://comic.naver.com/webtoon/weekday")
    
    # 페이지 로딩 대기
    time.sleep(5)  # 페이지 로딩을 위한 충분한 시간 제공
    
    # 페이지의 HTML 구조를 확인
    page_source = driver.page_source
    
    # 현재 URL 확인 (리다이렉트 발생 시 확인)
    current_url = driver.current_url
    print(f"현재 URL: {current_url}")
    
    # 요일 섹션 찾기 시도
    try:
        day_sections = driver.find_elements(By.TAG_NAME, "h4")
        print(f"\n찾은 h4 태그 수: {len(day_sections)}")
        for section in day_sections:
            print(f"h4 텍스트: {section.text}")
    except Exception as e:
        print(f"h4 태그 찾기 오류: {e}")
    
    # 다른 주요 요소 찾기 시도
    try:
        webtoon_list = driver.find_elements(By.CSS_SELECTOR, "ul.img_list")
        print(f"\n웹툰 리스트(ul.img_list) 수: {len(webtoon_list)}")
        
        webtoon_items = driver.find_elements(By.CSS_SELECTOR, "li > a.title")
        print(f"\n웹툰 아이템(a.title) 수: {len(webtoon_items)}")
        for i, item in enumerate(webtoon_items[:5]):  # 처음 5개만 출력
            print(f"웹툰 {i+1}: {item.text}")
    except Exception as e:
        print(f"웹툰 리스트 찾기 오류: {e}")
    
    # 페이지 소스의 일부만 출력하여 HTML 구조 파악
    print("\n페이지 소스 일부:")
    print(page_source[:1000])  # 처음 1000자만 출력
    
except Exception as e:
    print(f"오류 발생: {e}")
    
finally:
    # 5초 대기 후 브라우저 종료 (직접 확인을 위해)
    time.sleep(5)
    if 'driver' in locals():
        driver.quit()
        print("브라우저가 종료되었습니다.") 