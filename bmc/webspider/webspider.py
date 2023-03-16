from datetime import datetime
import time

from bmc.webspider import tool
from bs4 import BeautifulSoup


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
    :param lower_time: string: '%m/%d/%Y'
    :param upper_time: string
    :param keyword: string
    :return: dict
             key: title of the article: string
             value: a dict:
                    1. 'title': string
                    2. 'publish_time': string
                    3. 'url': string
                    4. 'authors': string
    """
    start_time = datetime.strptime(lower_time, '%m/%d/%Y')
    end_time = datetime.strptime(upper_time, '%m/%d/%Y')
    results = {}
    classification_urls = tool.get_sub_classification_urls(classification)
    # classification_url: http://actaneurocomms.biomedcentral.com/articles
    for classification_url in classification_urls:
        articles_t_test = tool.search_keyword(classification_url, 't-test', lower_time, upper_time)
        for t, i in articles_t_test.items():
            publish_time = datetime.strptime(i['publish_time'], '%d %B %Y')
            if tool.keyword_is_in(i['url'], keyword) and start_time < publish_time < end_time:
                results[t] = i
        print("search for " + tool.get_url_without_property(classification_url) + " complete")
    return results


# res = search_bmc(classification='Criminology-and-Criminal-Justice', keyword='p-value')
# print(len(res))
# print(res)
# dic1 = tool.search_keyword('https://crimesciencejournal.biomedcentral.com/articles', 't-test')
# dic2 = tool.search_keyword('https://crimesciencejournal.biomedcentral.com/articles', 'p-value')
# print(dic1)
# print(dic2)
# print(tool.intersection(dic1, dic2))
