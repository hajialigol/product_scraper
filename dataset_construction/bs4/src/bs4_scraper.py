import requests
import logging
import numpy as np
import time
import json
from tqdm import tqdm
from lxml.html import fromstring
from dataset_construction.bestbuy_scraper.src.bs4_classes import ReviewScraper, ThumbnailScraper, OverviewScraper, SpecScraper

# write out product urls
def write_products(product_dict: dict, out_path: str):

    # open the file
    with open(out_path, 'a', encoding="utf-8") as fp:

        # write out the results
        fp.writelines(str(product_dict) + '\n')

# scraper
def bs4_review_scraper(url, out_path):

    # headers
    headers = {'User-Agent': 'Mozilla/5.0'}

    # get the url
    cont = requests.get(url, headers=headers).content

    # get the lxml document
    lxml_doc = fromstring(html=cont)

    # scrape thumbnail pics
    thumbnails = ThumbnailScraper(url=url, doc=lxml_doc, headers=headers)

    # overview class
    overview = OverviewScraper(url=url, doc=lxml_doc, headers=headers)

    # scrape the reviews
    reviews = ReviewScraper(url=url, doc=lxml_doc, headers=headers)

    # make a dictionary of what you want to return
    url_dict = {
        'url': url,
        'thumbnails': thumbnails.thumbnail_list,
        'overview_section': overview.overview_dict,
        'reviews': reviews.reviews_list
    }

    # case when writing out works
    try:
        # write out as text document
        write_products(url_dict, out_path)
    except:
        pass

    # return the dictionary
    return url_dict

# runner
if __name__ == "__main__":

    # input file
    input_path = r'../data/backup_products_to_scrape_05_23.txt'

    # output text path
    output_txt = r'../data/bestbuy_scraped.txt'

    # output path
    output_path = r'../data/bestbuy_scraped.json'

    # list to hold all data
    data = []

    # open the file and read all data
    with open(input_path, 'r') as fp:
        for line in fp.readlines():
            data.append(line.replace('\n', ''))

    # only get the unique data
    data = np.unique(data)

    # create logger
    logging.basicConfig(filename="../logs/bs4.log", level=logging.DEBUG)

    # list to hold results
    scraped_list = []

    # iterate over each url
    for url in tqdm(data):

        # run the scraper
        url_info = bs4_review_scraper(url, output_txt)

        # add scraping results to list
        scraped_list.append(url_info)

    # write to json
    with open(output_path, 'w') as fp:
        json.dump(scraped_list, fp, indent=4)
