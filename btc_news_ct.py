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
    sec = driver.find_element_by_class_name("post-content")
    texts = sec.find_elements_by_tag_name('p')
    for txt in texts:
        article+=txt.text
    return article




url = 'https://cointelegraph.com/tags/bitcoin'
driver = webdriver.Chrome('../chromedriver.exe')
driver.get(url)
done = True
links = []
titles = []
dates = []
articles = []
base_date = datetime.date(2021, 6, 6)
count = 0
sc = 0
action = ActionChains(driver)
while(done):
    btn = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "posts-listing__more-btn")))
    driver.execute_script("arguments[0].click();", btn)
    elements = driver.find_elements_by_class_name("post-card-inline__content")
    n = len(elements)
    print("clicked ", n)
    time.sleep(30)
    for i in range(count,n):
        e = driver.find_elements_by_class_name("post-card-inline__content")[i]
        print(i)
        anchors = e.find_element_by_tag_name('a')
        link = anchors.get_attribute('href')
        title = anchors.find_element_by_tag_name('span').text
        dt = e.find_element_by_tag_name('time').get_attribute('datetime')
        d = datetime.datetime.strptime(dt, '%Y-%m-%d').date()
        count+=1
        if (d > base_date):
            links.append(link)
            titles.append(title)
            dates.append(dt)
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
for i in range(len(links)):
    try:
        article = getArticle(links[i])
        articles.append(article)
    except:
        print("some error")
        links.pop(i)
        dates.pop(i)

        titles.pop(i)
        continue

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


