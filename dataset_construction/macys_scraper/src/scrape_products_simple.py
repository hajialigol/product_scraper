import requests
import json
from tqdm import tqdm

# function to get a product's id
def get_prod_id(url):

    # case when this works
    try:

        # get the id
        return url.split('ID=')[1].split('&')[0]

    # should work all the time but just in case it doesn't
    except:

        # return -1
        print("id fetch didn't work")
        return -1

# function to get data from the reviews dictionary
def _get_review_data(rev_dict_list):

    # list that will hold all review data
    rev_list = []

    # iterate over the number of reviews
    for rev_dict in rev_dict_list:

        # get the user id
        user_id = rev_dict['authorId']

        # get the rating
        rating = rev_dict['rating']

        # check if "title" is in the dictionary
        if 'title' in rev_dict:

            # get the review title
            rev_title = rev_dict['title']

        # yes, there are people who left reviews without a title
        else:

            # set equal to N/A
            rev_title = 'N/A'

        # get the review body
        rev_body = rev_dict['reviewText']

        # get number of positive feedback
        num_positive_feedback = rev_dict['totalPositiveFeedbackCount']

        # get number of positive feedback
        num_negative_feedback = rev_dict['totalNegativeFeedbackCount']

        # get photos
        images = rev_dict['photos']

        # make a dictionary of all this information
        review_dict = {
            'user_id': user_id,
            'rating': rating,
            'review_title': rev_title,
            'review_body': rev_body,
            'images': images,
            'number_positive_feedback': num_positive_feedback,
            'number_negative_feedback': num_negative_feedback
        }

        # add to list
        rev_list.append(review_dict)

    # return this list
    return rev_list

# function to get the reviews
def get_reviews(product_dict, num_reviews, headers):

    # get the id
    id = product_dict['id']

    # url without attributes
    base_url = f'http://www.macys.com/xapi/digital/v1/product/{id}/reviews'

    # list that will hold all reviews
    reviews_list = []

    # check if number of reviews > 8
    if num_reviews > 8:

        # offset value
        offset = 8

        # iterate until offset is larger than number of reviews
        while (offset < num_reviews):

            # make the request
            rev_req = requests.get(url=base_url, headers=headers,
                                   params={'offset': offset}).json()

            # get the reviews dictionary
            reviews_dict = rev_req['review']['reviews']

            # get reviews data
            reviews_result_dict = _get_review_data(reviews_dict)

            # add this to a list
            reviews_list.extend(reviews_result_dict)

            # update offset
            offset += 30

    # case when there are reviews, but less than 8
    # elif num_reviews > 0:
    #
    #     # make the request
    #     rev_req = requests.get(url=base_url, headers=headers,
    #                            params={'offset': 8}).json()
    #
    #     # get the reviews dictionary
    #     reviews_dict = rev_req['review']['reviews']
    #
    #     # get reviews data
    #     reviews_result_dict = _get_review_data(reviews_dict)
    #
    #     # add this to a list
    #     reviews_list.extend(reviews_result_dict)

    # return the list
    return reviews_list



# extract all data of interest (except reviews)
def get_product_data(prod_dict, url, headers):

    # get the meta data dictionary
    meta_dict = prod_dict['meta']['analytics']['data']

    # get the product dictionary
    prod_dict = prod_dict['product'][0]

    # get the category name
    category_name = meta_dict['t_category_name'][0]

    # get the product name
    prod_name = meta_dict['product_name'][0]

    # get the product brand
    prod_brand = meta_dict['product_brand'][0]

    # get the original product price
    orig_price = meta_dict['product_original_price'][0]

    # get the current product price
    cur_price = meta_dict['product_price'][0]

    # get the product rating
    prod_rating = float(meta_dict['product_rating'][0])

    # get the number of reviews
    num_reviews = int(meta_dict['product_reviews'][0])

    # get reviews
    prod_reviews = get_reviews(prod_dict, num_reviews, headers)

    # get the description
    prod_desc = prod_dict['detail']['description']

    # check if a bullet description exists
    if 'bulletText' in prod_dict['detail']:

        # get bulleted text
        bullet_text = prod_dict['detail']['bulletText']

    # otherwise, just make an empty string
    else:

        # empty string assignment
        bullet_text = ''

    # get keywords
    keywords = prod_dict['detail']['seoKeywords']

    # get product images
    prod_images = ["https://slimages.macysassets.com/is/image/MCY/products/" +
                   image_dict['filePath'] for image_dict in prod_dict['imagery']['images']]

    # get the colors
    # colors = [color_dict['normalName'] for color_dict in prod_dict['traits']['colors']['colorMap']]

    # make a dictionary of all results
    results_dict = {
        'url': url,
        'product_name': prod_name,
        'product_brand': prod_brand,
        'category': category_name,
        'original_price': orig_price,
        'current_price': cur_price,
        'product_description': prod_desc,
        'product_bullet_description': bullet_text,
        'product_rating': prod_rating,
        'number_reviews': num_reviews,
        'product_images': prod_images,
        'product_keywords': keywords,
        'product_reviews': prod_reviews
        # 'colors': colors
    }

    # return the dictionary
    return results_dict


# runner
if __name__ == "__main__":

    # input file
    input_path = '../data/macys_products_to_scrape.txt'

    # headers
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
                             ' (KHTML, like Gecko) Version/15.3 Safari/605.1.15'}

    # output path
    output_path = r'../data/macys_scraped.json'

    # read in the data
    with open(input_path, 'r') as fp:
        data = ["https://www.macys.com" + line.split('\n')[0] for line in fp.readlines()]

    # get unique values
    data = list(set(data))

    # list to hold all output
    output_list = []

    # iterate over each url
    for url in tqdm(data[:50]):

        # get the product id
        url_id = get_prod_id(url)

        # make the product url for the request
        prod_url = f'https://www.macys.com/xapi/digital/v1/product/{url_id}'

        # make the request
        prod_results = requests.get(url=prod_url, headers=headers).json()

        # get the description
        results = get_product_data(prod_dict=prod_results, url=url, headers=headers)

        # see what this looks like
        output_list.append(results)

    # write json out
    with open(output_path, 'w', encoding='utf-8') as fp:
        json.dump(output_list, fp, indent=4)