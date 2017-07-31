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
    shingle_size = 3#int(input("Shingle size parameter? : "))

    #DELETEME
    #urls.append("https://www.amazon.com/ap/signin?openid.assoc_handle=aws&openid.return_to=https%3A%2F%2Fsignin.aws.amazon.com%2Foauth%3Fresponse_type%3Dcode%26client_id%3Darn%253Aaws%253Aiam%253A%253A015428540659%253Auser%252Fhomepage%26redirect_uri%3Dhttps%253A%252F%252Fconsole.aws.amazon.com%252Fconsole%252Fhome%253Fstate%253DhashArgs%252523%2526isauthcode%253Dtrue%26noAuthCookie%3Dtrue&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&action=&disableCorpSignUp=&clientContext=&marketPlaceId=&poolName=&authCookies=&pageId=aws.ssop&siteState=registered%2Cen_US&accountStatusPolicy=P1&sso=&openid.pape.preferred_auth_policies=MultifactorPhysical&openid.pape.max_auth_age=120&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&server=%2Fap%2Fsignin%3Fie%3DUTF8&accountPoolAlias=&forceMobileApp=0&language=en_US&forceMobileLayout=0")
    #urls.append("https://aws.amazon.com/")
    urls.append("file:///home/franzzy/Workspace/python/SEO/SEO/one.html")
    urls.append("file:///home/franzzy/Workspace/python/SEO/SEO/two.html")

    #input urls
    #print("Enter some urls, Empty string to stop")
    #url_input_loop_count = 0
    #while True  : 
    #    url_input_loop_count += 1
    #    url = input("Url " + str(url_input_loop_count) + ": ")
    #    if len(url) == 0 :
    #        break
    #    urls.append(url)

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
    """for pages in urls_kgrams :
        for gram in urls_kgrams[pages] :
            print(gram)"""



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
                if (x > 0 and y > 0 and str(data[x][y]) != "X" and float(data[x][y]) >= 0.8):
                    t.setStyle(TableStyle([('TEXTCOLOR', (y, x), (y, x), colors.red)]))

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
        def compare_shingles(sa, sb):
            for i in range(len(sa)):
                if sa[i] != sb[i]:
                    return False
            return True

        common_shingle_found = 0
        shingle_number = 0
        sketch2_size_counted = False
        for x in sketch1:
            shingle_number += 1
            for y in sketch2:
                if sketch2_size_counted == False:
                    shingle_number += 1
                if compare_shingles(x, y):
                    common_shingle_found += 1
                else :
                    print("==")
                    print(x)
                    print(y)
            sketch2_size_counted = True





        print(common_shingle_found)
        print(shingle_number)

        return 2#common_shingle_found / (shingle_number - common_shingle_found);



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
                line.insert(loop2_count - 1, "X")
        raw_data.append(line)



    return raw_data;







############################
############################    MAIN
############################


urls_kgrams = get_kgrams_from_user_inputs()


raw_data = compute_duplicate_rates(urls_kgrams)

make_output(raw_data)

print("END")