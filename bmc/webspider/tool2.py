import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


def handle_http_requests(url, header=None):
    """
    Handle network requests
    :param header:
    :param url: string
    :return: response.text
    """
    if header is None:
        header = {}
    response = requests.get(url, headers=header)
    content = ''
    if response.status_code == 200:
        content = response.text
        print("success to get the content of the URL " + url)
    else:
        print("Failed to fetch the URL " + url + ", status code:" + str(response.status_code))
    return content


def handle_http_requests2(url):
    """
    Handle network requests with selenium
    :param url: string
    :return: response.text
    """
    driver_path = "msedgedriver.exe"
    driver = webdriver.Edge(executable_path=driver_path)
    driver.get(url)
    html = driver.page_source
    # print(html)
    driver.quit()
    print(f"the url with {url} was opened")
    return html


def convert_date_form(date_str):
    """
    :param date_str: "12/31/2017"
    :return: new_date_str = "31 Dec 2017"
    """
    date = datetime.strptime(date_str, '%m/%d/%Y')
    new_date_str = datetime.strftime(date, '%d %b %Y')
    return new_date_str


def find_min_distance_between_regex_matches(text, string2):
    """
    regex1: the regex of t-test
    :param text: html content
    :param string2: the keyword string given by the user
    :return: if no match is found, return -1. Otherwise returns the minimum distance
    """
    # Find all matches for the first regular expression
    regex1 = re.compile(r'(<\w+>)*t(</\w+>)*[\s-]*test', re.IGNORECASE)
    regex2 = re.compile(rf'{regex_keyword(string2)}', re.IGNORECASE)

    matches1 = list(re.finditer(regex1, text))
    if not matches1:
        print("First match not found")
        return float('inf')

    # Find all matches for the second regular expression
    matches2 = list(re.finditer(regex2, text))
    if not matches2:
        print("Second match not found")
        return float('inf')

    # Calculate the distance between each pair of matched items and return the minimum value
    min_distance = float('inf')  # positive infinity
    for match1 in matches1:
        for match2 in matches2:
            distance = abs(match2.start() - match1.end())
            if distance < min_distance:
                min_distance = distance

    if min_distance == float('inf'):
        print("No matches found")
        return float('inf')

    return min_distance


def regex_keyword(string, regex=re.compile(r'\b[A-Za-z]\b', re.IGNORECASE)):
    """
    Allow individual letters to be wrapped in html tags in the keywords entered by the user
    :param string: the user-defined keyword
    :param regex:
    :return: the wrapped string
    """
    pattern = re.compile(regex)
    matches = pattern.finditer(string)
    indices = [match.span() for match in matches]
    indices = [(idx[0], idx[1]) for idx in indices]

    new_string = ""
    last_index = 0
    for index in indices:
        new_string += string[last_index:index[0]] + "(<\\w+>)*" + string[index[0]:index[1]] + "(</\\w+>)*"
        last_index = index[1]
    new_string += string[last_index:]
    result_string = new_string.replace(" ", "[\\s]*")

    # (<\w+>)*n(</\w+>)*[\s]*=[\s]3
    return result_string


def month_str_to_num(month):
    """
    :param month: the form as "Jan"
    :return: string as "1"
    """
    switcher = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }
    return switcher[month]


def generate_url(start_time, end_time, keyword):
    """
    Based on the user's input, generate the corresponding url
    :param start_time: 01 Jan 2017
    :param end_time: 31 Dec 2017
    :param keyword:
    :return: https://www.science.org/action/doSearch?field1=AllField&text1=t-test&field2
    =AllField&text2=p-value&field3=AllField&text3=&publication=&Ppub=&AfterMonth=1&AfterYear=2017&BeforeMonth=12
    &BeforeYear=2017
    """
    start_str = start_time.split()
    end_str = end_time.split()
    start_str[1] = month_str_to_num(start_str[1])
    end_str[1] = month_str_to_num(end_str[1])
    keyword = keyword.replace('=', '%3D')
    keyword = keyword.replace(' ', '')
    url = f'https://www.science.org/action/doSearch?field1=AllField&text1=t-test&field2=AllField&text2={keyword}&field3=AllField&text3=&publication=&Ppub=&AfterMonth={start_str[1]}&AfterYear={start_str[2]}&BeforeMonth={end_str[1]}&BeforeYear={end_str[2]}'
    return url


