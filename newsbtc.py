import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime as datetime
import time

BASE_URL = 'https://www.coolblue.nl/producttype:mobiele-telefoons'


def npages(url):
    """
    Return number of subpages from base url
    """
    base = "https://www.mediamarkt.nl"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    pagination_lists = soup.find('ul', {'class': 'pagination'}).find('li', {'class':'pagination-next'})
    if pagination_lists is None:
        return None
    link = base + pagination_lists.a['href']

    return link


def get_productinfo(url):
    """
    Scrape product information per webpage
    """
    base = "https://www.mediamarkt.nl"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    product_list = list()
    price_list = list()
    rating_list = list()
    review_list = list()
    product_imgs = []
    product_links = []


    products = soup.find_all('a', {'class': 'photo clickable'})
    for product in products:
        product_links.append(base+product['href'])
        title = product.img['alt']
        product_imgs.append(product.img['src'])
        product_list.append(title)

    prices = soup.find_all('div', {'class': 'price-box'})
    for p in prices:
        spans = p.find_all('div', {'class':'price small'})
        for s in spans:
            try:
                pr_text = s.text[:-2]
                price_list.append(float(pr_text))
            except:
                pr_text = s.text.replace(",", ".")
            print(pr_text, " spans for price")


    contents = soup.find_all('div', {'class': 'content'})
    for cont in contents:
        stars = cont.find('a', {'class':'rating'})['class']
        num_of_reviews = cont.find('a', {'class':'clickable see-reviews'}).font.font.text[1:-1]
        rating_list.append(float(stars[14:].replace("-", ".")))
        review_list.append(float(num_of_reviews))
    reviews = soup.find_all('span', {'class': 'review-rating__reviews'})
    print("printing lengths")
    print(len(product_list))
    print(len(product_imgs))
    print(len(price_list))
    print(len(rating_list))
    print(len(review_list))
    productinfo = pd.DataFrame({'product': product_list,
                                'price': price_list,
                                'rating': rating_list,
                                'reviews': review_list,
                                'images': product_imgs,
                                'product_links': product_links
                                })
    return productinfo


def main(url):
    """
    Save scraped product data to file
    """

    df = pd.DataFrame()
    data = get_productinfo(url)
    df = pd.concat([df, data])
    while((npages(url)) is not None):
        url = npages(url)
        data = get_productinfo(url)
        print("PAGINATING ", url)
        df = pd.concat([df, data])

    df['brand'] = df['product'].apply(lambda x: x.strip().split(' ')[0])

    file_name = '../productinfo.csv'
    df.to_csv(file_name, index=False)

    #print(f'{df.shape[0]} records saved to {file_name}')

def getArticleLinks(url):
    global titles
    global articles_urls
    global dates
    base_date = datetime.date(2020, 6, 5)
    months = {
        "Jan" : 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sept": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find_all('div', {'class': 'cnn-search__result-contents'})
    print(soup)
    for res in content:
        title = res.h3.a.text
        link = "https:"+res.h3.a['href']
        date_div = res.div.find('span')[1].text
        mnth = months[date_div[:-9]]
        yr = int(date_div[-4:])
        d = int(date_div[-8:-6])
        dt = datetime.date(yr, mnth, d)
        if (dt > base_date):
            print(link)
            articles_urls.append(link)
            titles.append(title)
            dates.append(dt)
            continue
        else:
            break



if __name__ == "__main__":
    url = "newsbtc.com/news/bitcoin/"
    base = "https://edition.cnn.com/"
    titles = []
    articles_urls = []
    dates = []
    getArticleLinks(url)