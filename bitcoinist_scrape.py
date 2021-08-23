import datetime as datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def getArticle(url):
    global driver
    driver.get(url)
    article = ""
    sec = driver.find_element_by_class_name("content-inner")
    texts = sec.find_elements_by_tag_name('p')
    for txt in texts:
        try:
            article+=txt.find_element_by_tag_name('span').text
        except:
            continue
    return article



url = 'https://bitcoinist.com/category/bitcoin/'
driver = webdriver.Chrome('../chromedriver.exe')
driver.get(url)

done = True
months = {
    "January": 1,
    "February":2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}
links = []
titles = []
dates = []
articles = []
base_date = datetime.date(2020, 6, 6)
count = 0
sc = 0
action = ActionChains(driver)
while(done):
    #load_more = driver.find_element_by_class_name('jeg_block_loadmore')
    elements = driver.find_elements_by_class_name("jeg_postblock_content")
    n = len(elements)
    print("clicked ", n)
    time.sleep(10)
    for i in range(count,n):
        e = driver.find_elements_by_class_name("jeg_postblock_content")[i]
        print(i)
        top = e.find_element_by_class_name('jeg_post_title').find_element_by_tag_name('a')
        link = top.get_attribute('href')
        title = top.text
        meta = e.find_element_by_class_name('jeg_post_meta').find_element_by_class_name('jeg_meta_date')
        dt_div = meta.find_element_by_tag_name('a').text
        try:
            mnth = months[dt_div[:-9]]
        except:
            mnth = months[dt_div[:-8]]
        yr = int(dt_div[-4:])
        dt = int(dt_div[-8:-6])
        d = datetime.date(yr, mnth, dt)
        print(d, " ",  link, " ", title )
        count+=1
        if (d > base_date):
            links.append(link)
            titles.append(title)
            dates.append(d)
            continue
        else:
            done = False
            break
bitcoin_titles = {
    "Date": dates,
    "Title": titles,
    "Links": links
}
tdf = pd.DataFrame(bitcoin_titles)
tdf.to_csv("bitcoin_titles.csv")
to_remove = []
for i in range(len(links)):
    try:
        article = getArticle(links[i])
        articles.append(article)
    except:
        print("some error ", i)
        to_remove(i)
        continue
tdf.drop(to_remove, inplace=True)
tdf.to_csv("bitcoin_titles.csv")
for j in to_remove:
    del links[j]
    del titles[j]
    del dates[j]
if(len(articles)==len(titles)):
    try:
        bitcoin_news = {
            "Date": dates,
            "Title": titles,
            "Links": links,
            "Articles": articles}
        df = pd.DataFrame(bitcoin_news)
    except:
        bitcoin_news = {"Articles": articles}
        df = pd.DataFrame(bitcoin_news)

df.to_csv("bitcoin_news_coin_telegraph.csv")


