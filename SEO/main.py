from nltk.corpus import stopwords
from nltk import ngrams
from bs4 import BeautifulSoup
from bs4 import Comment
from urllib.request import urlopen
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

import csv
import string
import re

############################
############################    GLOBAL VARIABLES
############################

SKETCH_SIZE_MINIMUM = 200
SKETCH_SIZE_MAXIMUM_PERCENTAGE = 0.25


############################
############################    INPUT
############################

# Get k-grams for every url the user inputs
def get_kgrams_from_user_inputs():
    #init
    urls = []
    url = "init"
    punc = string.punctuation.join(["»", "©", '\xa0'])

    #dictionary (url -> [k-grams])
    urls_kgrams = {}


    #input shingle size parameter
    shingle_size = int(input("Shingle size parameter? : "))

    #input urls
    print("Enter some urls, Empty string to stop")
    url_input_loop_count = 0
    while True  : 
        url_input_loop_count += 1
        url = input("Url " + str(url_input_loop_count) + ": ")
        if len(url) == 0 :
            break
        urls.append(url)

    #For each url, get corresponding k-grams
    for url in urls :
        html = urlopen(url)
        soup = BeautifulSoup(html, 'html.parser')
        texts = soup.find_all(string=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in texts]
        texts = soup.find_all(text=True)

        #filter
        def visible(element):
            el = str (element)
            if element.parent.name in ['style', 'script', 'head', 'title']:
                return False
            elif re.match('<!--*-->', el):
                return False
            return True

        visible_texts = filter(visible, texts)
        lst = list(visible_texts)

        #concat
        fulltxt = " ".join(" ".join(lst).split());

        #remove punctuation
        predicate = lambda x:x not in punc
        fulltxtwp = list(filter(predicate, fulltxt))

        #concat again
        fulltxtwp = ''.join(fulltxtwp)

        #extract grams
        grams =  ngrams(fulltxtwp.split(' '), shingle_size)
        urls_kgrams[url] = grams


    #display
    #for pages in urls_kgrams :
    #    for gram in urls_kgrams[pages] :
    #        print(gram)



    return urls_kgrams;




############################
############################    OUTPUT
############################

# Create output files from calculated duplicate rate bewteen the urls
def make_output(raw_data):
    
    # Sets output's content from raw duplicate rate data
    data = raw_data
    header = [""]
    for x in range(len(data)):
        s = "URL " + str(x + 1)
        header.append(s)
        data[x].insert(0, s)
    data.insert(0, header)

    def make_csv(data):
        # Write csv with column & row names
        with open("output.csv", "w", newline = "") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        return;

    def make_pdf(data):
        # Define a style for the entire table
        style = TableStyle([('ALIGN',(1,1),(-1,-1),'RIGHT'),
                               ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                               ('TEXTCOLOR',(0,0),(-1,0),colors.blue),
                               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ])

        # Create table from data and assign the style we defined
        t=Table(data)
        t.setStyle(style)

        # Colour according to values.
        # x > 0 && Y > 0 are so we don't parse row / column names
        for x in range(len(data)):
            for y in range(len(data[x])):
                print("data " + str(data[x][y]))
                if (x > 0 and y > 0 and str(data[x][y]) != "" and float(data[x][y]) >= 0.8):
                    t.setStyle(TableStyle([('TEXTCOLOR', (x, y), (x, y), colors.red)]))
                    print("IN")

        doc = SimpleDocTemplate("output.pdf", pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
        doc.pagesize = landscape(A4)
        elements = []
        elements.append(t)
        doc.build(elements) # This writes to disk in the current directory.
        return;

    make_csv(data)
    make_pdf(data)

    return;



############################
############################    COMPUTATION
############################

def compute_duplicate_rates(urls_kgrams):

    # For time optimisation purposes we only keep a randomly chosen subset of all the shingles, called sketches
    def get_urls_sketches(urls_kgrams):
        return;

    # computes the duplicate rate between two urls
    # Inputs: the urls' sketches
    # Output: number between 0 and 1
    def compute_duplicate_rate_between_two_urls(sketch1, sketch2):
        return 2.1;



    urls_sketches = urls_kgrams #get_urls_sketches(urls_kgrams)
    raw_data = []


    loop1_count = 0
    for url1, sketch1 in urls_sketches.items():
        loop1_count += 1
        line = []
        loop2_count = 0
        for url2, sketch2 in urls_sketches.items():
            loop2_count += 1
            if loop2_count > loop1_count:
                line.insert(loop2_count - 1, compute_duplicate_rate_between_two_urls(sketch1, sketch2))
            else :
                line.insert(loop2_count - 1, "")
        raw_data.append(line)


    return raw_data;







############################
############################    MAIN
############################


urls_kgrams = get_kgrams_from_user_inputs()

raw_data = compute_duplicate_rates(urls_kgrams)
#raw_data = [["", 0.79, 0.8, 80],
 #               [0, 100, 0, 50], 
  #              [0.9, 0, 100, 0],
   #             [80, 50, 0, 100]]

make_output(raw_data)

print("END")