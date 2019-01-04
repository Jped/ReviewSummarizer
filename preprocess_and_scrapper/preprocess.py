# Preprocessing file 

import string
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import snowballstemmer


def load_valid_word_list():
    '''
    Loads in a file with all the valid words and returns
    it as a set.
    '''
    with open('valid_word_list.txt') as word_file:
        words = set(word_file.read().split())

    return words


def remove_nonvalid_words(string_array):
    '''
    Given an array of reviews (or any array of strings),
    this function keeps only the words that are valid and returns
    the new array (this function does not modify the original input).
    
    Valid words are determined based on the valid_word_list.txt file.
    '''    
    valid_word_list = load_valid_word_list()
    return [' '.join([w for w in s.split() if w in valid_word_list]) for s in string_array]



def remove_stop_words(string_array):
    '''
    Given an array of reviews (or any array of strings),
    this function removes any stopwords from it and returns
    the new array (this function does not modify the original input).
    '''
    stop_words = set(stopwords.words('english'))
    return [' '.join([w for w in s.split() if w not in stop_words]) for s in string_array]



def remove_punctuation(string_array):
    '''
    Given an array of reviews (or any array of strings),
    this function removes any punctuation and returns
    the new array (this function does not modify the original input).
    '''
    return [' '.join([w for w in s.split() if w not in string.punctuation]) for s in string_array]



def lower_case_words(string_array):
    '''
    Given an array of reviews (or any array of strings),
    this function lower-cases all the words and returns
    the new array (this function does not modify the original input).
    '''
    return [s.lower() for s in string_array]



def normalize_words(string_array):
    '''
    Given an array of reviews (or any array of strings),
    this function normalizes all its words and returns
    the new array (this function does not modify the original input).
    
    Normalization means stemming each word to its root.
    '''
    stemmer = snowballstemmer.stemmer('English')
    return [' '.join([stemmer.stemWord(word) for word in s.split()]) for s in string_array] 



def preprocess(string_array):
    '''
    Preprocess an array of strings using all of the above functions:
        1. Lower-cases all strings.
        2. Removes any punctuation in the strings.
        3. Removes all stop words in the strings.
        4. Normalizes all words in the strings.
        5. Removes all non-valid words.
    '''
    tmp = lower_case_words(string_array)
    tmp = remove_punctuation(tmp)
    tmp = remove_stop_words(tmp)
    tmp = normalize_words(tmp)
    tmp = remove_nonvalid_words(tmp)
    return tmp