def get_last_related_article(html, keyword):
    """
    :param keyword: user defined keyword
    :param html: the source code of pagination url
    https://www.science.org/action/doSearch?field1=AllField&text1=t-test&field2=AllField&text2=p-value&field3=AllField&text3=&publication=&Ppub=&AfterMonth=1&AfterYear=2017&BeforeMonth=12&BeforeYear=2017&pageSize=20&startPage=0
    :return: dict: the last related article and the page
    {'article': 'https://', 'page': '2'}
    """
    max_page = get_last_page(html)
    # article = ''
    # result_page = ''
    current_page = int(max_page/14) + 1
    # To mark special cases: the last article on the previous page is relevant, the
    # first article on the next page is not
    tag = 0
    while True:
        html = html + f"&pageSize=20&startPage={current_page-1}"
        articles = get_all_articles(html)
        first_is_related = is_related(articles[0], keyword)
        last_is_related = is_related(articles[-1], keyword)
        if first_is_related and not last_is_related:
            result_page = str(current_page)
            article = binary_search(articles, keyword)
            break
        elif not first_is_related:
            current_page -= 1
            tag += 1
        elif last_is_related:
            if tag != 0:
                result_page = str(current_page)
                article = articles[-1]
                break
            current_page += 1
    return {'article': article, 'page': result_page}


def get_last_page(html):
    """
    :param html: the url of the current page
    :return: page: string
    """
    soup = BeautifulSoup(html, "html.parser")
    li_list = soup.find_all(name='li', class_='page-item')
    pages = li_list[-2].find_all('a')[0].text.strip()
    return pages


def is_related(url, keyword):
    """
    Determine if an article is related
    :param url: the url of the article
    :param keyword: user defined keyword
    :return: true or false
    """
    html = handle_http_requests2(url)
    distance = find_min_distance_between_regex_matches(html, keyword)
    return True if distance < 1000 else False


def get_all_articles(html):
    """
    get all articles in one page
    :param html:
    :return: url_list: ['url1', 'url2', 'url3', ...]
    """
    soup = BeautifulSoup(html, 'html.parser')
    h2_list = soup.find_all(name='h2', class_='article-title')
    url_list = ['https://www.science.org' + h2.find('a').get('href') for h2 in h2_list]
    return url_list


def binary_search(articles, keyword):
    """
    Find the last article that matches the criteria by the binary search method
    :param keyword: user defined keyword
    :param articles: the url list of all articles
    :return: html: the url of the last related article
    """
    low = 0
    high = len(articles) - 1
    while low <= high:
        mid = (low + high) // 2
        if is_related(articles[mid], keyword) and not is_related(articles[mid+1], keyword):
            return articles[mid]
        elif is_related(articles[mid], keyword) and is_related(articles[mid+1], keyword):
            low = mid + 1
        else:
            high = mid - 1
    return ""


def get_all_related_article(start_time, end_time, keyword, last_article):
    """

    :param start_time: "01 Jan 2017"
    :param end_time: "31 Dec 2017"
    :param keyword: "n = 3" the space is required between "="
    :param last_article: {"page": "3", "article": "https://"}
    :return: articles: {"Biomedicine":{"title": "Biomedicine", "url": "https://", "pdf": "https://", "authors": "...", "published time": "24 Jun 2017"}}
    """
    # f'https://www.science.org/action/doSearch?field1=AllField&text1=t-test&field2=AllField&text2={keyword}&field3=AllField&text3=&publication=&Ppub=&AfterMonth={start_str[1]}&AfterYear={start_str[2]}&BeforeMonth={end_str[1]}&BeforeYear={end_str[2]}'
    url_pages = [generate_url(start_time, end_time, keyword) + f'&pageSize=20&startPage={page}' for page in range(int(last_article["page"]))]
    articles = {}
    for i in range(len(url_pages)-1):
        html = handle_http_requests2(url_pages[i])
        dic = get_articles_info_in_one_page(html)
        articles.update(dic)
    html = handle_http_requests2(url_pages[-1])
    dic = get_only_related_articles_info(html, last_article)
    articles.update(dic)
    return articles


