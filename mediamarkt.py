import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time



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
    #rating_list = list()
    #review_list = list()
    product_imgs = []
    product_links = []
    product_brands = []
    product_desc = []

    div_cont = soup.find_all('div', {'class':'content'})
    for b in div_cont:
        try:
            product_brands.append(b.find('span').img['alt'])
        except:
            continue
    details = soup.find_all('dl', {'class':'product-details'})
    for i in details:
        desc = ""
        for det in i.find_all('dd'):
            desc+=det.text + "| "
        product_desc.append(desc)
        print(desc)
    products = soup.find_all('span', {'class': 'photo clickable'})
    for product in products:
        product_links.append(base+product['data-clickable-href'])
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
                price_list.append(float(pr_text))
    print("printing lengths")
    print(len(product_list))
    print(len(product_imgs))
    print(len(price_list))
    print(len(product_links))
    print(len(product_desc))
    print(len(product_brands))

    product_data = {
        "product_name": product_list,
        'price': price_list,
        'image': product_imgs,
        "product_url": product_links,
        "product_brand": product_brands,
        "description": product_desc
    }
    productinfo = pd.DataFrame(product_data)
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

    #file_name = 'productinfo.csv'
    #df.to_csv(file_name, index=False)
    return df
    #print(f'{df.shape[0]} records saved to {file_name}')

def getCategory():
    urls = ["https://www.mediamarkt.nl/nl/category/_computer-482710.html", "https://www.mediamarkt.nl/nl/category/_beeld-geluid-450681.html", "https://www.mediamarkt.nl/nl/category/_telefonie-navigatie-483192.html", "https://www.mediamarkt.nl/nl/category/_gaming-film-muziek-488118.html", "https://www.mediamarkt.nl/nl/category/_foto-video-483199.html"]
    titles = ["Computers", "TV/MEDIA", "Telephone", "Music/film/games", "Cameras"]
    base = "https://www.mediamarkt.nl"
    dfs = []
    categories = []
    for i in range(len(urls)):
        print(titles[i])
        r = requests.get(urls[i])
        soup = BeautifulSoup(r.text, 'html.parser')
        objs = soup.find_all('li', {'class':'active child-active'})
        if objs is not None:
            for stuff in objs:
                categories.append(stuff.a.text)
                lists = stuff.ul
                links = lists.find_all('a')
                for t in links:
                    link = base + t['href']
                    print(link)
                    dfs.append(main(link))







if __name__ == "__main__":
    getCategory()