import json
import requests
import sys
import util
import yaml
import os
mypath = os.path.abspath(os.path.dirname(sys.argv[0]))
with open(os.path.join(mypath, "keys.yml"), 'r') as stream:
    keys = yaml.safe_load(stream)



def query(company, page_results=10000):
    url = "https://api.rocketreach.co/v1/api/search"
    params = {"api_key": keys["rocketreach"]["key"],
        "company": "{}".format(company),
        "page_size":page_results}

    more_results = True
    while more_results:
        r = util.query(url, params)
        response = json.loads(r.text)
        
        if "error" in response or ("detail" in response and response["detail"] == "Invalid API key"):
            sys.stderr.write("Query error: {}\n".format(response) )
            sys.exit(1)

        if "profiles" in response:
            for profile in response["profiles"]:
                yield profile

        pagination = response["pagination"]
        if pagination["total"] > pagination["nextPage"]:
            params["start"] = pagination["nextPage"]
        else:
            more_results=False

def profiles(results):
    if "profiles" in results:
        for profile in results["profiles"]:
            yield profile

if len(sys.argv) != 2:
    sys.stderr.write("Usage: {} \"<comma separated list of titles>\".\n".format(sys.argv[0]))

titles = sys.argv[1].split(",")

for line in sys.stdin:

    line = json.loads(line)
    for company in line["results"]:

        name = company["name"]
        if "country" in company and company["country"] == "FI":

            for profile in query(name):
                if "current_title" not in profile:
                    continue


                for title in titles:
                    if title.lower() not in profile["current_title"].lower():
                        continue
                    if "contacts" not in company:
                        company["contacts"] = {"rocketreach": list()}
                    company["contacts"]["rocketreach"].append(profile)
    print(json.dumps(line))
