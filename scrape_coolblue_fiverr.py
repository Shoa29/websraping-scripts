import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time


def getDesBrand(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sec = soup.find('section', {'id':'product-information'})
    des = sec.find('div', {'class':'cms-content'}).p.text
    brand = soup.find('dl', {'data-property-name':'Merk'}).dd.text
    return des , brand
def npages(url):
    """
    Return number of subpages from base url
    """

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    pagination = list()
    for page_number in soup.find('ul', {'class': 'pagination__units'}).find_all('li', {'class': 'pagination__item'}):
        pagination.append(page_number.text.strip())

    return int(pagination[-1])


def get_productinfo(url):
    """
    Scrape product information per webpage
    """
    global base
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    product_list = list()
    product_urls = list()
    product_brands = list()
    product_desc = list()
    price_list = list()
    rating_list = list()
    review_list = list()
    product_imgs = list()


    products = soup.find_all('figure', {'class': 'fitted-product-image-box'})
    if(len(products)==0):
        products = soup.find_all('figure', {'class':'js-product-image'})
    for product in products:
        title = product.img['alt']
        product_imgs.append(product.img['src'])
        product_list.append(title)

    prod_cards = soup.find_all('div', {'class': 'product-card__title'})
    for pc in prod_cards:
        link = base + pc.a['href']
        product_urls.append(link)
        desc, brand = getDesBrand(link)
        product_desc.append(desc)
        product_brands.append(brand)

    prices = soup.find_all('strong', {'class': 'sales-price__current'})
    for price in prices:
        price_list.append(float(price.text.strip().strip(',-').replace('.', '').replace(',', '.')))

    ratings = soup.find_all('div', {'class': 'review-rating__icons'})
    for rating in ratings:
        stars = rating.find('div',{'class':'review-stars'})['aria-label']
        if(stars.find(".",13, 16)!=-1):
            score = stars[13:16]
        else:
            score = stars[13:14]
        rating_list.append(float(score))

    reviews = soup.find_all('span', {'class': 'review-rating__reviews'})
    for review in reviews:
        rev = review.text.split()
        num_of_reviews = rev[0]
        review_list.append(int(num_of_reviews))
    print("printing lengths")
    print(len(product_list))
    print(len(product_urls))
    print(len(product_desc))
    print(len(product_brands))
    print(len(product_imgs))
    print(len(price_list))
    print(len(rating_list))
    print(len(review_list))
    product_data = {
        "product_name": product_list,
        'price': price_list,
        'rating': rating_list,
        'review': review_list,
        'image': product_imgs,
        "product_url": product_urls,
        "product_brand" : product_brands,
        "description": product_desc
    }
    productinfo = pd.DataFrame(product_data)
    return productinfo


def main(url):
    """
    Save scraped product data to file
    """

    df = pd.DataFrame()
    for page in tqdm(range(1, npages(url) + 1), desc='Page'):
        data = get_productinfo(f'{url}?pagina={page}')
        df = pd.concat([df, data])
        print("PAGINATING")

    df['brand'] = df['product'].apply(lambda x: x.strip().split(' ')[0])

    file_name = '../productinfo.csv'
    df.to_csv(file_name, index=False)

    return df
    #print(f'{df.shape[0]} records saved to {file_name}')

def getCategory():
    urls = ["https://www.coolblue.nl/computers-tablets", "https://www.coolblue.nl/beeld-geluid", "https://www.coolblue.nl/telefonie", "https://www.coolblue.nl/gaming", "https://www.coolblue.nl/foto-video"]
    counts = [6, 5, 4, 6, 6]
    dfs = []
    categories = []
    count = 0
    for i in range(len(urls)):
        r = requests.get(urls[i])
        soup = BeautifulSoup(r.text, 'html.parser')
        objs = soup.find_all('div', {'class':'js-swipeable-content-slide'})
        if objs is not None:
            for stuff in objs:
                count+1
                if(count==counts[i]):
                    break
                else:
                    link = stuff.a['href']
                    title = stuff.find('div', {'class':'card__title'}).span.text
                    categories.append(title)
                    navigate = base+link+"/filter"
                    dfs.append(main(navigate))





if __name__ == "__main__":
    base = "https://www.coolblue.nl"
    getCategory()