from woocommerce import API
import requests
from bs4 import BeautifulSoup
import mysql.connector as mysql
import json
from selenium import webdriver

def connectDB():
    HOST = "smarthomeaanbieding.nl"  # or "domain.com"
    DATABASE = "u36593p31915_wp5"
    # this is the user you create
    USER = "u36593p31915"
    # user password
    PASSWORD = "Bastion-14"
    # connect to MySQL server
    db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD)
    print("Connected to:", db_connection.get_server_info())

def createCategory(name):
    category = {"name": name}
    d = wcapi.post("products/categories", category).json()
    try:
        if(d['data']['status']==400):
            return d['data']['resource_id']
    except:
        return d["id"]

def pushProducts(p, catid):

    data = {
            "name": p["name"],
            "external_url": p["url"],
            "regular_price": str(p["price"]),
            "description": p["description"],
            "categories": [
                {
                    "id": catid
                }
            ],
            "images": [
                {
                    "src":p["img"]
                }
            ]
        }
    res = wcapi.post("products", data).json()
    try:
        ids = res["id"]
    except:
        if(res["data"]["status"]==400):
            data = {"name": p["name"],
            "external_url": p["url"],
            "regular_price": str(p["price"]),
            "description": p["description"],
            "categories": [
                {
                    "id": catid
                }
            ]
        }
        print(wcapi.post("products", data).json())

def getProdDet(sec):
    global base
    div_content = sec.find('div', {'class':'product-item__info'})
    a_title = div_content.find('a', {'class': 'product-title'})
    prod_url = base+a_title['href']
    title = a_title.text
    return title, prod_url
def getBrand(sec):
    brand = sec.find('ul', {'class':'product-creator'}).li.a.text
    return brand
def getPrice(sec):
    instock = True
    prices_div = sec.find('div', {'class': 'product-prices'})
    if(prices_div.find('meta') is not None):
        price = float(prices_div.find('meta')['content'])
    else:
        price = 0
        instock = False
    return price, instock
def getRating(sec):
    stars_txt = sec.find('div', {'class':'star-rating'})['title']
    try:
        stars = float(stars_txt[-20: -17].replace(",", "."))
        reviews = float(sec.find('div', {'class':'star-rating'})['data-count'])
    except:
        stars = 0.0
        reviews = 0.0
    return stars, reviews
def getDescription(sec):
    des_more= base + sec.find('p', {'class': 'medium--is-visible'}).a['href']
    driver = webdriver.Chrome('../chromedriver.exe')
    driver.get(des_more)
    btn = driver.find_element_by_class_name('show-more-button')
    driver.execute_script("arguments[0].click();", btn)
    description = driver.find_element_by_class_name('product-description').text
    driver.quit()
    return description
def getImg(sec):
    try:
        img_url = sec.find('a', {'class':'product-image'}).img['src']
    except:
        return ""
    return img_url
def getProducts(url, category):
    global base
    catid = createCategory(category)
    products = list()
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    next = soup.find('a', {'aria-label':'volgende'})
    while(next is not None):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        lists_sec = soup.find_all('li', {'class':'product-item--row'})
        for l in lists_sec:
            prod = {}
            prod["name"], prod["url"] = getProdDet(l)
            prod["brand"] = getBrand(l)
            prod["img"] = getImg(l)
            prod["price"], prod["inStock"] = getPrice(l)
            prod["stars"] , prod["reviews"] = getRating(l)
            prod["description"] = getDescription(l)
            products.append(prod.copy())
            pushProducts(prod.copy(), catid)
        url = base + next['href']
    return products


def parseSubCategories(body, title):
    n = len(body)
    global subcategories
    global base
    subcategories[title] = []

    for i in range(n):
        subcategory = {}
        subcat = body[i]["node"]["title"]
        url = base+body[i]["node"]["url"]
        print(url, " ", title, " ", subcat)
        if(len(getProducts(url, subcat))>0):
            subcategories[title].append(subcat)
            subcategory[subcat]  = getProducts(url, subcat)
        else:
            for c in range(len(body[i]["node"]["children"])):
                subcat = body[i]["node"]["children"][c]["title"]
                url = base+body[i]["node"]["children"][c]["url"]
                subcategory[subcat]  = getProducts(url, subcat)

        print(" subcatogory[subcat] ", subcategory)
        subcategories[title].append(subcategory)
    return subcategories


def getJson():
    urls = ["https://www.bol.com/nl/nl/m/electronics/", "https://www.bol.com/nl/nl/m/alles-voor-de-pc-gamer/"]
    global titles
    for i in range(len(urls)):
        r = requests.get(urls[i])
        soup = BeautifulSoup(r.content, 'html5lib')
        body = json.loads(soup.find('body').text)["content"]['navigation']
        print(titles[i])
        print(parseSubCategories(body, titles[i]), "hlo")


if __name__ == "__main__":
    wcapi = API(
        url="https://smarthomeaanbieding.nl/",
        consumer_key="ck_5da6a69f48620ef67b6e0bb94f544a5a1d3238c7",
        consumer_secret="cs_03bb87a15bee34571acc2e88792c5e2d99a8ee92",
        wp_api=True,
        version="wc/v3",
        query_string_auth=True
    )
    titles = ['Electronika', "Gaming"]
    subcategories = {}
    base = "https://www.bol.com/"
    #connectDB()
    getJson()
# titles - "subcategories - products