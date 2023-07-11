import json
import os
import requests

from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from bmc.webspider import webspider
from bmc.webspider import webspider2

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
    diagram = {}


def welcome(request):
    return render(request, 'bmc/welcomePage.html')


# Jumping the page to searchMachine.html
def search(request, journal):
    selected = journal
    classifications = ""
    if selected == 1:
        classifications = webspider.find_classification('https://www.biomedcentral.com/journals')
        classifications = str(classifications)
    elif selected == 2:
        classifications = ["None"]
    else:
        classifications = webspider.find_classification("https://plos.org/")
        classifications = str(classifications)
    return render(request, 'bmc/searchMachine.html', {"journal": journal, "classification": json.dumps(classifications)})


# Change the content of the second drop-down box after the first one has been selected
def after_select(request):
    selected = request.GET['value']
    if selected == 'BMC-Journal':
        classifications = webspider.find_classification('https://www.biomedcentral.com/journals')
        classifications = str(classifications)
        return HttpResponse(classifications)
    elif selected == 'Science-Translational-Medicine':
        res = {"None": "None"}
        return HttpResponse(json.dumps(res))
    else:
        classifications = webspider.find_classification("https://plos.org/")
        classifications = str(classifications)
        return HttpResponse(classifications)


# Call the webspider to search the result and transfer to the front-end
def result(request):
    selectedWeb = request.GET['selectedWeb']
    selectedKat = request.GET['selectedKat']
    kriterien = request.GET['kriterien']
    start = request.GET['start']
    end = request.GET['end']
    if selectedWeb == "BMC-Journal":
        results = webspider.search_bmc(classification=selectedKat.replace('_', '-'), lower_time=start, upper_time=end,
                                       keyword=kriterien)
        searchresult = {'results': results, 'resultnumber': len(results), 'kriterien': kriterien,
                        'selectedKat': selectedKat}
        SaveItem.searchresult = results
        SaveItem.selectedWeb = selectedWeb
        SaveItem.selectedKat = selectedKat
        SaveItem.kriterien = kriterien
        SaveItem.start = start
        SaveItem.end = end
        return HttpResponse(json.dumps(searchresult))
    elif selectedWeb == "Science-Translational-Medicine":
        results = webspider2.search_science(start, end, kriterien)
        searchresult = {'results': results['articles'], 'resultnumber': len(results['articles']),
                        'kriterien': kriterien,
                        'selectedKat': selectedKat}
        SaveItem.searchresult = results['articles']
        SaveItem.selectedWeb = selectedWeb
        SaveItem.selectedKat = selectedKat
        SaveItem.kriterien = kriterien
        SaveItem.start = start
        SaveItem.end = end
        SaveItem.diagram = results['diagram']
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
    index = request.GET['index']
    selected = eval('[' + index + ']')
    print(selected)
    path = os.getcwd()
    timedate = datetime.now().date().__str__().replace("-", "_") + "_" + datetime.now().strftime("%H_%M_%S")
    if not os.path.exists(timedate):
        os.mkdir(path + "\\" + timedate)
        location = 0
        for i in SaveItem.searchresult:
            if location in selected:
                response = requests.get(SaveItem.searchresult[i]['pdf'])
                bytes_io = io.BytesIO(response.content)
                with open(path + "\\" + timedate + "\\" + SaveItem.searchresult[i]['title'] + ".PDF", mode='wb') as f:
                    f.write(bytes_io.getvalue())
            location += 1
    print("download successfully")
    return HttpResponse("Successfully")


# Show the statistical result of the Search
def static_result(request):
    x = list(SaveItem.diagram.keys())
    print(x)
    y = list(SaveItem.diagram.values())
    print(y)
    plt.bar(x, y)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    base64_image = base64.b64encode(buffer.getvalue()).decode()

    context = {'chart_data': base64_image}
    return render(request, 'bmc/static.html', context)
