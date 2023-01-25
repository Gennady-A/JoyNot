from bs4 import BeautifulSoup
import requests
import time
import aiogram
import os

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


allHeaders = {
    "Referer": "https://joyreactor.cc/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}


def valid_link(link):
    """
        Переменные: 
            link - ссылка, которую нужно проверить.

        Описание: Функция для проверки доступа к ссылке. Если при 
                  подключении возникает ошибка - возвращается False. 
                  В ином случае следует проверка на статус подключения. 
                  Если с подключением всё впорядке - подключаемся. В ином
                  случае выводим номер ошибки и возвращаем False.
        
        Ввод: string

        Вывод: BeautifulSoup
    """
    try:
        url = requests.get(link, headers = allHeaders)
        if url.status_code == 200:
            url.close()
            return True
        else:
            print('Функция "valid_link" ссылка {0} имеет status_code равный'.format(link), url.status_code)
            return False
    except:
        return False

def get_page_bs4(link):
    """
        Переменные: 
            link - ссылка, из которой нужно вытянуть html-документ.

        Описание: Получает ссылку, после по ссылке получает через запрос
                  объект BeautifulSoup.
        
        Ввод: string

        Вывод: BeautifulSoup
    """
    if valid_link(link):
        url = requests.get(link, headers = allHeaders)
        page = BeautifulSoup(url.text, "lxml")
        url.close()
        return page
    else: 
        print('Проблема в функции "get_page_bs4". Ссылка "{0}" невалидна'.format(link))
        return False

def get_lastPostLink_in_tagPage(tagPage):
    """
        Переменные: 
            tagPage - html-документ, в котором нужно найти последний пост.

        Описание: Получает страницу в виде BeautifulSoup элемента.
                  Затем ищет последний пост на странице, собирает ссылку
                  на него и возвращает в удобоваримом виде.
        
        Ввод: BeautifulSoup

        Вывод: string
    """
    if tagPage:
        try:
            post_list = tagPage.find_all("div", class_ = "postContainer")
            last_post_link = post_list[0].find(class_ = "link_wr")
            last_post_link = last_post_link.find("a", class_="link").get("href")
            return 'https://joyreactor.cc' + last_post_link
        except:
            print('Непредвиденная ошибка в функции "get_lastPostLink_in_tagPage"')
            return False
    else:
        return False

def download_Post_full(postLink, dirAdress):
    """
        Переменные: 
            PostLink - ссылка на последний пост; 
            dirAdress - дирректория, в которую нужно загрузить пост;

        Описание: Получает ссылку на последний пост, после чего
                  Выгружает всю информацию о нём в отдельный текстовый 
                  файл, а медиаматериалы в их исходном расширении.
        
        Ввод: string; string;

        Вывод: bool
    """
    # Проверяем ссылку.
    if postLink:
        postPage = get_page_bs4(postLink)
        if postPage:
            pass
        else: 
            return False
    else: 
        return False

    # Пытаемся парсить.
    try:
        if os.path.exists(dirAdress):
            if os.path.isdir(dirAdress):
                postDir = dirAdress+'\\'+(postLink.split('/'))[-1]
                print(postDir)

                # Првоеряем существование папки с постом.
                if os.path.exists(postDir):
                    print("Такой путь уже существует")
                else:
                    os.mkdir(postDir)

                # Выгружаем файлы.
                postContent = postPage.find('div', class_ = 'post_content')
                if len(postContent) == 0:
                    return False
                else: 
                    photoCount = 0
                    divImageList = postContent.find_all('div', class_ = 'image')
                    aList = []
                    for div in divImageList:
                        aList.extend(div.find_all('a'))
                    
                    linkList = [a.get('href') for a in aList]

                    for link in linkList:
                        if (link.split('.'))[-1] in ['jpeg', 'png', 'gif', 'jpg']:
                            photoCount += 1
                            img = requests.get("https:" + link, headers = allHeaders, verify=False)
                            with open("{0}\\{1}.{2}".format(postDir, photoCount, (link.split('.'))[-1]), 'wb') as f:
                                f.write(img.content)

                # Собираем данные о посте.
                tagList = "|-|".join( [i.text for i in ((postPage.find(class_ = "taglist")).find_all("a"))] )
                rating = (postPage.find(class_ = "post_rating")).text
                date = (postPage.find(class_ = "date")).find(class_ = "date").text + " " + (postPage.find(class_ = "date")).find(class_ = "time").text
                downloadDate = time.strftime('%d.%m.%Y %H:%M', time.localtime(time.time()))

                # Записываем данные в файл.
                with open(postDir+'\\info.txt', 'w') as infoFile:
                    infoFile.write('Link: ' + postLink + '\nTags: ' + tagList + '\nRating: ' + rating + '\nPost date: ' + date + '\nDownload date: ' + downloadDate + '\nPhoto count: ' + str(photoCount))

                return True

            else:
                print("Указанный путь существует, но не является директорией. Проверьте правильность пути. Был указан путь {0}".format(dirAdress))
                return False
        else:
            print("Указанный путь несуществует. Проверьте правильность пути. Был указан путь {0}".format(dirAdress))
            return False
    except:
        print('Непредвиденная ошибка в функции "download_Post_full"')
        return False

def getTagName(tagPage):
    """
        Переменные: 
            tagPage - Страница в виде bs-объекта.

        Описание: Получает BeautifulSoup-объект, после чего парсит из него имя раздела. 
        
        Ввод: BeautifulSoup

        Вывод: string
    """
    name = (tagPage.find('div', id='blogName')).find('h1').text
    return name



if __name__ == "__main__":

    print('Тесты:')

    print('----|Функция "valid_link" |')
    print('----|----Тест1. Статус:', '+' if valid_link('https://at.reactor.cc/') else '-')
    print('----|----Тест2. Статус:', '+' if valid_link('https://anime.reactor.cc/tag/Boku+no+Hero+Academia') else '-')
    print('----|----Тест3. Статус:', '+' if valid_link('https://joyreactor.cc/tag/%D0%BC%D0%B8%D0%BB%D0%BE%D1%82%D0%B0') else '-')
    print('----|----Тест4. Статус:', '+' if valid_link('https://joyreactor.cc/tag/%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B') else '-')
    print('----|----Тест5. Статус:', '+' if valid_link('https://wh.reactor.cc/tag/Wh+Other') else '-')
    print('----|----Тест6. Статус:', '+' if not(valid_link('ыпвмвыжь')) else '-')
    print('----|----Тест7. Статус:', '+' if not(valid_link('https://#@UTJGDSK>zxj>.kjzxf.kzfx.,nfzs')) else '-')
    print('----|----Тест8. Статус:', '+' if not(valid_link('www://789iuyghjkjhgbhjkj#@$2hsjl.k/DDS/ds>ds/.!@#@$#%')) else '-')
    print('----|----Тест9. Статус:', '+' if valid_link('https://undertale.reactor.cc') else '-')
    print('----|----Тест10. Статус:', '+' if not(valid_link('https://undertale.reactor.cc/tag')) else '-')
    print('----|----Тест11. Статус:', '+' if valid_link('https://undertale.reactor.cc/post/5434334') else '-')
    print('----|----Тест12. Статус:', '+' if valid_link('https://joyreactor.cc/post/5435888') else '-')
    print('----|----Тест13. Статус:', '+' if valid_link('https://vy.reactor.cc/post/5435538') else '-')
    print('----|----Тест14. Статус:', '+' if valid_link('https://vy.reactor.cc/post/5435935') else '-')
    print('----|----Тест15. Статус:', '+' if not(valid_link('')) else '-')
    print()



    print('----|Функция "get_page_bs4"|')
    print('----|----Тест1. Статус:', '+' if get_page_bs4('https://at.reactor.cc/') else '-')
    print('----|----Тест2. Статус:', '+' if get_page_bs4('https://anime.reactor.cc/tag/Boku+no+Hero+Academia') else '-')
    print('----|----Тест3. Статус:', '+' if get_page_bs4('https://joyreactor.cc/tag/%D0%BC%D0%B8%D0%BB%D0%BE%D1%82%D0%B0') else '-')
    print('----|----Тест4. Статус:', '+' if get_page_bs4('https://joyreactor.cc/tag/%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B') else '-')
    print('----|----Тест5. Статус:', '+' if get_page_bs4('https://wh.reactor.cc/tag/Wh+Other') else '-')
    print('----|----Тест6. Статус:', '+' if get_page_bs4('ыпвмвыжь') == False else '-')
    print('----|----Тест7. Статус:', '+' if get_page_bs4('https://#@UTJGDSK>zxj>.kjzxf.kzfx.,nfzs') == False else '-')
    print('----|----Тест8. Статус:', '+' if get_page_bs4('www://789iuyghjkjhgbhjkj#@$2hsjl.k/DDS/ds>ds/.!@#@$#%') == False else '-')
    print('----|----Тест9. Статус:', '+' if get_page_bs4('https://undertale.reactor.cc') else '-')
    print('----|----Тест10. Статус:', '+' if get_page_bs4('https://undertale.reactor.cc/tag') == False else '-')
    print('----|----Тест11. Статус:', '+' if get_page_bs4('https://undertale.reactor.cc/post/5434334') else '-')
    print('----|----Тест12. Статус:', '+' if get_page_bs4('https://joyreactor.cc/post/5435888') else '-')
    print('----|----Тест13. Статус:', '+' if get_page_bs4('https://vy.reactor.cc/post/5435538') else '-')
    print('----|----Тест14. Статус:', '+' if get_page_bs4('https://vy.reactor.cc/post/5435935') else '-')
    print('----|----Тест15. Статус:', '+' if get_page_bs4('') == False else '-')
    print()



    print('----Функция "get_lastPostLink_in_tagPage"')
    print('----|----Тест1. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://at.reactor.cc/')) else '-')
    print('----|----Тест2. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://anime.reactor.cc/tag/Boku+no+Hero+Academia')) else '-')
    print('----|----Тест3. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://joyreactor.cc/tag/%D0%BC%D0%B8%D0%BB%D0%BE%D1%82%D0%B0')) else '-')
    print('----|----Тест4. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://joyreactor.cc/tag/%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B')) else '-')
    print('----|----Тест5. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://wh.reactor.cc/tag/Wh+Other')) else '-')
    print('----|----Тест6. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('ыпвмвыжь')) == False else '-')
    print('----|----Тест7. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://#@UTJGDSK>zxj>.kjzxf.kzfx.,nfzs')) == False else '-')
    print('----|----Тест8. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('www://789iuyghjkjhgbhjkj#@$2hsjl.k/DDS/ds>ds/.!@#@$#%')) == False else '-')
    print('----|----Тест9. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://undertale.reactor.cc')) else '-')
    print('----|----Тест10. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://undertale.reactor.cc/tag')) == False else '-')
    print('----|----Тест11. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://undertale.reactor.cc/post/5434334')) else '-')
    print('----|----Тест12. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://joyreactor.cc/post/5435888')) else '-')
    print('----|----Тест13. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://vy.reactor.cc/post/5435538')) else '-')
    print('----|----Тест14. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('https://vy.reactor.cc/post/5435935')) else '-')
    print('----|----Тест15. Статус:', '+' if get_lastPostLink_in_tagPage(get_page_bs4('')) == False else '-')
    print()
    


    print('----Функция "download_Post_full"')
    print('----|----Тест1. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://at.reactor.cc/')), 'Logs') else '-')
    print('----|----Тест2. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://anime.reactor.cc/tag/Boku+no+Hero+Academia')), 'Logs') else '-')
    print('----|----Тест3. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://joyreactor.cc/tag/%D0%BC%D0%B8%D0%BB%D0%BE%D1%82%D0%B0')), 'Logs') else '-')
    print('----|----Тест4. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://joyreactor.cc/tag/%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B')), 'Logs') else '-')
    print('----|----Тест5. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://wh.reactor.cc/tag/Wh+Other')), 'Logs') else '-')
    print('----|----Тест6. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('ыпвмвыжь')), 'Logs') == False else '-')
    print('----|----Тест7. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://#@UTJGDSK>zxj>.kjzxf.kzfx.,nfzs')), 'Logs') == False else '-')
    print('----|----Тест8. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('www://789iuyghjkjhgbhjkj#@$2hsjl.k/DDS/ds>ds/.!@#@$#%')), 'Logs') == False else '-')
    print('----|----Тест9. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://undertale.reactor.cc')), 'Logs') else '-')
    print('----|----Тест10. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://undertale.reactor.cc/tag')), 'Logs') == False else '-')
    print('----|----Тест11. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://undertale.reactor.cc/post/5434334')), 'Logs') else '-')
    print('----|----Тест12. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://joyreactor.cc/post/5435888')), 'Logs') else '-')
    print('----|----Тест13. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://vy.reactor.cc/post/5435538')), 'Logs') else '-')
    print('----|----Тест14. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('https://vy.reactor.cc/post/5435935')), 'Logs') else '-')
    print('----|----Тест15. Статус:', '+' if download_Post_full(get_lastPostLink_in_tagPage(get_page_bs4('')), 'Logs') == False else '-')
    print()




# def valid_link(artist_link):
#     """
#         Input: ссылка в виде строки.

#         Output: логическое значение или значение ошибки в виде строки.

#         Функция для проверки доступа к ссылке. Если при подключении возникает
#         ошибка - возвращается False. В ином случае следует проверка на статус 
#         подключения. Если с подключением всё впорядке - подключаемся. В ином 
#         случае выводим номер ошибки.
#     """
#     try:
#         url = requests.get(artist_link, headers = allHeaders, verify=False)
#     except:
#         return False
#     if url.status_code == 200:
#         url.close()
#         return True
#     else:
#         return url.status_code

# def get_page(artist_link):
#     """
#         Input: ссылка в виде строки

#         Output: элемент типа BeautifulSoup или результат функции валидации.

#         Функция для получения страницы. Сначала проверяется ссылка.
#         Если подключения не происходи, возвращаем результат функции валидации.
#         В ином случае получаем код страницы и возвращаем его.
#     """
#     if valid_link(artist_link) == True:
#         url = requests.get(artist_link, headers = allHeaders, verify=False)
#         page = BeautifulSoup(url.text, "lxml")
#         url.close()
#         return page
#     else: 
#         return valid_link(artist_link)

# def last_page_post(page):
#     """
#         Input: страница в виде объекта супа.

#         Output: страница последнего поста в виде объекта супа.

#         Функция для получения последнего поста со страницы. Получаем список всех 
#         постов со страницы. Находим самый новый пост, затем возвращаем ссылку на 
#         него.
#     """
#     post_list = page.find_all("div", class_="postContainer")
#     last_post_link = post_list[0].find(class_ = "link_wr")
#     last_post_link = last_post_link.find("a", class_="link").get("href")
#     return get_page("https://anime.reactor.cc"+last_post_link)

# def last_post_link(page):
#     """
#         Input: страница в виде объекта супа.

#         Output: ссылка на последний пост в виде строки.

#         Функция для получения последнего поста со страницы. Получаем список всех 
#         постов со страницы. Находим самый новый пост, затем возвращаем ссылку на 
#         него.
#     """
#     post_list = page.find_all("div", class_="postContainer")
#     last_post_link = post_list[0].find(class_ = "link_wr")
#     last_post_link = last_post_link.find("a", class_="link").get("href")
#     return "https://anime.reactor.cc" + last_post_link

# def img_in_post(post, adress="Logs\Last_Post\Img\\"):
#     """
#         Input: пост в виде объекта супа.

#         Output: ничего.

#         Функция для выгрузки изображений из поста. 
#     """
#     post = post.find("div", class_ = "post_content")
#     img_list = post.find_all("a", class_ = "prettyPhotoLink")
#     img_link_list = [i.get("href") for i in img_list]
#     for i in range(len(img_link_list)):
#         img = requests.get("https:"+img_link_list[i], headers = allHeaders, verify=False)
#         with open(f"{adress}{str(i)}.jpg", 'wb') as f:
#             f.write(img.content)
