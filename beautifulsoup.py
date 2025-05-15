import csv, time, random
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL  = "https://m.comic.naver.com/webtoon/weekday"
HEADERS   = {
    "User-Agent": ("Mozilla/5.0 (Linux; Android 10; SM‑G975F) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/122.0 Mobile Safari/537.36")
}
WEEKDAYS  = {
    "mon": "월요일", "tue": "화요일", "wed": "수요일",
    "thu": "목요일", "fri": "금요일", "sat": "토요일", "sun": "일요일"
}

def fetch_day(day_code: str) -> list[dict]:
    """요일별 웹툰 목록을 반환"""
    url  = f"{BASE_URL}?week={day_code}"
    res  = requests.get(url, headers=HEADERS, timeout=5)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select(".section_list_toon .list_item")   # li 태그

    results = []
    for li in items:
        title  = li.select_one(".title").get_text(strip=True)
        link   = li.select_one("a")["href"]
        author = (li.select_one(".author").get_text(strip=True)
                  if li.select_one(".author") else "작자미상")

        results.append({
            "title"     : title,
            "author"    : author,
            "url"       : "https://m.comic.naver.com" + link,
            "weekday"   : WEEKDAYS[day_code],
            "crawl_date": datetime.now().strftime("%Y-%m-%d")
        })
    return results

def main():
    all_rows = []
    for code in WEEKDAYS:
        print(f"[+] {WEEKDAYS[code]} 수집 중 … ", end="")
        rows = fetch_day(code)
        print(f"{len(rows)}개")
        all_rows.extend(rows)
        time.sleep(random.uniform(1, 2))   # polite delay

    if not all_rows:
        print("수집 결과가 없습니다.")
        return

    with open("naver_webtoons_bs4.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"[√] 총 {len(all_rows)}개 웹툰을 naver_webtoons_bs4.csv 에 저장했습니다.")

if __name__ == "__main__":
    main()
