import csv
from datetime import datetime
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class NaverWebtoonCrawler:
    """
    네이버 웹툰 요일별 웹툰 목록을 크롤링하고 CSV로 저장하는 클래스 
    """
    def __init__(self):
        self.base_url = "https://m.comic.naver.com/webtoon/weekday"
        self.user_agent = (
            'Mozilla/5.0 (Linux; Android 10; SM-G975F) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/121.0.0.0 Mobile Safari/537.36'
        )
        self.weekdays = {'mon': '월요일', 'tue': '화요일', 'wed': '수요일', 
                          'thu': '목요일', 'fri': '금요일', 'sat': '토요일', 'sun': '일요일'}

    def crawl_webtoons(self):
        """
        요일별 웹툰 정보를 크롤링하여 리스트로 반환
        """
        all_webtoons = []
        
        # Chrome 옵션 설정 - 모바일 에뮬레이션
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 화면 표시 없이 실행
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'user-agent={self.user_agent}')
        
        # 모바일 기기 에뮬레이션 설정
        mobile_emulation = {
            "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
            "userAgent": self.user_agent
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        try:
            # WebDriver Manager로 Chrome 드라이버 자동 설치 및 관리
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 웹툰 페이지 열기
            print(f"웹툰 페이지 로딩 중... URL: {self.base_url}")
            driver.get(self.base_url)
            
            # 페이지 로딩 대기
            print("페이지 로딩을 위해 5초 대기 중...")
            time.sleep(5)
            
            # 현재 URL 확인
            current_url = driver.current_url
            print(f"현재 URL: {current_url}")
            
            # 각 요일별 크롤링
            for day_code, day_name in self.weekdays.items():
                day_url = f"{self.base_url}?week={day_code}"
                print(f"\n{day_name} 웹툰 수집 중... URL: {day_url}")
                
                # 요일별 페이지 로드
                driver.get(day_url)
                time.sleep(3)  # 페이지 로딩 대기
                
                # 웹툰 목록 찾기
                try:
                    # 모바일 네이버 웹툰의 웹툰 항목 선택자
                    webtoon_items = driver.find_elements(By.CSS_SELECTOR, ".section_list_toon .list_item")
                    print(f"찾은 웹툰 수: {len(webtoon_items)}")
                    
                    if not webtoon_items:
                        # 다른 선택자 시도
                        webtoon_items = driver.find_elements(By.CSS_SELECTOR, ".item")
                        print(f"두 번째 시도 - 찾은 웹툰 수: {len(webtoon_items)}")
                    
                    # 웹툰이 찾아지지 않으면 페이지 소스 일부 출력
                    if not webtoon_items:
                        print("웹툰 항목을 찾을 수 없습니다. 페이지 소스 일부:")
                        print(driver.page_source[:1000])
                        continue
                    
                    # 각 웹툰 정보 추출
                    for item in webtoon_items:
                        try:
                            # 제목 찾기
                            title_elem = item.find_element(By.CSS_SELECTOR, ".title")
                            title = title_elem.text.strip()
                            
                            # URL 찾기
                            link_elem = item.find_element(By.TAG_NAME, "a")
                            url = link_elem.get_attribute("href")
                            
                            # 작가 찾기
                            try:
                                author_elem = item.find_element(By.CSS_SELECTOR, ".author")
                                author = author_elem.text.strip()
                            except:
                                author = "작자미상"
                            
                            # 웹툰 정보 추가
                            all_webtoons.append({
                                'title'     : title,
                                'author'    : author,
                                'url'       : url,
                                'weekday'   : day_name,
                                'crawl_date': datetime.now().strftime('%Y-%m-%d')
                            })
                            print(f"웹툰 추가: {title} - {author} ({day_name})")
                            
                        except Exception as e:
                            print(f"웹툰 정보 추출 중 오류: {e}")
                    
                except Exception as e:
                    print(f"웹툰 목록 찾기 오류: {e}")
                
                # 서버 부하 방지를 위한 랜덤 딜레이
                time.sleep(random.uniform(1.0, 2.0))
            
        except Exception as e:
            print(f"크롤링 중 오류 발생: {e}")
        
        finally:
            # 브라우저 종료
            if 'driver' in locals():
                driver.quit()
        
        print(f"총 {len(all_webtoons)}개 웹툰 정보를 수집했습니다.")
        return all_webtoons

    def save_to_csv(self, webtoons, filename='naver_webtoons.csv'):
        """
        크롤링한 웹툰 정보를 CSV 파일로 저장
        """
        if not webtoons:
            print("저장할 웹툰 정보가 없습니다.")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['title', 'author', 'url', 'weekday', 'crawl_date']
            )
            writer.writeheader()
            writer.writerows(webtoons)

        print(f"웹툰 정보가 '{filename}'에 저장되었습니다.")

def main():
    crawler = NaverWebtoonCrawler()
    webtoons = crawler.crawl_webtoons()
    crawler.save_to_csv(webtoons)

if __name__ == '__main__':
    main()
