import json
import os

from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from bmc.webspider import webspider

import matplotlib.pyplot as plt
import io
import base64


class SaveItem:
    selectedWeb = ""
    selectedKat = ""
    kriterien = ""
    start = 0
    end = 0
    searchresult = {}


# Jumping the page to searchMachine.html
def search(request):
    return render(request, 'bmc/searchMachine.html')


# Change the content of the second drop-down box after the first one has been selected
def after_select(request):
    selected = request.GET['value']
    if selected == 'BMC-Journal':
        classifications = webspider.find_classification('https://www.biomedcentral.com/journals')
        classifications = str(classifications)
        return HttpResponse(classifications)
    elif selected == 'Two':
        res = {"2.1": "2.1", "2.2": "2.2", "2.3": "2.3", "2.4": "2.4"}
        return HttpResponse(json.dumps(res))
    else:
        res = {"3.1": "3.1", "3.2": "3.2", "3.3": "3.3", "3.4": "3.4"}
        return HttpResponse(json.dumps(res))


# Call the webspider to search the result and transfer to the front-end
def result(request):
    selectedWeb = request.GET['selectedWeb']
    selectedKat = request.GET['selectedKat']
    kriterien = request.GET['kriterien']
    start = request.GET['start']
    end = request.GET['end']
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


# Save the result and the condition information in workspace
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


# Download all the selected pdf in a special folder in the workspace
def download_pdf(request):
    path = os.getcwd()
    timedate = datetime.now().date().__str__().replace("-", "_") + "_" + datetime.now().strftime("%H_%M_%S")
    if not os.path.exists(timedate):
        os.mkdir(path + "\\" + timedate)
        for i in range(0, 10):
            filename = i.__str__() + ".txt"
            with open(path + "\\" + timedate + "\\" + filename, "w", encoding="utf-8") as file:
                file.write("i")
    print("download successfully")
    return HttpResponse("Successfully")


# Show the statistical result of the Search
def static_result(request):
    x = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
    y = [10, 20, 30, 40, 50, 60, 70]
    plt.bar(x, y)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    base64_image = base64.b64encode(buffer.getvalue()).decode()

    context = {'chart_data': base64_image}
    return render(request, 'bmc/static.html', context)
