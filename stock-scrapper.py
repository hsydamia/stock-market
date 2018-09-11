from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import re
import json
import numpy as np

# add to replace non ascii char
# replace("/\u2013|\u2014/g", "-").replace("/\u2019s", "'")

base_url = "http://www.theedgemarkets.com"

years = [
    "2018",
    "2017",
    "2016",
    "2015",
    "2014"
]

companies = [
    "maybank",
    # "axiata",
    # "cimb",
    # "petronas",
    # "sime darby"
]

delays = [7, 4, 6, 2, 10, 19]

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

def go_to_link(url, referer):

    # add random delay between request
    delay = np.random.choice(delays)
    time.sleep(delay)

    # use random user agents, set referer as previous page.
    # add extra headers to mimic browser activity
    headers = {
        'User-Agent': get_random_ua(),
        'referer': referer,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ms;q=0.8',
        'cache-control': 'no-cache'
        'dnt': '1'
        'pragma': 'no-cache'
        'upgrade-insecure-requests': '1'
    }

    req = Request(url, headers=headers)
    page_html = urlopen(req).read()

    return soup(page_html,"html.parser")

for company in companies:
    terminate = False

    company_dict = {}
    index = 0
    filename  = company.replace(" ", "-") + "-data.json"
    file = open(filename, "w", encoding="utf-8")

    for page in range(0, 1000):
        if terminate is True:
            break

        search_url = base_url + "/search-results?page=" + str(page) + "&keywords=" + company + "+stock"
        search_page = go_to_link(search_url, base_url)
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
            article_page = go_to_link(base_url + article_url, search_url)

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
                break

            body_div = body_div.find('div', {'class': 'field-items'})
            if not body_div:
                break

            body_div = body_div.find('div', {'class': 'field-item even'})
            if not body_div:
                break

            body_p = body_div.findAll('p');
            if not body_p:
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
            index += 1
            print(company_dict)
            print(index)

# write to file
data_to_write = json.dumps(company_dict)
file.write(data_to_write)
print(data_to_write.encode("utf-8"))
print("")
file.close()