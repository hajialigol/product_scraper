def get_product_info(doc):

    # define the name path
    name_path = '//div[starts-with(@id, "shop-product-title")]'

    # get the name ele
    try:
        name_ele = doc.xpath(name_path)[0]
    except:
        # something is wrong with url
        return {}

    # return a dictionary with all information
    try:
        return {
            'company': name_ele.xpath('.//div')[0].xpath('.//a')[0].text,
            'product_name': name_ele.find_class('sku-title')[0].text_content()
        }

    # case when something is wrong with the website
    except:
        return {}