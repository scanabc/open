import json
import requests
import sys
import time
import util

def query(q):
    url = "http://avoindata.prh.fi/bis/v1/"
    return util.query(url + q)

def ytparse(ytjout, field, filterkey="language", filtervalue="EN", returnvaluefrom="name"):
    if "results" in ytjout:
        for result in ytjout["results"]:
            for lines in result[field]:
                if lines[filterkey] == filtervalue:
                    yield lines[returnvaluefrom]

def augment(result, ytjfield, newkey, filterkey="language", filtervalue="EN", returnvaluefrom="name"):

    for value in ytparse(ytj, ytjfield, filterkey=filterkey, filtervalue=filtervalue, returnvaluefrom=returnvaluefrom):
        if newkey not in result:
            result[newkey] = set()
        result[newkey].add(value)
    if newkey in result:
        result[newkey] = list(result[newkey])
    return result

if __name__ == "__main__":
    i=0
    for iline in sys.stdin:
        iline = json.loads(iline)
        i += 1
        if i % 10 == 0:
            sys.stderr.write("#")
            sys.stderr.flush()
        if i % 100 == 0:
            sys.stderr.write("\n{}\n".format(i))
            sys.stderr.flush()
        if "results" not in iline:
            continue

        for company in iline["results"]:
            # find results and yield a line per result
            out = dict()
            if "prequalified" in company and company["prequalified"] == True and \
                "businessId" in company and \
                "country" in company and company["country"] == "FI":

                ytj = query(company["businessId"])
                ytj = json.loads(ytj.text)

                company = augment(company, "businessLines", "businesslines")
                company = augment(company, "contactDetails", "telephones", returnvaluefrom="value")
                company = augment(company, "companyForms", "companyforms")

        print(json.dumps(iline))
    sys.stderr.write("\n")
