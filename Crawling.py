from newspaper import Article
import requests
from lxml.html import fromstring
from bs4 import  BeautifulSoup

def news_link(category,Category_url):
    i=1
    num=0
    if i==1:
        url_page = '?page='
        url = 'https://news.daum.net/breakingnews/' + Category_url + url_page + str(i)
        print(url)
        res = requests.get(url)

        parser = fromstring(res.text)

        article_list = parser.xpath('//div[@class="box_etc"]')

        parsed_articles = article_list[0].xpath('.//li')

        for article in parsed_articles:
            parsed_link = article.xpath('.//a[@href]')

            link = parsed_link[0].get('href')
            category.append(link)
            if num == 2:
                break
            num+=1

    return category

def split(category, category_ko):
    titles = []
    sentences = []
    for link in category:
        resp = requests.get(link)
        soup = BeautifulSoup(resp.text,"lxml")
        news_titles = soup.select_one('h3.tit_view')
        title= news_titles.get_text()
        content = ''
        for p in soup.select('div#harmonyContainer p'):
            content +=p.get_text()
        sentence = content
        titles.append(title)
        sentences.append(sentence)
    return titles, sentences

