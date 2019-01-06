
# coding: utf-8

# Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/, modified by us.

# In[129]:


from lxml import html
from json import dump,loads
from requests import get
import json
import re
from dateutil import parser as dateparser
from time import sleep
from itertools import cycle 
from selenium import webdriver


# In[166]:

def parseReviews(amazon_url):
    '''
    Given a url to an amazon product, this function returns all
    of its amazon reviews in a json format.
    
    Each review is made up of both some text and a rating(1-5).
    '''

    parser = getLink(amazon_url)
    if parser:
        XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
        XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
        XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'
        XPATH_REVIEW_MOBILE = '//div[contains(@class,"reviews-content")]'
        print(type(parser), parser)
        reviews = parser.xpath(XPATH_REVIEW_SECTION_1)

        if not reviews:
            reviews = parser.xpath(XPATH_REVIEW_SECTION_2)
            if not reviews:
                reviews = parser.xpath(XPATH_REVIEW_MOBILE)
                if not reviews: 
                    raise Exception("No Reviews section found")
        reviews_list = []
        if len(reviews) ==0:
            raise Exception("Zero reviews!")

        # Parsing individual reviews
        for review in reviews:

            XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
            raw_review_rating = review.xpath(XPATH_RATING)
            review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')

            XPATH_REVIEW_TEXT = './/span[@data-hook="review-body"]//text()'
            XPATH_REVIEW_MOBILE= './/div[contains(@class, "a-expander-content")]//text()'
            raw_review_text = review.xpath(XPATH_REVIEW_TEXT)
            if not raw_review_text:
                raw_review_text = review.xpath(XPATH_REVIEW_MOBILE)
                if not raw_review_text:
                    raise Exceptions("raw reviews is empty")
            review_text = ' '.join(' '.join(raw_review_text).split())    
            reviews_list.append({'review_text': review_text, 'review_rating': review_rating})
        print("review LIST",reviews_list)
        if len(reviews_list)== 0:
            raise Exception("Reviews list is empty")
        data = { 'url': amazon_url,
                 'reviews': reviews_list }
        return data

    return {"error": "failed to process the page", "url": amazon_url}
# In[99]:


def getProxies():
    url = 'https://free-proxy-list.net/'
    response = get(url)
    parser = html.fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


# In[100]:


agents = ["Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0", 
          "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36", 
          "Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; SCH-I535 Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30", 
          "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)"]
agent_pool = cycle(agents)


# In[142]:


proxies = getProxies()
proxy_pool = cycle(proxies)


# In[106]:


def isRobot(response):
    title = response.findtext('.//title')
    if "robot" in title.lower():
        print("ROBOT!")
        return True
    return False


# In[135]:


def headless(amazon_url): 
    print("HEADLESS!!!")
    driver = webdriver.PhantomJS()
    driver.get(amazon_url)
    return driver.page_source


# In[145]:


def getLink(amazon_url):
    headers = {'User-Agent': '''Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'''}
    response = ''
    parser = ''
    successful = False
    counter = 0
    MAX_TRIES = 10
    shuffle = False
    while not successful and counter<MAX_TRIES: 
        if not shuffle:
            response = get(amazon_url, headers = headers, timeout=30)
        else:
            agent = next(agent_pool)
            headers['User-Agent'] = agent
            try:
                print("trying proxy!")
                proxy = next(proxy_pool)    
                response = get(amazon_url,proxies={"http":proxy,"https":proxy}, headers=headers, timeout=30)
            except Exception as e:
                print("exception while trying to use a proxy", e)
        if response.status_code == 404:
            return False
        cleaned_response = response.text.replace('\x00', '')
        #fo = open("text.html", "w")
        #fo.write(response.text)
        #fo.close()
        # get html in tree structure that can be parsed with XPath
        parser = html.fromstring(cleaned_response) 
        robot = isRobot(parser)
        if robot:
            shuffle = True
        else:
            print("succcesful!")
            successful = True
        counter+=1
    if successful:
        pass
    else:
        #headless:
        response = headless(amazon_link)
        cleaned_response = response.replace('\x00','')
        parser = html.fromstring(cleaned_response)
    return parser


# In[125]:


def getTotalReviewcount(amazon_url):
    '''
    Given an amazon product url, this function scrapes the total
    amount of reviews that the product has, and returns the value.
    '''
    parser = getLink(amazon_url)
    if parser:
        # getting the product name
        XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
        XPATH_MOBILE_NAME = '//h1[@id="title"]//text()'
        raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
        product_name = ''.join(raw_product_name).strip()
        if  product_name: 
            raw_product_name = parser.xpath(XPATH_MOBILE_NAME)
            product_name = ''.join(raw_product_name).strip()
            if  len(product_name) == 0:
                raise Exception("PRODUCT NAME MESSED UP!")
        # getting the total review count
        XPATH_REVIEW_COUNT = '//*[@data-hook="total-review-count"]//text()'
        raw_review_count = parser.xpath(XPATH_REVIEW_COUNT)
        if not raw_review_count:
            raise Exception("REVIEW COUNT MESSED UP!")
        review_count = raw_review_count[0].split()[0]
        review_count = int(review_count.replace(",",''))

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
    else:
        raise Exception("Was not able to get the link")

def scrapeAmazonReviews(link):
    '''
    Scrapes the user-inputted website for reviews, returns the reviews
    in a JSON format
    '''
    response = {"link":link}
    # get the name, the amount of reviews, and the aggregated ratings
    basic_info = getTotalReviewcount(link)
    print("basic info", basic_info)
    response["basic_info"] = basic_info
    

    # get the reviews
    reviews_link = re.sub(r"/dp/","/product-reviews/",link)
    reviews_link_match = re.search(r".*/product-reviews/\w+",reviews_link)
    if reviews_link_match:
        reviews_link = reviews_link_match.group(0) + '/?pageNumber='
    else:
        raise Excpetion("No Product number")
    for i in range(1, (basic_info['review-count']//10) + 2):
        extracted_data = parseReviews(reviews_link + str(i))
        response[i] = extracted_data
    return response

