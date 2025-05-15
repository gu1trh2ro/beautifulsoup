import requests
from bs4 import BeautifulSoup

def save_html():
    BASE_URL = "https://cse.pusan.ac.kr/cse/14651/subview.do"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    
    # 세션 생성 및 GET 요청
    session = requests.Session()
    resp = session.get(BASE_URL, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    
    # HTML 파일로 저장
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
    
    # 간단한 구조 분석
    soup = BeautifulSoup(resp.text, "html.parser")
    
    print(f"페이지 저장 완료: page_source.html")
    
    # 모든 테이블 찾기
    print("\n== 테이블 정보 ==")
    tables = soup.find_all("table")
    print(f"테이블 개수: {len(tables)}")
    for i, table in enumerate(tables):
        print(f"\n테이블 #{i+1}:")
        print(f"  - 클래스: {table.get('class', '없음')}")
        print(f"  - ID: {table.get('id', '없음')}")
        if table.find("thead"):
            thead_cols = len(table.select("thead th"))
            print(f"  - 헤더 열 개수: {thead_cols}")
        if table.find("tbody"):
            tbody_rows = len(table.select("tbody tr"))
            print(f"  - 본문 행 개수: {tbody_rows}")
            if tbody_rows > 0:
                tr = table.select_one("tbody tr")
                td_count = len(tr.find_all("td"))
                print(f"  - 첫 행 열 개수: {td_count}")
                # 첫 행의 클래스 확인
                print(f"  - 첫 행 클래스: {tr.get('class', '없음')}")
    
    # 게시판 관련 요소 찾기
    print("\n== 가능한 게시판 요소 ==")
    article_list_container = None
    
    # 1. 게시판 관련 키워드를 가진 div 찾기
    board_divs = []
    for div in soup.find_all("div"):
        div_class = ' '.join(div.get("class", []))
        div_id = div.get("id", "")
        
        for keyword in ["bbs", "board", "list", "artcl", "article", "notice", "cont"]:
            if (keyword in div_class.lower() or keyword in div_id.lower()):
                board_divs.append(div)
                break
    
    print(f"게시판 관련 div 개수: {len(board_divs)}")
    for i, div in enumerate(board_divs[:5]):  # 처음 5개만 출력
        print(f"\n게시판 관련 div #{i+1}:")
        print(f"  - 클래스: {div.get('class', '없음')}")
        print(f"  - ID: {div.get('id', '없음')}")
        
        # 내부 ul/li 확인
        uls = div.find_all("ul")
        if uls:
            print(f"  - 내부 ul 개수: {len(uls)}")
            for j, ul in enumerate(uls[:2]):  # 처음 2개만 확인
                ul_class = ' '.join(ul.get("class", []))
                ul_id = ul.get("id", "")
                print(f"    * ul #{j+1} - 클래스: {ul_class}, ID: {ul_id}")
                li_count = len(ul.find_all("li"))
                print(f"      li 개수: {li_count}")
        
        # 내부 테이블 확인
        tables = div.find_all("table")
        if tables:
            print(f"  - 내부 테이블 개수: {len(tables)}")
            
        # a 태그 개수 확인 (게시판 항목은 보통 a 태그를 포함)
        a_tags = div.find_all("a")
        if a_tags:
            print(f"  - a 태그 개수: {len(a_tags)}")
            
    # 2. 완전히 일반적인 접근: 페이지에서 모든 테이블이나 목록 확인
    print("\n== 일반적 목록 요소 ==")
    # 1) ul 태그 중 게시판처럼 보이는 것들
    uls = soup.find_all("ul")
    list_ul = []
    for ul in uls:
        li_count = len(ul.find_all("li"))
        if li_count >= 5:  # 게시판은 보통 여러 개의 항목을 가짐
            list_ul.append((ul, li_count))
    
    print(f"5개 이상의 li를 가진 ul 개수: {len(list_ul)}")
    for i, (ul, li_count) in enumerate(list_ul[:3]):  # 처음 3개만 출력
        print(f"\nul #{i+1} (li 개수: {li_count}):")
        print(f"  - 클래스: {ul.get('class', '없음')}")
        print(f"  - ID: {ul.get('id', '없음')}")
        
        # 첫 번째 li 확인
        if li_count > 0:
            li = ul.find("li")
            print(f"  - 첫 번째 li 클래스: {li.get('class', '없음')}")
            # a 태그 확인
            a_tags = li.find_all("a")
            if a_tags:
                print(f"  - a 태그 개수: {len(a_tags)}")
                for j, a in enumerate(a_tags[:2]):
                    print(f"    * a #{j+1} - 텍스트: {a.get_text(strip=True)[:20]}")
    
    # 3. 메인 컨텐츠 영역 찾기
    print("\n== 메인 컨텐츠 영역 ==")
    content_divs = []
    for div in soup.find_all("div"):
        div_class = ' '.join(div.get("class", []))
        div_id = div.get("id", "")
        
        for keyword in ["content", "main", "container", "wrapper", "body"]:
            if (keyword in div_class.lower() or keyword in div_id.lower()):
                content_divs.append(div)
                break
    
    print(f"컨텐츠 관련 div 개수: {len(content_divs)}")
    for i, div in enumerate(content_divs[:3]):  # 처음 3개만 출력
        print(f"\n컨텐츠 div #{i+1}:")
        print(f"  - 클래스: {div.get('class', '없음')}")
        print(f"  - ID: {div.get('id', '없음')}")
        
        # 내부 a 태그 개수
        a_count = len(div.find_all("a"))
        print(f"  - a 태그 개수: {a_count}")

if __name__ == "__main__":
    save_html() 