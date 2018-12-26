#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json


# In[3]:


# USAGE: pass in the number of reviews you want and the filename with the JSON
# It will return a dictionary where the key is an asin for a product and the value is an array with the reviews
def returnReviews(num_reviews, filename):
    reviews = {}
    fo = open(filename,'r')
    for x in range(num_reviews):
        reviewRaw = fo.readline()
        review = json.loads(reviewRaw)
        asin = review["asin"]
        if asin in reviews:
            tmp = reviews[asin]
            tmp.append(review['reviewText'])
            reviews[asin] = tmp
        else:
            reviews[asin] = [review["reviewText"]]
    return reviews

