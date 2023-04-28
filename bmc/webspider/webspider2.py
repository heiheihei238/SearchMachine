from bmc.webspider import tool2


def search_science(start_time, end_time, keyword):
    """
    :param start_time: "01/01/2017"
    :param end_time: "31/12/2017"
    :param keyword: "n = 3" (the user must input space beside special symbols such as "=")
    :return: result:
            {'diagram':{'2017-05': 1, '2017-11': 2, '2017-02': 1, '2017-04': 2, '2017-10': 2},
             'articles':{'BMP8A sustains spermatogenesis by activating both SMAD1/5/8 and SMAD2/3 in spermatogonia':
                            {'title': 'BMP8A sustains spermatogenesis by activating both SMAD1/5/8 and SMAD2/3 in spermatogonia',
                             'url': 'https://www.science.org/doi/10.1126/scisignal.aal1910',
                             'pdf': 'https://www.science.org/doi/pdf/10.1126/scisignal.aal1910?download=true',
                             'authors': 'by Fang-Ju Wu, Ting-Yu Lin, Li-Ying Sung, Wei-Fang Chang, Po-Chih Wu, Ching-Wei Luo',
                             'published time': '02 May 2017'},
                         'Arabidopsis ATXR2 deposits H3K36me3 at the promoters of LBD genes to facilitate cellular dedifferentiation':
                            {'title': 'Arabidopsis ATXR2 deposits H3K36me3 at the promoters of LBD genes to facilitate cellular dedifferentiation',
                            'url': 'https://www.science.org/doi/10.1126/scisignal.aan0316',
                            'pdf': 'https://www.science.org/doi/pdf/10.1126/scisignal.aan0316?download=true',
                            'authors': 'by Kyounghee Lee, Ok-Sun Park, Pil Joon Seo',
                            'published time': '28 Nov 2017'}, ...
                         }
            }
    """
    format_start_time = tool2.convert_date_form(start_time)
    format_end_time = tool2.convert_date_form(end_time)
    url = tool2.generate_url(format_start_time, format_end_time, keyword)
    html = tool2.handle_http_requests2(url)
    last_related_article = tool2.get_last_related_article(url, html, keyword)
    articles = tool2.get_all_related_article(format_start_time, format_end_time, keyword, last_related_article)
    diagram = tool2.generate_diagram(format_start_time, format_end_time, articles)
    result = tool2.merge_diagram_articles(diagram, articles)
    return result
