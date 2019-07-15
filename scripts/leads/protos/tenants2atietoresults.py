import json
import sys
import re
import requests
import util

def query(q):
    url = "https://www.asiakastieto.fi/yritykset/haku"
    parameter_dict = {"type": "BUSINESS"}
    parameter_dict["q"] = q
    r = util.query(url, parameter_dict)
    return r.text

def results(text):

    #matches = list()
    for company in hit:
        match = dict()
        #print(company)
        for key in ["businessId","name","streetAddress","city","personnel","turnover","country"]:
            if key in company:
                match[key] = company[key]
        yield match

if __name__ == "__main__":
    #for line in sys.stdin:
    #    line = json.loads(line)
    #    print(line["tenant"], line["domains"])
    #file = open('aurejarvi.html','r')
    #text = file.read()


    for line in sys.stdin:

        line = json.loads(line)
        tenant = line["tenant"]
        tenant = tenant.replace("-fi","")
        querystring = tenant

        text = query(querystring)
        stick_with_it=True
        for hit in re.findall("searchResults: (.*), query", text):
            hit = json.loads(hit)
            if len(hit) == 0:
                print(json.dumps(line))
            else:
                for result in results(text):
                    if "results" not in line:
                        line["results"] = list()
                    line["results"].append(result)
                print(json.dumps(line))
