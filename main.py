import re
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import numpy as np

# selenium import
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

options = webdriver.ChromeOptions()
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument('--no-sandbox')
options.add_argument('headless')

service = Service()
driver = webdriver.Chrome(service=service, options=options)
driver.get('https://www.melon.com/genre/song_list.htm?gnrCode=GN1500&dtlGnrCode=GN1507')
driver.implicitly_wait(10)

time.sleep(0.01)

pages = 14
page = 1

titleData = []
actorData = []
albumData = []
lyricsData = []

a = 2

while True:
    print(f'{page} 페이지 작업 중')

    htmlSource = driver.page_source
    soup = BeautifulSoup(htmlSource, "html.parser")

    for tr in soup.select('table > tbody > tr'):
        titleElement = tr.select_one('div.ellipsis.rank01 > span > a')
        actorElement = tr.select_one('div.ellipsis.rank02 > a')
        albumElement = tr.select_one('div.ellipsis.rank03 > a')

        title = titleElement.text.strip() if titleElement else "No title available"
        actor = actorElement.text.strip() if actorElement else "No actor available"
        album = albumElement.text.strip() if albumElement else "No album available"

        titleData.append(title)
        actorData.append(actor)
        albumData.append(album)

    for i in range(1, len(soup.select('table > tbody > tr')) + 1):  
        try:
            lyricsSelector = f'#frm > div > table > tbody > tr:nth-child({i}) > td:nth-child(4) > div > a'
            lyricsLink = driver.find_element(By.CSS_SELECTOR, lyricsSelector)
            lyricsLink.click()

            try:
                lyrics_button = WebDriverWait(driver, 1.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#lyricArea > button'))
                )
                lyrics_button.click()
            except TimeoutException:
                print("없다")
                lyrics = "No lyrics available"
            else:
                lyrics = driver.find_element(By.CSS_SELECTOR, '#d_video_summary').text

            lyricsData.append(lyrics)

            driver.back()
            time.sleep(0.3)  

        except NoSuchElementException as e:
            print(f"Element not found for song {i}: {e}")
            driver.back()
            time.sleep(0.1)
            continue
    
    break
    cssPageSelector = ''

    if a == 11:
        cssPageSelector = '#pageObjNavgation > div > a'
        a = 2
    else:
        cssPageSelector = f'#pageObjNavgation > div > span > a:nth-child({a})'
        a = a + 1
    
    if page ==  pages:
        break
    else:
        page = page + 1

    nextPage = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, cssPageSelector))
        )
    
    driver.execute_script("arguments[0].scrollIntoView(true);", nextPage)
    driver.execute_script("arguments[0].click();", nextPage)


df = pd.DataFrame({'넘버 제목': titleData, '배우': actorData, '앨범': albumData, '가사': lyricsData})

df.to_csv("뮤지컬 넘버 데이터_2.csv",encoding='utf-8-sig',index=False)



