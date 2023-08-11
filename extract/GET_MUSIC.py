# 발매곡 데이터를 크롤링하여 저장하는 파일

from config import Config
from mysql import connector
import requests
import time
import re
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def run_query(query):
    conn = connector.connect(**Config) 
    with conn.cursor() as cur:
        cur.execute(query)
        rows= cur.fetchall()
    conn.commit()
    conn.close()

    return rows

def get_init_music() :

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(options=options)
    url = 'https://www.komca.or.kr/CTLJSP'
    driver.get(url)
    time.sleep(5)

    # 검색어 입력
    select=Select(driver.find_element(By.NAME,"sel_gubun"))
    select.select_by_value("3")
    driver.find_element(By.ID, 'search').send_keys('뉴진스')
    driver.find_element(By.ID, 'search').send_keys(Keys.ENTER)

    # 검색결과 100개씩 보기
    select=Select(driver.find_element(By.CLASS_NAME,"fr.mt10"))
    select.select_by_value("100")

    # 정보 가져오기
    id = []
    name = []
    date = []
    album = []

    title = driver.find_elements(By.CLASS_NAME, 'tit2')
    for t in title :
        t = t.text
        t = t.replace("[대중]", "")
        t = t.split(" - ")
        id.append(t[1])
        name.append(t[0])

    release = driver.find_elements(By.XPATH, "//p[contains(text(), '공표일자 : ')]")
    for r in release :
        t = r.text
        date.append(t.split(" ")[2])

    program = driver.find_elements(By.XPATH, "//p[contains(text(), '앨범명/프로그램명 : ')]")
    for p in program :
        t = p.text
        t = t.replace("앨범명/프로그램명 : ","")
        album.append(t)

    # run_query('DROP TABLE IF EXISTS music_table ;')    
    conn = connector.connect(**Config)
    cursor = conn.cursor()

    for items in zip(id,name,date,album) :
        cursor.execute(f'INSERT INTO album_table VALUES {items};')
        rows= cursor.fetchall()
    conn.commit()
    conn.close()
    
    return rows

if __name__ == '__main__' :
    get_init_music()