him-lychee: Lychee Language Core
Description
him-lychee is a lightweight Python package designed for high-performance cleaning and pre-processing of user-generated text (social media, reviews, forum data). It specializes in normalizing modern internet slang and abbreviations and provides a comprehensive suite of NLP utility functions.

Installation
This package requires several external NLP libraries (TextBlob, NLTK, spaCy).

Install the Core Package:

pip install him-lychee

Install Resources (Crucial for NLP Features): You must run these commands to download the linguistic models required by NLTK and spaCy:

# Download NLTK resources
python -m nltk.downloader stopwords punkt wordnet

# Download spaCy model
python -m spacy download en_core_web_sm

Lychee Core Usage
The library provides two main classes: SlangDictionary (for replacement) and TextCleaner (for NLP pipeline).

1. SlangDictionary (Abbreviation Replacement)
This module handles thousands of slang terms in a case-insensitive, highly optimized manner.

Method

Description

Usage (Recommended Pattern)

RemoveSlang(text)

[FASTEST] Converts slang terms (e.g., LOL, TBH) to their full, human-readable meanings.

df['col'].apply(slang_core.RemoveSlang)

RemoveSlangWithStopwords(text)

(v0.3.0 Placeholder) Converts slang after removing common English stop words.

df['col'].apply(slang_core.RemoveSlangWithStopwords)

get_meaning(slang_term)

Finds the meaning of a given slang term (e.g., lol -> "Laugh out loud").

slang_core.get_meaning('BRB')

reverse_lookup(keyword)

Finds slang terms based on a keyword in the meaning.

slang_core.reverse_lookup('friend')

2. TextCleaner (NLP Pre-processing Pipeline)
The TextCleaner class provides essential cleaning functions that should be applied before language modeling.

Method

Purpose

to_lowercase(text)

Converts text to lowercase.

remove_html_tags(text)

Removes embedded HTML/XML tags (<p>, <div>, etc.).

remove_urls(text)

Removes all web links (http://, www.).

remove_punctuation(text)

Removes all standard punctuation (using string.punctuation).

clean_emojis(text, mode='replace')

Removes emojis (mode='remove') or converts them to text descriptions (mode='replace').

remove_stopwords(text)

Removes common stop words (e.g., 'a', 'the', 'is') using NLTK.

spelling_correction(text)

Corrects spelling mistakes (Note: Uses TextBlob and can be slow).

stem_words(text)

Reduces words to their root/stem (e.g., 'running' -> 'run').

lemmatize_text(text)

Reduces words to their dictionary root/lemma (e.g., 'better' -> 'good').

tokenize(text, library='nltk')

Breaks text into word tokens using either NLTK or spaCy.

Quick Example
import him_lychee as ly
import pandas as pd 

slang_core = ly.SlangDictionary()
cleaner = ly.TextCleaner()

# 1. Slang Cleaning
text_a = "TBH, the GOAT dropped an absolute banger. No cap, that chorus slaps. IYKYK. BRB!"
cleaned_slang = slang_core.RemoveSlang(text_a)
# Output: "To be honest, the greatest of all time dropped an absolute banger..."

# 2. Pipeline Cleaning (Example)
cleaned_text = slang_core.RemoveSlang(df['review']).apply(cleaner.remove_urls)
