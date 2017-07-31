from nltk.corpus import stopwords
from nltk import ngrams
from bs4 import BeautifulSoup
from bs4 import Comment
from urllib.request import urlopen
import string
import re

#init
urls = []
url = "init"
punc = string.punctuation.join(["»", "©"])


#dictionary (url -> [k-grams])
pagesGrams = {}


#input k gram
kgram = int(input("K-grams? :"))

print("Enter some urls, Empty string to stop")
#input urls
while True  :
    url = input("Url :")
    if len(url) == 0 :
        break
    urls.append(url)

#For each url -> grams
for url in urls :
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    texts = soup.findAll(string=lambda text:isinstance(text,Comment))
    [comment.extract() for comment in texts]
    texts = soup.findAll(text=True)
    texts.enco

    #filter
    def visible(element):
        el = str (element)
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--*-->', el):
            return False
        elif re.match('\n', el):
            return False
        elif re.match('  +', el):
            return False
        elif re.match('/\*', el):
            return False
        return True

    visible_texts = filter(visible, texts)
    lst = list(visible_texts)

    #concat
    fulltxt = ' '.join(lst);

    #remove punctuation
    predicate = lambda x:x not in punc
    fulltxtwp = list(filter(predicate, fulltxt))

    #concat again
    fulltxtwp = ''.join(fulltxtwp)

    #remove extra spaces
    fulltxtwp = re.sub(' +', ' ', fulltxtwp)

    #extract grams
    grams =  ngrams(fulltxtwp.split(' '), kgram)
    pagesGrams[url] = grams


#display
for pages in pagesGrams :
    for gram in pagesGrams[pages] :
        print(gram)
