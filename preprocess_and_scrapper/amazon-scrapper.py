#
# Functionality for scrapping an amazon page for reviews.
#
# To run, import file and run:
#    $ scrapeAmazonReviews(output_folder)
# where output_folder is an optional input.
# 
# For more information, type in 'help(scrapeAmazonReviews)'


from lxml import html
from json import dump,loads
from requests import get
import json
from re import sub
from dateutil import parser as dateparser
from time import sleep



def ParseReviews(amazon_url):
    '''
    Given a url to an amazon product, this function returns all
    of its amazon reviews in a json format.
    
    Each review is made up of both some text and a rating(1-5).
    '''
    # Add some recent user agent to prevent amazon from blocking the request 
    headers = {'User-Agent': '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'''
                                '''(KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'''}
    
    # try getting the data 5 times. Will only retry getting data if response code isn't 200
    for i in range(5): 
        # The response is the whole page (html, css, javascript, response code)
        response = get(amazon_url, headers = headers, timeout=30)
        if response.status_code == 404:
            return {"url": amazon_url, "error": "page not found"}
        if response.status_code != 200: # checks whether to retry getting the page.
            continue
        
        # Removing the null bytes from the response. 
        cleaned_response = response.text.replace('\x00', '') 

        # get html in tree structure that can be parsed with XPath
        parser = html.fromstring(cleaned_response) 
        
        XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
        XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
        XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'
        
        reviews = parser.xpath(XPATH_REVIEW_SECTION_1)
        
        if not reviews:
            reviews = parser.xpath(XPATH_REVIEW_SECTION_2)
        
        reviews_list = []

        
        # Parsing individual reviews
        for review in reviews:
            
            XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
            raw_review_rating = review.xpath(XPATH_RATING)
            review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')

            XPATH_REVIEW_TEXT = './/span[@data-hook="review-body"]//text()'
            raw_review_text = review.xpath(XPATH_REVIEW_TEXT)
            review_text = ' '.join(' '.join(raw_review_text).split())
            
            reviews_list.append({'review_text': review_text, 'review_rating': review_rating})

        data = { 'url': amazon_url,
                 'reviews': reviews_list }
        
        return data

    return {"error": "failed to process the page", "url": amazon_url}
            


def getTotalReviewcount(amazon_url):
    '''
    Given an amazon product url, this function scrapes the total
    amount of reviews that the product has, and returns the value.
    '''
    # Add some recent user agent to prevent amazon from blocking the request 
    headers = {'User-Agent': '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'''
                               '''(KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'''}
    
    # try getting the data 5 times. Will only retry getting data if response code isn't 200
    for i in range(5): 
        # The response is the whole page (html, css, javascript, response code)
        response = get(amazon_url, headers = headers, timeout=30)
        if response.status_code == 404:
            return {"url": amazon_url, "error": "page not found"}
        if response.status_code != 200: # checks whether to retry getting the page.
            continue
        
        # Removing the null bytes from the response. 
        cleaned_response = response.text.replace('\x00', '') 

        # get html in tree structure that can be parsed with XPath
        parser = html.fromstring(cleaned_response) 
        
        # getting the product name
        XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
        raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
        product_name = ''.join(raw_product_name).strip()
        
        # getting the total review count
        XPATH_REVIEW_COUNT = '//h3//span[@data-hook="top-customer-reviews-title"]//text()'
        raw_review_count = parser.xpath(XPATH_REVIEW_COUNT)
        review_count = ''.join(raw_review_count).strip()

        starting_index = review_count.find('of ') + 3
        ending_index = review_count.find(' reviews')
        review_count = review_count[starting_index:ending_index]
        
        review_count = review_count.replace(',', '') # get rid of any potential commas
        
        review_count = int(review_count)

        # getting the aggregated ratings
        XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
        total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
     
        ratings_dict = {}
        for ratings in total_ratings:
            extracted_rating = ratings.xpath('./td//a//text()')
            if extracted_rating:
                rating_key = extracted_rating[0] 
                rating_value = extracted_rating[1]
                if rating_key:
                    ratings_dict.update({rating_key: rating_value})
        
        return { 'url': amazon_url,
                 'name': product_name,
                 'review-count': review_count,
                 'ratings': ratings_dict }



def scrapeAmazonReviews(output_folder = None):
    '''
    Scrapes the user-inputted website for reviews, writing them
    into a json file.

    If a global path to an output folder is not inputted, this
    function defaults to writing the json file into ./scrapped-reviews/.
    '''
    if not output_folder:
        output_folder = './scrapped-reviews/'
    
    link = input('Website link:')
    
    # get the name, the amount of reviews, and the aggregated ratings
    basic_info = getTotalReviewcount(link)
    
    if len(basic_info['name']) > 15:
        f = open(output_folder + basic_info['name'][:15] + '..._product-reviews.json', 'w')
    else:
        f = open(output_folder + basic_info['name'][:15] + '_product-reviews.json', 'w')    
            
    dump(basic_info, f, indent=4)

    # get the reviews
    reviews_link = link.replace('/dp/', '/product-reviews/')
    
    last_index1 = reviews_link.find('?')
    last_index2 = reviews_link.find('/ref')
    if last_index1 is -1:
        min_index = last_index2
    elif last_index2 is -1:
        min_index = last_index1
    else:
        min_index = min(last_index1, last_index2)
        
    reviews_link = reviews_link[:min_index]
    reviews_link = reviews_link + '/?pageNumber='
    
    for i in range(1, (basic_info['review-count']//10) + 2):
        extracted_data = ParseReviews(reviews_link + str(i))
        dump(extracted_data, f, indent=4)
        
    f.close()

