import requests
from bs4 import BeautifulSoup
import csv
import time
import re

BASE_URL = "https://cse.pusan.ac.kr/cse/14651/subview.do"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
START_PAGE = 1        # 크롤링 시작 페이지
END_PAGE   = 5        # 크롤링 끝 페이지
CSV_FILE   = "pnu_cse_notices.csv"

def clean_text(text):
    """텍스트에서 불필요한 공백과 줄바꿈을 제거합니다."""
    if not text:
        return ""
    # 모든 줄바꿈과 탭을 공백으로 변경
    text = re.sub(r'[\n\t\r]+', ' ', text)
    # 여러 개의 공백을 하나로 변경
    text = re.sub(r'\s+', ' ', text)
    # 양쪽 공백 제거
    return text.strip()

def get_page_params(session):
    """웹페이지에서 필요한 파라미터를 추출합니다."""
    resp = session.get(BASE_URL, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # 페이지 이동에 필요한 기본 파라미터 설정
    params = {"pageIndex": "1"}
    
    # pageForm에서 추가 파라미터 확인
    page_form = soup.find("form", {"name": "pageForm"})
    if page_form:
        print("[*] pageForm 발견")
        for inp in page_form.find_all("input"):
            name = inp.get("name")
            val = inp.get("value", "")
            if name and name != "pageIndex":  # pageIndex는 나중에 설정할 것이므로 제외
                params[name] = val
    
    print(f"[*] 파라미터: {params}")
    return params

def fetch_notice_page(session, params, page):
    """
    pageIndex=page 요청을 보내고, BeautifulSoup 오브젝트를 리턴합니다.
    POST 요청 사용
    """
    data = params.copy()
    data["pageIndex"] = str(page)
    print(f"[*] {page}페이지 요청 파라미터: {data}")
    
    resp = session.post(BASE_URL, data=data, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    
    return BeautifulSoup(resp.text, "html.parser")

def parse_notices(soup):
    """공지사항 정보를 뽑아 dict 리스트로 리턴합니다."""
    notices = []
    
    # artclTable 클래스 테이블을 찾음
    table = soup.find("table", class_="artclTable")
    if not table:
        print("[!] 게시판 테이블을 찾지 못했습니다.")
        return []
    
    # 게시글 행 찾기 (tbody tr)
    rows = table.select("tbody tr")
    if not rows:
        print("[!] 게시글 행을 찾지 못했습니다.")
        return []
    
    print(f"[*] 게시글 행 개수: {len(rows)}")
    
    for row in rows:
        try:
            # td 요소들 추출
            tds = row.find_all("td")
            if len(tds) < 6:  # 테이블은 6개의 열을 가짐
                continue
            
            # 게시글 번호 (첫 번째 열)
            num = clean_text(tds[0].get_text())
            if not num:  # 번호가 없으면 건너뜀
                continue
                
            # 제목 & 링크 (두 번째 열)
            title_td = tds[1]
            a_tag = title_td.find("a")
            if not a_tag:
                continue
                
            # 게시글 카테고리 (있을 경우)
            category = ""
            category_span = title_td.find("span", class_="cate")
            if category_span:
                category = clean_text(category_span.get_text())
                
            # 제목 텍스트
            title_text = clean_text(a_tag.get_text())
            # 카테고리가 제목에 포함되어 있으면 카테고리 정보 추가
            if category and category not in title_text:
                title = f"[{category}] {title_text}"
            else:
                title = title_text
                
            link_href = a_tag.get("href", "")
            
            # 상대 경로인 경우 도메인 추가
            if link_href.startswith("/"):
                full_url = "https://cse.pusan.ac.kr" + link_href
            else:
                full_url = link_href
            
            # 새글 표시 (span.new 또는 이미지로 표시될 수 있음)
            is_new = bool(title_td.find("span", class_="new") or 
                       title_td.find("img", alt="새글") or 
                       title_td.find("span", class_="newArtcl"))
            
            # 작성자 (세 번째 열)
            writer = clean_text(tds[2].get_text()) if len(tds) > 2 else ""
            
            # 작성일 (네 번째 열)
            date = clean_text(tds[3].get_text()) if len(tds) > 3 else ""
            
            # 첨부파일 (다섯 번째 열)
            attach = "0"
            attach_td = tds[4] if len(tds) > 4 else None
            if attach_td:
                if attach_td.find("img"):  # 이미지가 있으면 첨부파일 있음
                    attach = "1"
                else:
                    attach_text = clean_text(attach_td.get_text())
                    attach = attach_text if attach_text else "0"
            
            # 조회수 (여섯 번째 열)
            views = clean_text(tds[5].get_text()) if len(tds) > 5 else "0"
            
            notices.append({
                "num": num,
                "title": title,
                "url": full_url,
                "is_new": is_new,
                "writer": writer,
                "date": date,
                "attach_cnt": attach,
                "views": views,
            })
            
        except Exception as e:
            print(f"[!] 행 파싱 중 오류: {e}")
            continue
    
    return notices

def save_to_csv(all_notices, filename):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "num", "title", "url", "is_new",
            "writer", "date", "attach_cnt", "views"
        ])
        writer.writeheader()
        for notice in all_notices:
            writer.writerow(notice)
    print(f"[+] 총 {len(all_notices)}건을 {filename}에 저장했습니다.")

def main():
    session = requests.Session()
    params = get_page_params(session)

    all_notices = []
    for page in range(START_PAGE, END_PAGE + 1):
        print(f"[*] {page}페이지 크롤링 중…")
        soup = fetch_notice_page(session, params, page)
        notices = parse_notices(soup)
        if not notices:
            print(f"[!] {page}페이지에서 공지사항을 찾지 못했습니다.")
            # 에러가 발생해도 계속 진행
            continue
        all_notices.extend(notices)
        time.sleep(0.5)  # 서버 과부하 방지

    if all_notices:
        save_to_csv(all_notices, CSV_FILE)
        print(f"[+] 크롤링 완료: {len(all_notices)}건의 공지사항을 저장했습니다.")
    else:
        print("[!] 수집된 공지사항이 없습니다.")

if __name__ == "__main__":
    main() 