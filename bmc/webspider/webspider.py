import datetime
import time

from bmc.webspider import tool
from bs4 import BeautifulSoup

# get all classifications url from a super classification
# classification_urls = tool.get_sub_classification_urls("Chemistry")
# 472 + 312 + 163 + 8 + 70 + 760 + 411 = 2196   2205
# classification_urls = tool.get_sub_classification_urls("Criminology-and-Criminal-Justice")
# print(classification_urls)

# classification_url: http://actaneurocomms.biomedcentral.com/articles
# page: https://actaneurocomms.biomedcentral.com/articles?searchType=journalSearch&sort=PubDate&page=2
# for classification_url in classification_urls:
#     classification_url = classification_url + '?tab=keyword&searchType=journalSearch&sort=Relevance&query=t-test'
#     pages = tool.get_links_of_all_pages(classification_url)
#     for page in pages:
#         article = tool.get_all_article_links_in_a_page(page)
#         articles.extend(article)
#
# print(len(articles))  # 472 + 312 + 163 + 8 + 70 + 760 + 411 = 2196


def find_classification(url):
    """

    :param url: the link of the homepage
           for example: https://www.biomedcentral.com/journals
    :return: a list of classification_name: [string]
    """

    content = tool.handle_http_requests(url)
    soup = BeautifulSoup(content, "html.parser")

    if url == 'https://www.biomedcentral.com/journals':
        classification_name = [name.string.replace(' ', '_') for name in soup.find_all('h3')]

        classification_name.pop()
        return classification_name

    elif url == 'https://plos.org/research-communities':
        pass

    else:
        pass


def search_bmc(sort=True, classification='', lower_time='01/01/2010', upper_time=time.strftime('%m/%d/%Y', time.localtime()), keyword=''):
    """
    :param sort: boolean.  True --> newest first
    :param classification: string.  id of the classification. for example: "Criminology-and-Criminal-Justice"
    :param lower_time: datetime.date
    :param upper_time: datetime.date
    :param keyword: string
    :return: dict
             key: title of the article: string
             value: a dict:
                    1. 'title': string
                    2. 'publish_time': string
                    3. 'url': string
                    4. 'authors': string
    """

    articles_t_test = {}
    articles_keyword = {}
    classification_urls = tool.get_sub_classification_urls(classification)
    # classification_url: http://actaneurocomms.biomedcentral.com/articles
    for classification_url in classification_urls:
        articles_t_test.update(tool.search_keyword(classification_url, 't-test'))
        articles_keyword.update(tool.search_keyword(classification_url, keyword))
        print("search for " + tool.get_url_without_property(classification_url) + " complete")
    results1 = tool.intersection(articles_keyword, articles_t_test)
    results2 = {}
    format_lt = datetime.datetime.strptime(lower_time, '%m/%d/%Y')
    format_ut = datetime.datetime.strptime(upper_time, '%m/%d/%Y')
    for title, info in results1.items():
        format_pt = datetime.datetime.strptime(info['publish_time'], '%d %B %Y')
        if format_lt <= format_pt <= format_ut:
            results2[title] = info
    return results2


# res = search_bmc(classification='Criminology-and-Criminal-Justice', keyword='p-value')
# print(len(res))
# print(res)
# dic1 = tool.search_keyword('https://crimesciencejournal.biomedcentral.com/articles', 't-test')
# dic2 = tool.search_keyword('https://crimesciencejournal.biomedcentral.com/articles', 'p-value')
# print(dic1)
# print(dic2)
# print(tool.intersection(dic1, dic2))
