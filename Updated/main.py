import textSummarizer as ts
import json
import sqlite3 as lite
with open("test2.json", "r") as read_file:
    temp = json.load(read_file)

article_content = {}
article_title = []

#Reading in the urls
import feedparser
from newspaper import Article
counter = 0
while counter < len(temp['content']):
    print(temp['content'][counter]['url'])
    url = temp['content'][counter]['url']
    d = feedparser.parse(url)
    #rss_feedName.append(d['feed']['title'])
    #rss_feedHome.append(d['feed']['link'])
    for post in d.entries:
        links = post.link
        article = Article(links, language='en')
        article.download()
        try:
            article.parse()
            article_content[article.text] = d['feed']['link']
            article_title.append(article.title)
        except:
            pass
    counter+=1

import warnings
warnings.filterwarnings('ignore')

from nltk.tokenize import sent_tokenize
from operator import itemgetter
from nltk.corpus import brown, stopwords

stop_words = stopwords.words('english')

counter = 0
temp = ""
con = lite.connect('paperstuff.db')
with con:
    cur = con.cursor()
    for texts in article_content:
        sentences = sent_tokenize(texts)
        S = ts.build_similarity_matrix(sentences, stop_words)
        sentence_ranks = ts.pagerank(S)
        ranked_sentence_indexes = [item[0] for item in sorted(enumerate(sentence_ranks), key=lambda item: -item[1])]
        SUMMARY_SIZE = 5
        SELECTED_SENTENCES = sorted(ranked_sentence_indexes[:SUMMARY_SIZE])
        summary = itemgetter(*SELECTED_SENTENCES)(sentences)
        # Print the actual summary
        print(article_title[counter])
        print('\nSUMMARY')
        print('------------------------------')
        for sentence in summary:
            temp+=''.join(sentence)
            print(''.join(sentence))
        print('-----------------------------')
        cur.execute("INSERT INTO Paper VALUES(?,?,?)",(article_content[texts], article_title[counter], temp))
        counter+=1
