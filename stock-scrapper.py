from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import re
import json
import numpy as np
import time

# add to replace non ascii char
# replace("/\u2013|\u2014/g", "-").replace("/\u2019s", "'")

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

delays = [2, 4, 3, 5, 7, 9, 13, 19, 1, 9, 15, 10]

def get_random_ua():
    random_ua = ''
    ua_file = 'user-agents.txt'
    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_proxy = lines[int(idx)]
    except Exception as ex:
        print('Exception in random_ua')
        print(str(ex))
    finally:
        return random_ua

def go_to_link(url, referer, company, count = None):

    # add random delay between request
    delay = np.random.choice(delays)
    logging(company, url + ' : delay ' + str(delay) + ' second(s)', count)
    time.sleep(delay)

    # use random user agents, set referer as previous page.
    headers = {
        'User-Agent': get_random_ua(),
        'referer': referer
    }

    req = Request(url, headers=headers)
    page_html = urlopen(req).read()

    return soup(page_html,"html.parser")

def logging(company, text, count = None):

    if count is not None:
        company = company.upper() + '(' + str(count+1) + ')'
    else:
        company = company.upper()

    print(company + ' : ' + text)

def set_company_total(company, total):
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

for company in companies:
    logging(company, '------- START SCRAPPING -------')
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
        rows = search_page.findAll("div",{"class":"views-row"})
        
        for row in rows:

            # get year, compared to years list
            date_div = row.find('div', {'class': 'views-field views-field-nothing'})
            date_posted = date_div.find('span', {'class': 'field-content'})

            if not date_posted:
                break

            date_array = date_posted.text.split(" ")

            del date_array[0]
            date_value = "".join(date_array)

            if not date_value:
                break

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
                break

            body_div = body_div.find('div', {'class': 'field-items'})
            if not body_div:
                logging(company, base_url + article_url + ' : NO BODY, SKIPPED!', index)
                break

            body_div = body_div.find('div', {'class': 'field-item even'})
            if not body_div:
                logging(company, base_url + article_url + ' : NO BODY, SKIPPED!', index)
                break

            body_p = body_div.findAll('p');
            if not body_p:
                logging(company, base_url + article_url + ' : NO BODY, SKIPPED!', index)
                break

            body_text = ""
            for p in body_p:
                body_text = body_text + " " + p.text

            data_dict = {
                'date_posted' : date_value,
                'title' : title,
                'article' : body_text
            }

            company_dict[index] = data_dict
            logging(company, base_url + article_url + ' : DONE', index)
            print("")

            index += 1

    # write to file
    data_to_write = json.dumps(company_dict)
    file.write(data_to_write)
    file.close()
    set_company_total(company, index)
    logging(company, 'TOTAL OF ' + str(index) + ' ARTICLES SCRAPPED' )
    logging(company, '------- SCRAP ENDED -------')
    print("")

print('------- SUMMARY OF ARTICLES SCRAPPED -------')
print(' MAYBANK : ' + str(maybank_total))
print(' AXIATA : ' + str(axiata_total))
print(' CIMB : ' + str(cimb_total))
print(' PETRONAS : ' + str(petronas_total))
print(' SIME DARBY : ' + str(sime_darby_total))
print('')
print(' GRAND TOTAL : ' + str(grand_total))
print('--------------------------------------------')