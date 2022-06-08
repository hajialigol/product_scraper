from lxml.html import fromstring
from tqdm import tqdm
import requests


# scrape product urls from each url
def scrape_urls(doc, url, out_path):

    # get the elements
    url_eles = doc.xpath('//a[starts-with(@class, "productDescLink")]')

    # case when this works
    try:
        # get all urls
        prod_urls = {ele.attrib['href'] for ele in url_eles}

        # write out the urls
        write_product_urls(prod_urls, out_path, len(prod_urls))

    # for whatever reason, this may not work
    except:

        # just return
        print(f'failed at url: {url}')

# write out product urls
def write_product_urls(urls_set: set, out_path: str, num_products_wrote: int):

    # open the file
    with open(out_path, 'a') as fp:

        # write out the results
        fp.writelines('\n'.join(list(urls_set)))

# runner
if __name__ == "__main__":

    # file location
    input_path = r'../data/macys_product_pages.txt'

    # output path
    out_path = r'../data/macys_products_to_scrape.txt'

    # read data
    data = []
    with open(input_path, 'r') as fp:
        for line in fp.readlines():
            data.append(line.split('\n')[0])
            if len(line.split('https')) > 2:
                data.append('https' + line.split('https')[2].split('\n')[0])

    # headers
    headers = {'User-Agent': 'Mozilla/5.0'}

    # iterate over each url
    for url in tqdm(data):

        # get the page's html
        doc = fromstring(html=requests.get(url, headers=headers).content)

        # scrape the urls
        scrape_urls(doc, url, out_path)
