# 시간별 멜론 차트 순위 정보를 크롤링하여 저장하는 파일

from config import Config
from mysql import connector
import requests
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs

def run_query(query):
    conn = connector.connect(**Config) 
    with conn.cursor() as cur:
        cur.execute(query)
        rows= cur.fetchall()
    conn.commit()
    conn.close()

    return rows

def get_melon_chart() :

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.get(url='https://www.melon.com/chart/index.htm')
    time.sleep(5)

    # 수집일시
    today = driver.find_element(By.CLASS_NAME, 'yyyymmdd').text.replace(".","-")
    now = driver.find_element(By.CLASS_NAME, 'hour').text
    todaynow = ' '.join([today,now])

    # 순위
    rank = [num for num in range(1,101)]

    # 음악명
    html = driver.page_source
    soup = bs(html, 'html.parser')
    soup = soup.select('tbody > tr')

    song_list = []

    title = []
    artist = []
    album = []
    likes = []
    rank = [i for i in range(1,101)]

    conn = connector.connect(**Config)
    cursor = conn.cursor()

    for song in soup:
        title.append(song.find('div', class_= 'ellipsis rank01').get_text().replace('\n', ''))
        artist.append(song.find('span', class_= 'checkEllipsis').get_text().replace('\n', ''))
        album.append(song.find('div', class_= 'ellipsis rank03').get_text().replace('\n', ''))
        likes.append(song.find('button', class_ = 'button_etc like').get_text().replace('\n', '').replace('좋아요총건수', '').replace(",",""))

    query = f'INSERT INTO melon_table VALUES '
    for i in range(0,100) :
        query += f'("{todaynow}", {rank[i]}, "{title[i]}", "{artist[i]}", "{album[i]}", {int(likes[i])}), \n'
    query = query[:-3]
    run_query(query)

    # Chrome창 종료    
    driver.quit()

if __name__ == '__main__' :
    get_melon_chart()



