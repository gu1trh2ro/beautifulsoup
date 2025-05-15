import csv, time, random
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# PC 버전 URL로 변경
BASE_URL = "https://comic.naver.com/webtoon/weekday"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/121.0.0.0 Safari/537.36")
}
WEEKDAYS = {
    "mon": "월요일", "tue": "화요일", "wed": "수요일",
    "thu": "목요일", "fri": "금요일", "sat": "토요일", "sun": "일요일"
}

def fetch_day(day_code):
    try:
        url = f"{BASE_URL}#{day_code}"
        res = requests.get(url, headers=HEADERS, timeout=5)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        webtoons = []
        
        # PC 웹툰 페이지 구조에 맞게 선택자 업데이트
        day_selector = f"div#${day_code}"
        day_section = soup.select_one(day_selector)
        
        if day_section:
            for item in day_section.select("ul > li"):
                try:
                    title_element = item.select_one("a.title")
                    if not title_element:
                        continue
                        
                    title = title_element.get_text(strip=True)
                    
                    link = title_element["href"] if title_element.has_attr("href") else ""
                    
                    # 작가 정보
                    author_element = item.select_one(".author")
                    author = author_element.get_text(strip=True) if author_element else "작자미상"

                    webtoons.append({
                        "title"     : title,
                        "author"    : author,
                        "url"       : "https://comic.naver.com" + link if link.startswith("/") else link,
                        "weekday"   : WEEKDAYS[day_code],
                        "crawl_date": datetime.now().strftime("%Y-%m-%d")
                    })
                except Exception as e:
                    print(f"Error parsing webtoon: {e}")
                    continue
        else:
            # 대체 방법: 모든 웹툰 가져와서 요일별로 필터링
            all_webtoons = soup.select(".daily_all > .col > .col_inner")
            for day_block in all_webtoons:
                day_header = day_block.select_one("h4")
                if not day_header:
                    continue
                
                # 현재 요일에 맞는 블록만 처리
                if day_code in WEEKDAYS and WEEKDAYS[day_code] in day_header.text:
                    for item in day_block.select("ul > li"):
                        try:
                            title_element = item.select_one("a.title")
                            if not title_element:
                                continue
                                
                            title = title_element.get_text(strip=True)
                            
                            link = title_element["href"] if title_element.has_attr("href") else ""
                            
                            # 작가 정보
                            author_element = item.select_one(".author")
                            author = author_element.get_text(strip=True) if author_element else "작자미상"

                            webtoons.append({
                                "title"     : title,
                                "author"    : author,
                                "url"       : "https://comic.naver.com" + link if link.startswith("/") else link,
                                "weekday"   : WEEKDAYS[day_code],
                                "crawl_date": datetime.now().strftime("%Y-%m-%d")
                            })
                        except Exception as e:
                            print(f"Error parsing webtoon in day block: {e}")
                            continue
        
        return webtoons
    except Exception as e:
        print(f"Error fetching day {day_code}: {e}")
        return []

def main():
    all_rows = []
    for code in WEEKDAYS:
        print(f"{WEEKDAYS[code]} 수집 중 …", end=" ")
        try:
            rows = fetch_day(code)
            print(f"{len(rows)}개")
            all_rows.extend(rows)
        except Exception as e:
            print(f"오류 발생: {e}")
        time.sleep(random.uniform(1,2))   # polite delay

    if not all_rows:
        print("웹툰을 찾을 수 없습니다. 선택자를 확인해주세요.")
        return

    with open("naver_webtoons_bs4.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"총 {len(all_rows)}개 저장 완료")

if __name__ == "__main__":
    main()
