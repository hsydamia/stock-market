from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re

# assuming review has 100 pages
# number of review per page = 10

offset = 0
total_page = 10
number_per_page = 10

filename="review.csv"
f = open(filename, "w", encoding="utf-8")

for p in range(0, total_page):

    page = p + 1;

    if page > 1:
        offset = (number_per_page * page) - number_per_page

    myurl = "https://steamcommunity.com/app/431960/homecontent/?userreviewsoffset={}&p={}&numperpage={}".format(str(offset), str(page), str(number_per_page))
    myurl += "&browsefilter=toprated&browsefilter=toprated&appid=431960&l=english&appHubSubSection=10&filterLanguage=english"

    uClient = uReq(myurl)
    page_html=uClient.read()
    uClient.close()

    page_soup = soup(page_html,"html.parser")

    containers = page_soup.findAll("div",{"class":"apphub_UserReviewCardContent"})
    
    for container in containers:

        # get date only from class=date_posted. remove unwanted word
        date_posted = container.find('div', {'class': 'date_posted'})
        date_posted = date_posted.text.replace('Posted: ', '').replace(',', '')
        if not date_posted:
            continue

        # get recommended status inside class=reviewInfo
        review_info_div = container.find('div', {'class': 'reviewInfo'})
        status = review_info_div.find('div', {'class': 'title'})
        status = status.text
        if not status:
            continue

        # get review from class=apphub_CardTextContent
        # remove class=date_posted and class=early_access_review that are inside class=apphub_CardTextContent
        # we will get review data only. strip all whitespace
        review = container.find('div', {'class': 'apphub_CardTextContent'})
        review.find('div', {'class': 'date_posted'}).decompose()
        review.find('div', {'class': 'early_access_review'}).decompose()
        review = ' '.join(review.text.strip().split())
        if not review:
            continue

        write_to_file = status + "|" + review + "|" + date_posted + "\n"
        f.write(write_to_file)
        print(write_to_file.encode("utf-8"))
        
f.close()