def get_articles_info_in_one_page(html):
    """

    :param html: the source code of a page
    :return: articles: {"Biomedicine":{"title": "Biomedicine", "url": "https://", "pdf": "https://", "authors": "...", "published time": "24 Jun 2017"}}
    """
    soup = BeautifulSoup(html, 'html.parser')
    all_divs = soup.find_all(name='div', class_='card-header')
    articles = {}
    for div in all_divs:
        title_with_space = div.find('a').text.strip().replace('\n', ' ')
        # Converts more than two consecutive spaces in a string to one space
        title = re.sub(r"\s{2,}", " ", title_with_space)
        url = 'https://www.science.org' + div.find('a').get('href')
        pdf = url.replace('/doi', '/doi/pdf') + '?download=true'
        authors_span = div.find(name='div', class_='authors').find_all('span')
        authors_list = [span.text for span in authors_span][1:]
        authors = 'by ' + ', '.join(authors_list)
        published_time = div.find('time').text
        articles[title] = {"title": title, "url": url, "pdf": pdf, "authors": authors, "published time": published_time}
    return articles


def get_only_related_articles_info(html, last_article):
    """

    :param html: the source code of the page
    :param last_article: {"page": "3", "article": "https://"}
    :return: articles: {"Biomedicine":{"title": "Biomedicine", "url": "https://", "pdf": "https://", "authors": "...", "published time": "24 Jun 2017"}}
    """
    soup = BeautifulSoup(html, 'html.parser')
    all_divs = soup.find_all(name='div', class_='card-header')
    articles = {}
    for div in all_divs:
        title_with_space = div.find('a').text.strip().replace('\n', ' ')
        # Converts more than two consecutive spaces in a string to one space
        title = re.sub(r"\s{2,}", " ", title_with_space)
        url = 'https://www.science.org' + div.find('a').get('href')
        pdf = url.replace('/doi', '/doi/pdf') + '?download=true'
        authors_span = div.find(name='div', class_='authors').find_all('span')
        authors_list = [span.text for span in authors_span][1:]
        authors = 'by ' + ', '.join(authors_list)
        published_time = div.find('time').text
        articles[title] = {"title": title, "url": url, "authors": authors, "published time": published_time}
        if url == last_article['article']:
            break
    return articles


def generate_diagram(start_time, end_time, articles):
    """

    :param start_time: 01 Jan 2017
    :param end_time: 31 Dec 2017
    :param articles: {"Biomedicine":{"title": "Biomedicine", "url": "https://", "pdf": "https://", "authors": "...", "published time": "24 Jun 2017"}}
    :return: time_stamp: If the time difference is less than or equal to one year
                         --> {'Jan 2017': 12, 'Feb 2017': 4, ...}
                         else
                         ---> {'2010': 103, '2011': 194, ...}
    """
    date1 = datetime.strptime(start_time, '%d %b %Y')
    date2 = datetime.strptime(end_time, '%d %b %Y')
    delta = (date2 - date1).days
    time_stamp = {}
    if delta > 365:
        for i, t in articles.items():
            date = datetime.strptime(t["published time"], '%d %b %Y')
            year = str(date.year)
            if year in time_stamp:
                time_stamp[year] += 1
            else:
                time_stamp[year] = 1
    else:
        for i, t in articles.items():
            date = datetime.strptime(t["published time"], '%d %b %Y')
            year_month = str(date.year) + '-' + str(date.month).zfill(2)
            if year_month in time_stamp:
                time_stamp[year_month] += 1
            else:
                time_stamp[year_month] = 1
    return time_stamp


def merge_diagram_articles(diagram, articles):
    """

    :param diagram:
    :param articles:
    :return:
    """
    result = {"articles": articles, "diagram": diagram}
    return result