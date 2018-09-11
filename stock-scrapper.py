from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup as soup
import re
import json
import numpy as np
import time
import datetime

# add to replace non ascii char
# replace("/\u2013|\u2014/g", "-").replace("/\u2019s", "'")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

base_url = "https://www.theedgemarkets.com"

years = [
    "2018",
    "2017",
    "2016",
    "2015",
    "2014"
]

companies = [
    "maybank",
    "axiata",
    "cimb",
    "petronas",
    "sime darby"
]

maybank_total = 0
axiata_total = 0
cimb_total = 0
petronas_total = 0
sime_darby_total = 0
grand_total = 0

# delays = [2, 4, 3, 5, 7, 9, 13, 19, 1, 9, 15, 10]
delays = [0]

def get_random_ua():

    # get random user agent from user-agents.txt file
    random_ua = ''
    ua_file = 'user-agents.txt'
    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_ua = lines[int(idx)]
    except Exception as ex:
        print('Exception in random_ua')
        print(str(ex))
    finally:
        return random_ua.replace('\n', '')

def go_to_link(url, referer, company, count = None):

    # add random delay between request
    # add your delay value (in second) to above delays array
    delay = np.random.choice(delays)
    logging(company, url + ' : Delay for ' + str(delay) + ' second(s)', count)
    time.sleep(delay)

    # use random user agents, set previous page as referer
    headers = {
        'User-Agent': get_random_ua(),
        'referer': referer
    }
    req = Request(url, headers=headers)

    try:
        response = urlopen(req)
        page_html = response.read()
        
        return soup(page_html,"html.parser")
    except HTTPError as e:
        logging(company, bcolors.FAIL + url + ' : ERROR! (HttpError,' + str(e.code) + ')' + bcolors.ENDC)
    except URLError as e:
        logging(company, bcolors.FAIL + url + ' : ERROR! (URLError,' + str(e.reason) + ')' + bcolors.ENDC)

    return False

def logging(company, text, count = None):

    # simplify logging
    if count is not None:
        company = company.upper() + '(' + str(count+1) + ')'
    else:
        company = company.upper()

    print(company + ' : ' + text)

def set_company_total(company, total):

    # set total for summary
    global maybank_total
    global axiata_total
    global cimb_total
    global petronas_total
    global sime_darby_total
    global grand_total

    if company == 'maybank':
        maybank_total = total
    elif company == 'petronas':
        petronas_total = total
    elif company == 'axiata':
        axiata_total = total
    elif company == 'cimb':
        cimb_total = total
    elif company == 'sime darby':
        sime_darby_total = total

    grand_total = grand_total + total

def print_summary():
    print(bcolors.BOLD + '------- SUMMARY OF TOTAL ARTICLES SCRAPPED -------')
    print(bcolors.OKBLUE)
    print(' MAYBANK : ' + str(maybank_total))
    print(' AXIATA : ' + str(axiata_total))
    print(' CIMB : ' + str(cimb_total))
    print(' PETRONAS : ' + str(petronas_total))
    print(' SIME DARBY : ' + str(sime_darby_total))
    print('')
    print(' GRAND TOTAL : ' + str(grand_total))
    print(bcolors.ENDC)
    print(bcolors.BOLD + '--------------------------------------------' + bcolors.ENDC)

for company in companies:
    logging(company, bcolors.BOLD + '------- START -------' + bcolors.ENDC)
    terminate = False

    company_dict = {}
    index = 0
    filename  = company.replace(" ", "-") + "-data.json"
    file = open(filename, "w", encoding="utf-8")

    for page in range(0, 1000):
        if terminate is True:
            break

        search_url = base_url + "/search-results?page=" + str(page) + "&keywords=" + company.replace(' ', '+') + "+stock"
        search_page = go_to_link(search_url, base_url, company)
        print("")

        if search_page is False:
            continue

        rows = search_page.findAll("div",{"class":"views-row"})
        
        for row in rows:

            # get year, compared to years list
            date_div = row.find('div', {'class': 'views-field views-field-nothing'})
            date_posted = date_div.find('span', {'class': 'field-content'})

            if not date_posted:
                continue

            date_array = date_posted.text.split(" ")

            del date_array[0]
            date_value = " ".join(date_array)

            dt = datetime.datetime.strptime(date_value, '%d %B %Y')
            date_value = f'{dt.day}/{dt.month}/{dt.year}'
            
            if not date_value:
                continue

            year_posted = date_array[-1];

            if year_posted not in years:
                terminate = True
                break

            # get url
            url_div = row.find('div', {'class': 'views-field views-field-title'})
            url_div = url_div.find('span', {'class': 'field-content'})
            article_url = url_div.find('a')['href']

            # in article page
            article_page = go_to_link(base_url + article_url, search_url, company, index)

            if article_page is False:
                continue

            # get article title
            title_div = article_page.find('div', {'class': 'post-title'})
            title = title_div.find('h1')

            if not title:
                title = "No title"
            else:
                title = title.text

            # get article body
            body_div = article_page.find('div', {'class': 'field field-name-body field-type-text-with-summary field-label-hidden'})
            
            if not body_div:
                logging(company, base_url + article_url + ' : NO BODY, SKIPPED!', index)
                continue

            body_div = body_div.find('div', {'class': 'field-items'})
            if not body_div:
                logging(company, base_url + article_url + ' : NO BODY, SKIPPED!', index)
                continue

            body_div = body_div.find('div', {'class': 'field-item even'})
            if not body_div:
                logging(company, base_url + article_url + ' : NO BODY, SKIPPED!', index)
                continue

            body_p = body_div.findAll('p');
            if not body_p:
                logging(company, base_url + article_url + ' : NO BODY, SKIPPED!', index)
                continue

            body_text = ""
            for p in body_p:
                body_text = body_text + " " + p.text

            data_dict = {
                'date_posted' : date_value,
                'title' : title,
                'article' : body_text
            }

            company_dict[index] = data_dict
            logging(company, bcolors.OKGREEN + base_url + article_url + ' : SCRAPPED' + bcolors.ENDC, index)
            print("")

            index += 1

    # write to file
    data_to_write = json.dumps(company_dict)
    file.write(data_to_write)
    file.close()
    set_company_total(company, index)
    logging(company, bcolors.HEADER + str(index) + ' article(s) scrapped' + bcolors.ENDC)
    logging(company, bcolors.HEADER + 'File saved as : ' + company.replace(" ", "-") + '-data.json' + bcolors.ENDC )
    logging(company, bcolors.BOLD + '------- ENDED -------' + bcolors.ENDC)
    print("")
    print("")

print_summary()