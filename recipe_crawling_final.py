import requests
from bs4 import BeautifulSoup
import cx_Oracle as ora
from urllib.request import urlopen


def get_recipe_type(url):

    global contents
    headers = {"User-Agent": "Chrome/63.0.3239.132 (Windows NT 6.3; Win64; x64)"}
    # link = "https://www.10000recipe.com/recipe/6842114"

    recipe_type_list = []
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.text, "html.parser")
    divs = soup.find_all("div", class_='col-xs-9')
    content_final = []
    for links in divs:
        link = links.find("img", id="main_thumbs")["src"]

        for i in range(1,30):
            content_1 = links.find_all("div", id="stepdescr"+str(i))
            for i in content_1:
                content_final.append(str(i.text))


        recipe_types = {
            "recipe_link": link,
            "content": content_final
        }
        recipe_type_list.append(recipe_types)
        # print("recipe_types : ", recipe_type_list)

    return recipe_type_list

def get_recipe_link(url):

    headers = {"User-Agent": "Chrome/63.0.3239.132 (Windows NT 6.3; Win64; x64)"}

    # url = "https://www.10000recipe.com/recipe/list.html?order=reco&page=2"

    request = requests.get(url, headers=headers)
    request.raise_for_status()
    soup = BeautifulSoup(request.text, "html.parser")
    list = soup.find_all("li", class_='common_sp_list_li') # 제목 링크

    list_file = []

    for li in list:

        recipe_title = li.find("div", class_="common_sp_caption_tit line2").text
        readcount = li.find("span", class_="common_sp_caption_buyer").text # 레시피 제목

        recipe_image_link = li.select("div.common_sp_thumb > a > img")[0]["src"]

        # print(recipe_image_link)

        recipe_link = li.a.attrs.get("href")

        list_file.append({
            "recipe_title": recipe_title,
            "recipe_link": "https://www.10000recipe.com" + recipe_link,
            "readcount": readcount,
            "recipe_image_link": recipe_image_link
        })

    # print(list_file)
    return list_file


def main_function():
    global content, origin_img, rename_img
    ora.init_oracle_client(lib_dir="./instantclient_21_6")
    pagenum = 2
    result = []
    link_detail = []

    for i in range (1, pagenum):
        print("PAGE NUMBER: ", i)

        link_base = "https://www.10000recipe.com/recipe/list.html?order=reco&page=" + str(pagenum)
        result.append(get_recipe_link(link_base))

    for i in result:
        for j in i:
            try:

                link_detail.append(get_recipe_type(j["recipe_link"]))
                # print(j["recipe_link"])
                title = j["recipe_title"]
                # print("title : ", j["recipe_title"])

                readcount = int((((str(j["readcount"]).replace("조회수", "")).replace("만", "000")).replace(".", "")).replace(",", ""))
                # print(int((((str(j["readcount"]).replace("조회수", "")).replace("만", "000")).replace(".", "")).replace(",", "")))

                rename_img = (str(j["recipe_image_link"]).replace("/", "_")).replace(":","__")

                rename_down = str(j["recipe_image_link"])

                with urlopen(rename_down) as f:
                    with open("./img_file/" + (str(rename_down).replace("/", "_")).replace(":","__"), "wb") as h:
                        img = f.read()
                        h.write(img)

                   # f = open(time.strftime("./recipe_txtfile/recipe_link_%y%b%d.txt"), 'a', newline='\n', encoding="utf-8")
                   # f.write(rename_img)
                   # f.close()

                for i in link_detail:
                    for j in i:
                        origin_img = j["recipe_link"]
                        content = str(j["content"])
                        print(j["recipe_link"])
                        print(j["content"])

                print("==========================================================================")

                conn = ora.connect(user="admin", password="Amjilt39260193", dsn="gtsoojdb_high")
                cursor = conn.cursor()
                cursor.execute('insert into recipe (recipe_num, '
                                                    'recipe_title, '
                                                    'recipe_writer, '
                                                    'recipe_content, '
                                                    'recipe_date, '
                                                    'recipe_original_imgname, '
                                                    'recipe_rename_imgname, '
                                                    'recipe_readcount) values((select max(recipe_num) + 1 from recipe), :2,:3,:4, sysdate, :6, :7, :8)', (title, "admin", content, "(null)", rename_img, readcount))

                cursor.close()
                conn.commit()
                conn.close()




            except Exception as msg:
                print(msg)
                pass

