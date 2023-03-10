import json

from django.http import HttpResponse
from django.shortcuts import render

from bmc.webspider import webspider


def search(request):
    return render(request, 'bmc/searchMachine.html')


def afterselect(request):
    selected = request.GET['value']
    if selected == 'One':
        classifications = webspider.find_classification('https://www.biomedcentral.com/journals')
        classifications = str(classifications)
        # res = {"1.1": "1.1", "1.2": "1.2", "1.3": "1.3", "1.4": "1.4"}
        return HttpResponse(classifications)
    elif selected == 'Two':
        res = {"2.1": "2.1", "2.2": "2.2", "2.3": "2.3", "2.4": "2.4"}
        return HttpResponse(json.dumps(res))
    else:
        res = {"3.1": "3.1", "3.2": "3.2", "3.3": "3.3", "3.4": "3.4"}
        return HttpResponse(json.dumps(res))


def result(request):
    selectedWeb = request.GET['selectedWeb']
    selectedKat = request.GET['selectedKat']
    kriterien = request.GET['kriterien']
    start = request.GET['start']
    end = request.GET['end']
    # 这里写爬虫代码
    results = webspider.search_bmc(classification=selectedKat.replace('_', '-'), lower_time=start, upper_time=end, keyword=kriterien)
    # results = {'result1': 'result1', 'result2': 'result2', 'result3': 'result3'}
    searchresult = {'results': results, 'resultnumber': len(results), 'kriterien': kriterien, 'selectedKat': selectedKat}
    return HttpResponse(json.dumps(searchresult))
