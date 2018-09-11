from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import re
import json

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

def go_to_link(url):
    search_url = url
    req = Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
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

        url = base_url + "/search-results?page=" + str(page) + "&keywords=" + company + "+stock"
        search_page = go_to_link(url)
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
            article_page = go_to_link(base_url + article_url)

            # get article title
            title_div = article_page.find('div', {'class': 'post-title'})
            title = title_div.find('h1')

            if not title:
                title = "No title"
            else:
                title = title.text

            # get article body
            body_div = article_page.find('div', {'class': 'field field-name-body field-type-text-with-summary field-label-hidden'})
            body_div = body_div.find('div', {'class': 'field-items'})
            body_div = body_div.find('div', {'class': 'field-item even'})
            body_p = body_div.findAll('p');

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