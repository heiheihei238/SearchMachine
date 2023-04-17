import json
import os

import requests
import io

from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from bmc.webspider import webspider


class SaveItem:
    selectedWeb = ""
    selectedKat = ""
    kriterien = ""
    start = 0
    end = 0
    searchresult = {}


def search(request):
    return render(request, 'bmc/searchMachine.html')


def afterselect(request):
    selected = request.GET['value']
    if selected == 'BMC-Journal':
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
    results = webspider.search_bmc(classification=selectedKat.replace('_', '-'), lower_time=start, upper_time=end,
                                   keyword=kriterien)
    # results = {'result1': 'result1', 'result2': 'result2', 'result3': 'result3'}
    searchresult = {'results': results, 'resultnumber': len(results), 'kriterien': kriterien,
                    'selectedKat': selectedKat}
    SaveItem.searchresult = results
    SaveItem.selectedWeb = selectedWeb
    SaveItem.selectedKat = selectedKat
    SaveItem.kriterien = kriterien
    SaveItem.start = start
    SaveItem.end = end
    return HttpResponse(json.dumps(searchresult))


def save(request):
    data = ["Journal:" + SaveItem.selectedWeb, "Classify: " + SaveItem.selectedKat, "Criteria: " + SaveItem.kriterien,
            "start "
            "time: " + SaveItem.start.__str__(), "end time: " + SaveItem.end.__str__()]
    result = SaveItem.searchresult
    filename = "savedResult.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for line in data:
            file.write(line + "\n")
    with open(filename, "a", encoding="utf-8") as file:
        for key in result:
            file.write("\n")
            for subkey in result[key]:
                file.write(result[key][subkey] + "\n")
    print("saved successfully")
    return HttpResponse("Successfully")


def download_pdf(request):
    path = os.getcwd() + '\\' + datetime.now().date().__str__().replace("-", "_")
    os.mkdir(path)
    for i in range(0,10):
        filename = i.__str__() + ".txt"
        with open(path + "\\" + filename, "w", encoding="utf-8") as file:
            file.write("i")
    print("download successfully")
    return HttpResponse("Successfully")
