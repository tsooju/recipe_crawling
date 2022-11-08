# 프로젝트에 필요한 패키지 불러오기
from bs4 import BeautifulSoup as bs
import requests
import cx_Oracle as ora

# 검색할 키워드 입력
keyword = input('검색할 키워드를 입력하세요: ')
print(type(keyword))
# 입력받은 keyword가 포함된 url 주소(레시피) 저장
url = 'https://www.10000recipe.com/recipe/list.html?q='+keyword
# tot_url = []
# requests 패키지를 이용해 'url'의 html 문서 가져오기
response = requests.get(url)
html_text = response.text

# 패키지로 파싱 후, 'soup' 변수에 저장
soup = bs(response.text, 'html.parser')

# 레시피 제목 텍스트 추출
#recipe_titles = soup.select('ul>li>div>a.common_sp_link')
recipe_titles = soup.select('#contents_area_full > ul > ul > li:nth-child(1) > div.common_sp_thumb > a')
# for i in recipe_titles:
#     title = i.get_text()
#     print(title)

ora.init_oracle_client(lib_dir="./instantclient_21_6")

# 레시피 하이퍼링크 추출하고 DB 저장
print("============ 레시피 link 리스트 ============")

for i in recipe_titles:
    href = i.attrs['href']
    print('https://www.10000recipe.com' + href)
