from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
import time


def handle_http_requests(url):
    """
    Handle network requests
    :param url: string
    :return: response.text
    """
    response = requests.get(url)
    content = ''
    if response.status_code == 200:
        content = response.text
    else:
        print("Failed to fetch the URL " + url + ", status code:" + str(response.status_code))
    return content


def get_sub_classification_urls(classification):
    """
    get subclassification of a super classification
    :param the id of classification: string
           for Example: 'Criminology-and-Criminal-Justice'
    :return: dic of url of articles pagination
             an element in the list: 'https://crimesciencejournal.biomedcentral.com/articles'
    """

    url = "https://www.biomedcentral.com/journals"
    content = handle_http_requests(url)
    soup = BeautifulSoup(content, "html.parser")
    target_li = soup.find(id=classification)
    a_list = target_li.select('li li a:nth-of-type(1)')
    href_list = ['http:'+a['href']+'/articles' for a in a_list]
    return href_list


def get_links_of_all_pages(url):
    """
    to get how many page of articles and return the links of all pages as a list
    :param url: a concrete link that from a classification pagination
           for Example: https://crimesciencejournal.biomedcentral.com/articles
    :return: the link list of all pages in this classification
             an element in the list: https://crimesciencejournal.biomedcentral.com/articles?searchType=journalSearch&sort=PubDate&page=2
    """

    url_list = []
    content = handle_http_requests(url)

    # how many pages in this concrete classification
    soup = BeautifulSoup(content, "html.parser")
    li_list = soup.find_all(name='li', class_='c-pagination__item')
    pages = int(li_list[-2].find_all(['span', 'a'])[0].text.strip())
    # modify url of all pages
    for page in range(pages):
        # url_list.append(url + '?searchType=journalSearch&sort=PubDate&page=' + str(page + 1))
        url_list.append(url + '&page=' + str(page + 1))
    return url_list


def get_links_of_valid_pages(url_list, lower_time, upper_time):
    """

    :param url_list: all url of pagination
    :param lower_time:string:'01/01/2010'
    :param upper_time:
    :return:the link list of valid pages in this classification
    """
    valid_list = []
    start_time = datetime.strptime(lower_time, '%m/%d/%Y')
    end_time = datetime.strptime(upper_time, '%m/%d/%Y')
    for url in url_list:
        content = handle_http_requests(url)
        soup = BeautifulSoup(content, "html.parser")
        times = [pub_time.text for pub_time in soup.find_all(attrs={"itemprop": "datePublished"})]
        last_article_time = datetime.strptime(times[-1], '%d %B %Y')
        first_article_time = datetime.strptime(times[0], '%d %B %Y')
        if start_time < end_time < last_article_time < first_article_time:
            continue
        elif start_time < last_article_time < end_time < first_article_time:
            valid_list.append(url)
        elif start_time < last_article_time < first_article_time < end_time:
            valid_list.append(url)
        elif last_article_time < start_time < first_article_time < end_time:
            valid_list.append(url)
        elif last_article_time < first_article_time < start_time < end_time:
            break
    return valid_list


def get_all_article_links_in_a_page(url):
    """
    get all article links in a page
    :param url: the link of the page
           for example: https://crimesciencejournal.biomedcentral.com/articles?searchType=journalSearch&sort=PubDate&page=1
    :return: the link list of all articles in this page
    """

    content = handle_http_requests(url)
    soup = BeautifulSoup(content, 'html.parser')
    a_list = soup.find_all(name='a', itemprop='citation')
    url_list = [get_url_without_property(url) + a['href'].replace('/articles', '') for a in a_list]
    return url_list


def get_url_without_property(url):
    """
    Remove the property part of the UR
    :param url: string
    :return: url: string
    """
    return url.partition('?')[0]


def get_article_info(url):
    """
    get the article title, Publish time, authors, links within a page
    :param url: the link of pagination
           for example: https://biotechnologyforbiofuels.biomedcentral.com/articles?tab=keyword&searchType=journalSearch&sort=Relevance&query=t-test&page=2
    :return: a dictionary results. results[titles[i]] = {'title': titles[i], 'publish_time': times[i], 'url': links[i], 'authors': authors[i]}
    """
    results = {}
    content = handle_http_requests(url)
    soup = BeautifulSoup(content, "html.parser")
    authors = [author.text for author in soup.find_all("span", class_='c-listing__authors-list')]
    times = [pub_time.text for pub_time in soup.find_all(attrs={"itemprop": "datePublished"})]
    links = get_all_article_links_in_a_page(url)
    titles = [title.text for title in soup.find_all('a', attrs={'data-test': 'title-link'})]
    # len(authors) = len(times) = len(links) = len(titles) = 50
    for i in range(len(authors)):
        results[titles[i]] = {'title': titles[i], 'publish_time': times[i], 'url': links[i], 'authors': authors[i]}
    return results


def search_keyword(url, keyword, start_time, end_time):
    """
    use the search engine that comes with the page
    :param end_time:
    :param start_time:string:'01/01/2010'
    :param keyword: search keyword
           for example: https://actaneurocomms.biomedcentral.com/articles
    :param url: a concrete link that from a classification pagination
    :return: dict
             key: title of the article: string
             value: a dict:
                    1. 'title': string
                    2. 'publish_time': string
                    3. 'url': string
                    4. 'authors': string
    """
    url = url + '?tab=keyword&searchType=journalSearch&sort=PubDate&query=' + keyword
    articles = {}
    pages = get_links_of_valid_pages(get_links_of_all_pages(url), start_time, end_time)
    for page in pages:
        article = get_article_info(page)
        articles.update(article)
    return articles


def keyword_is_in(url, keyword):
    """
    Determine if the keyword is present in the article
    :param url: the link of the article
    :param keyword: User-defined keyword
    :return: boolean
    """
    content = handle_http_requests(url)
    soup = BeautifulSoup(content, "html.parser")
    results = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
    if len(results) == 0:
        return False
    else:
        return True


def intersection(dict1, dict2):
    """
    The intersection of two dictionary
    :param dict1:
    :param dict2:
    :return: res: list
    """
    s = set(dict1.keys()) & set(dict2.keys())
    results = dict1.copy()
    for ele in dict1:
        if ele not in s:
            del results[ele]
    return results


# print('search for p-value start: ' + time.asctime())
# p_values = search_keyword('https://actaneurocomms.biomedcentral.com/articles', 'p-value')
# print('the number of t-test articles:' + str(len(p_values)))
# print('search for p-value end: ' + time.asctime())
# print('search for t-test start: ' + time.asctime())
# t_tests = search_keyword('https://actaneurocomms.biomedcentral.com/articles', 't-test')
# print('the number of t-test articles:' + str(len(t_tests)))
# print('search for t-test end: ' + time.asctime())
# print('the intersection start: ' + time.asctime())
# results = intersection(p_values, t_tests)
# print('the number of t-test and p-value articles: ' + str(len(results)))
# print('the intersection end: ' + time.asctime())

# t_tests = search_keyword('https://bmcimmunol.biomedcentral.com/articles', 't-test')
# print(len(t_tests))
