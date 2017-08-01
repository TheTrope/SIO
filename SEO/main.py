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
import random

############################
############################    GLOBAL VARIABLES
############################

SKETCH_SIZE_THRESHOLD = 200
SKETCH_SIZE_PERCENTAGE = 0.25


############################
############################    INPUT
############################

# Get the single size from user input
def get_user_shingle_parameter_input():
    try :
        sh = int(input("Shingle size parameter? (int > 1): "));
        assert(sh > 1)
    except :
        print("Size must be an int > 1")
        get_user_shingle_parameter_input()

# Get urls from user input
def get_user_urls_inputs():
    urls = []

    #input urls
    print("Enter some urls, Empty string to stop")
    url_input_loop_count = 0
    while True  :
        url_input_loop_count += 1
        url = input("Url " + str(url_input_loop_count) + ": ")
        if len(url) == 0 :
            break
        if (not re.match('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)) :
            print("Url must start with http://")
            continue
        urls.append(url)
    return urls;

# Get k-grams for every url the user has input
def get_kgrams_from_urls(urls, shingle_size):
    punc = string.punctuation.join(["»", "©", '\xa0'])
    urls_kgrams = []

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
        grams =  list(ngrams(fulltxtwp.split(' '), shingle_size))
        urls_kgrams.append(grams)


    return urls_kgrams;




############################
############################    OUTPUT
############################

# Create output files from calculated duplicate rate bewteen the urls
def make_output(raw_data, urls):
    def make_csv(data):
        # Write csv with column & row names
        with open("output.csv", "w", newline = "") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        return;

    def make_pdf(data, number_of_lines_to_skip):
        # Define a style for the entire table
        style = TableStyle([('ALIGN',(1,1),(-1,-1),'RIGHT'),
                               ('TEXTCOLOR',(0, number_of_lines_to_skip),(0,-1),colors.blue),
                               ('TEXTCOLOR',(0, number_of_lines_to_skip),(-1,number_of_lines_to_skip),colors.blue),
                               ('INNERGRID', (0, number_of_lines_to_skip), (-1,-1), 0.25, colors.black),
                               ('BOX', (1, number_of_lines_to_skip + 1), (-1, -1), 0.25, colors.black),
                               ('BOX', (1, number_of_lines_to_skip), (-1, number_of_lines_to_skip), 1, colors.black),
                               ('BOX', (0, number_of_lines_to_skip + 1), (0, -1), 1, colors.black),
                               ])

        # Create table from data and assign the style we defined
        t=Table(data)
        t.setStyle(style)

        # Colour according to values.
        for x in range(len(data)):
            for y in range(len(data[x])):
                if (x > number_of_lines_to_skip and y > 0 and str(data[x][y]) != "X" and float(data[x][y]) >= 0.8):
                    t.setStyle(TableStyle([('TEXTCOLOR', (y, x), (y, x), colors.red)]))

        doc = SimpleDocTemplate("output.pdf", pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
        doc.pagesize = landscape(A4)
        elements = []
        elements.append(t)
        doc.build(elements) # This writes to disk in the current directory.
        return;

    # Set output's content from raw duplicate rate data
    data = raw_data
    # add line and column names
    header = [""]
    for x in range(len(data)):
        s = "URL " + str(x + 1)
        header.append(s)
        data[x].insert(0, s)
    data.insert(0, header)

    # add list of urls
    for i in range(len(urls)):
        data.insert(i, ["URL " + str(i + 1) + ": " + (urls[i] if len(urls[i]) <= 50 else (urls[i][:50] + " (...)"))])
    data.insert(len(urls), [""])

    #render
    try:
        make_csv(data)
        make_pdf(data, len(urls) + 1)
    except:
        print("Error: Make sure outputs do not already exist or check their rights")

    return;



############################
############################    COMPUTATION
############################

def compute_duplicate_rates(urls, kgrams):

    # For time optimisation purposes we only keep a randomly chosen subset of all the shingles, called sketches
    def get_url_sketch(shingle):
        shingle_size = len(shingle)
        if shingle_size <= SKETCH_SIZE_THRESHOLD:
            return shingle
        elif shingle_size * SKETCH_SIZE_PERCENTAGE <= SKETCH_SIZE_THRESHOLD:
            return random.sample(shingle, SKETCH_SIZE_THRESHOLD)
        else :
            return random.sample(shingle, int(shingle_size * SKETCH_SIZE_PERCENTAGE))


    # computes the duplicate rate between two urls
    # Inputs: the urls' sketches
    # Output: number between 0 and 1
    def compute_duplicate_rate_between_two_urls(shingles1, shingles2):
        def shingles_are_identical(sa, sb):
            for i in range(len(sa)):
                if sa[i] != sb[i]:
                    return False
            return True

        sketch1 = get_url_sketch(shingles1)
        sketch2 = get_url_sketch(shingles2)

        common_shingle_found = 0
        shingle_number = len(sketch1) + len(sketch2)
        for x in shingles1:
            for y in shingles2:
                if shingles_are_identical(x, y):
                    common_shingle_found += 1

        return common_shingle_found / (shingle_number - common_shingle_found);


    raw_data = []

    loop1_count = 0
    for shingles1 in kgrams:
        loop1_count += 1
        line = []
        loop2_count = 0
        for shingles2 in kgrams:
            loop2_count += 1
            if loop2_count > loop1_count:
                line.insert(loop2_count - 1, compute_duplicate_rate_between_two_urls(shingles1, shingles2))
            else :
                line.insert(loop2_count - 1, "X")
        raw_data.append(line)

    return raw_data;



############################
############################    MAIN
############################

# User inputs
shingle_size = get_user_shingle_parameter_input()
urls = get_user_urls_inputs()
# Compute corresponding k-grams
kgrams = get_kgrams_from_urls(urls, shingle_size)
# Compute duplication rate matrix data
raw_data = compute_duplicate_rates(urls, kgrams)
# Make output
make_output(raw_data, urls)

print("DONE")
