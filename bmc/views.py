import json

from django.http import HttpResponse
from django.shortcuts import render


def search(request):
    return render(request, 'bmc/searchMachine.html')


def afterselect(request):
    selected = request.GET['value']
    if selected == 'One':
        # res = {"1.1": "1.1", "1.2": "1.2", "1.3": "1.3", "1.4": "1.4"}
        res = "['1.1', '1.2', '1.3', '1.4']"
        return HttpResponse(res)
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
    print(request.GET['start'])
    print(request.GET['end'])
    # 这里写爬虫代码
    results = {'result1': 'result1', 'result2': 'result2', 'result3': 'result3'}
    searchresult = {'results': results, 'resultnumber': len(results), 'kriterien': kriterien, 'selectedKat': selectedKat}
    return HttpResponse(json.dumps(searchresult))