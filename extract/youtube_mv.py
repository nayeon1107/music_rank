# 유튜브 공식 뮤비 실시간 현황을 수집하는 파일

from config import Config
from mysql import connector
import requests
import time
from datetime import datetime
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
  
def get_youtube_link() :  ## 음악명 - 뮤비영상링크 SELECT
    link_list = run_query("SELECT 음악명, 영상링크 FROM contents_table WHERE 구분='뮤직비디오';")
    return link_list

def get_youtube_mv() :

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(options=options)
    

    # 수집일시
    todaynow = datetime.now().strftime('%Y-%m-%d %H')

    official_mv = get_youtube_link()      # 음악명 : 링크

    for music, url in official_mv :
        driver.get(url)
        time.sleep(5)

        print(f"......{music} 실행 시작 ......")

        # 조회수
        driver.find_element(By.XPATH, '//*[@id="expand"]').click()
        view = driver.find_element(By.XPATH, '//*[@id="info"]/span[1]').text
        view = re.sub(r'[^0-9]', '', view)
        view

        for i in range(5) :
            driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.PAGE_DOWN)

        # 댓글수
        time.sleep(3)
        comment = driver.find_element(By.XPATH, '//*[@id="count"]/yt-formatted-string/span[2]').text
        comment = re.sub(r'[^0-9]', '', comment)

        # 좋아요수
        like = driver.find_element(By.XPATH, '//*[@id="segmented-like-button"]/ytd-toggle-button-renderer/yt-button-shape/button/div[2]/span').text
        like = like.replace("천", "000")
        like = like.replace("만","0000")
        like

        run_query(f'INSERT INTO musicvideo_table VALUES ((SELECT idx FROM contents_table WHERE 영상링크="{url}"), (SELECT 음악명 FROM contents_table WHERE 영상링크="{url}"), (SELECT 영상제목 FROM contents_table WHERE 영상링크="{url}"), "{todaynow}", {view}, {comment}, {like});')


if __name__ == '__main__' :
    get_youtube_mv()