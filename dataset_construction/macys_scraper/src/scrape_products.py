import requests
import json
from tqdm import tqdm
from lxml.html import fromstring


# function to get the brand and product title
def get_brand_prod_title(doc):
    # get the brand
    brand_ele = doc.xpath('//a[contains(@data-auto, "product-brand")]')

    # if the brand title wasn't found, set the brand title to an empty string
    if len(brand_ele) == 0:

        # make the brand an empty string
        brand = "N/A"

    # otherwise, get the string
    else:

        try:
            # get string
            brand = brand_ele[0].text_content().strip()
        except:
            brand = 'N/A'

    # get the title
    title_ele = doc.xpath('//div[contains(@class, "product-title")]')

    # if the title wasn't found, set the brand title to an empty string
    if len(title_ele) == 0:

        # make the title an empty string
        title = "N/A"

    # otherwise, get the string
    else:
        try:
            # get string
            title = title_ele[0].text_content().strip()
        except:
            title = 'N/A'

    # return a tuple of the brand and title
    return (brand, title)


# function to get the product description
def get_prod_description(doc):
    # get the path to the product description
    prod_desc_ele = doc.xpath('//p[contains(@itemprop, "description")]')

    # if empty, then return empty list
    if len(prod_desc_ele) == 0:

        # set to empty string
        paragraph_info = 'N/A'

    # otherwise, get the content
    else:
        try:

            # set content equal to the paragraph_info var
            paragraph_info = prod_desc_ele[0].text_content().strip()
        except:
            paragraph_info = 'N/A'

    # get the path to the product bullet list
    bullet_ele = doc.xpath('//ul[contains(@data-auto, "product-description-bullets")]')

    # if empty, then return empty list
    if len(bullet_ele) == 0:

        # set to empty string
        bullet_info = 'N/A'

    # otherwise, get the content
    else:

        try:
            # set content equal to the paragraph_info var
            nested_bullets = bullet_ele[0].xpath('.//li')

            # get the text
            bullet_info = [ele.text_content().strip() for ele in nested_bullets]

        except:
            bullet_info = 'N/A'

    # return the information
    return {
        "paragraph": paragraph_info,
        "bullets": bullet_info
    }

# function to get the thumbnails
def get_thumbnails(doc):
    # define thumbnail list
    thumbnail_urls = []

    # element that has the thumbnails
    thumbnail_eles = doc.xpath('//picture[contains(@class, "main-picture")]')

    # in the event this does work
    try:

        # get the thumbnails
        for ele in thumbnail_eles:

            # get all corresponding nested thumbnail elements
            nested_thumbnail_img = ele.xpath('.//img')[0].attrib['src']

            # get all the thumbnail links
            if nested_thumbnail_img not in thumbnail_urls:
                thumbnail_urls.append(nested_thumbnail_img)

    # case when it doesn't
    except:

        # set to an empty list
        return thumbnail_urls

    # return the thumbnails
    return thumbnail_urls

# function to get related products
def get_related_products(doc):
    # elements that represent related products
    related_eles = doc.xpath('//div[contains(@class, "productThumbnail")]')

    # case when this doesn't work
    if len(related_eles) == 0:

        # return an empty list
        return []

    # otherwise, get all the images
    else:

        # get all images
        try:
            return ["https://www.macys.com" + ele.xpath('./*')[0].attrib["href"]
                for ele in related_eles]
        except:
            return []

# get the product price
def get_price(doc):
    # try to see if there's a sale price
    sale_price_ele = doc.xpath('//div[contains(@class, "lowest-sale-price")]')

    # if the length is not 0, then this is the price you want to return
    if len(sale_price_ele) > 0:
        try:
            return float(sale_price_ele[0].xpath('./*')[0].text_content().strip().replace('$','').replace(',', ''))
        except:
            return -1

    # otherwise, return nothing
    else:
        return -1

# get customer reviews
def get_reviews(doc):

    # go to the pagination element
    pagination_ele = doc.xpath('//ul[contains(@class, "pagination text-center")]')

    # if this is empty, then that should mean there aren't any reviews
    if len(pagination_ele) == 0:
        return []

    # otherwise, get the number of pages
    num_review_pages = pagination_ele[0].text_content()



# function to scrape a product page
def scrape_product(doc, url):
    # get the thumbnails
    thumbnails = get_thumbnails(doc)

    # get the brand and product title
    brand, title = get_brand_prod_title(doc)

    # get the product description
    prod_desc = get_prod_description(doc)

    # get the price
    price = get_price(doc)

    # get related items
    # related_items = get_related_products(doc)

    # get the reviews
    reviews = get_reviews(doc)

    # return the scraped data
    return {
        'product_name': title,
        'brand': brand,
        'price': price,
        'description': prod_desc,
        'thumbnails': thumbnails
    }


# runner
if __name__ == "__main__":

    # input file
    input_path = r'../data/test.txt'

    # headers
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
                             ' (KHTML, like Gecko) Version/15.3 Safari/605.1.15'}

    # output path
    output_path = r'../data/macys_scraped.json'

    # read in the data
    with open(input_path, 'r') as fp:
        data = ["https://www.macys.com" + line.split('\n')[0] for line in fp.readlines()]

    # list to hold all scraped urls
    scraped_list = []

    # iterate over each url
    for url in tqdm(data):

        # in the case when this works
        try:

            # get the html for the site
            doc = fromstring(requests.get(url, headers=headers).content)

        # sometimes it won't work
        except:

            # if it doesn't, just move on
            continue

        # scrape the urls
        scraped_data = scrape_product(doc, url)

        # add to list
        scraped_list.append(scraped_data)

    # write to json
    with open(output_path, 'w') as fp:
        json.dump(scraped_list, fp, indent=4)
