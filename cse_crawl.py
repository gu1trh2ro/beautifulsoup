import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin

def scrape_pnu_announcements(default_pages=3):
    base_url = "https://cse.pusan.ac.kr/bbs/cse/2605/artclList.do?layout=unknown"
    headers = {"User-Agent": "Mozilla/5.0"}

    announcements = []
    for page_num in range(1, default_pages+1):
        url = f"{base_url}&pageIndex={page_num}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"[!] 페이지 {page_num} 로딩 실패: {resp.status_code}")
            continue

        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table')
        if not table:
            print(f"[!] 테이블을 찾을 수 없음 (페이지 {page_num})")
            continue

        # 2) 각 행에서 데이터 추출
        for row in table.find_all('tr')[9:]:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            article_num = cols[0].get_text(strip=True)
            title = cols[1].get_text(strip=True)
            article_writer = cols[2].get_text(strip=True)
            date = cols[3].get_text(strip=True)
            views = cols[5].get_text(strip=True)

            article_url_tag = cols[1].find('a')
            article_url = "https://cse.pusan.ac.kr"+article_url_tag['href'] if article_url_tag else print("글을 불러올 수 없습니다.")

            download_url = fetch_attachment_download_url(article_url, headers)

            announcements.append({
                'number': article_num,
                'title':  title,
                'author': article_writer,
                'date':   date,
                'views':  views,
                'download_url': download_url
            })

        print(f"[+] 페이지 {page_num} 완료, 누적 {len(announcements)}건")
        time.sleep(0.5)

    return announcements

def fetch_attachment_download_url(article_url, headers):
    if not article_url:
        print(f"[!] url을 찾을 수 없음 (페이지 {article_url})")
        return 
    
    try:
        res = requests.get(article_url, headers=headers)
        if res.status_code != 200:
            print("로딩 실패")
            return
        
        detail_soup = BeautifulSoup(res.text, 'html.parser')

        download_links = []
        # dt.artclLabel 이 '첨부파일'인 곳 아래 dd.artclInsert 안 a 태그 중 download.do만

        dt = detail_soup.find('dt', class_='artclLabel', string='첨부파일')
        if dt:
            dd = dt.find_next_sibling('dd', class_='artclInsert')
            if dd:
                for a in dd.find_all('a', href=True):
                    href = a['href']
                    if 'download.do' in href:
                        download_links.append(urljoin(article_url, href))
            else :
                print("첨부파일이 없습니다")
    except Exception as e:
        print(f"[!] Error fetching download URL from {article_url}: {e}")
        return ""
    
    return download_links



def save_to_csv(data, filename='pnu_announcements.csv'):
    fieldnames = ['number','title', 'author', 'date', 'views','download_url']
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"[+] 총 {len(data)}개의 공지사항을 '{filename}'에 저장했습니다.")

if __name__ == '__main__':
    ann = scrape_pnu_announcements(default_pages=3)
    if ann:
        save_to_csv(ann)
    else:
        print("[!] 크롤링된 공지사항이 없습니다.")
