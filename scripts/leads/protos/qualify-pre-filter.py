import json
import sys


def trim(business, reason):
    return {"businessId": business["businessId"], "name": business["name"], "prequalified": False, "reason": reason}

if __name__ == "__main__":

    for line in sys.stdin:
        line = json.loads(line)
        if "results" in line:
            survives = list()
            for result in line["results"]:
                if "turnover" not in result:
                    survives.append(trim(result, "no turnover"))
                    continue
                if result["turnover"] < 5000000:
                    survives.append(trim(result, "<5M turnover"))
                    continue
                if result["personnel"] < 50:
                    survives.append(trim(result, "too few employees"))
                    continue
                if result["country"] != "FI":
                    survives.append(trim(result, "not FI"))
                    continue
                result["prequalified"] = True
                survives.append(result)
            line["results"] = survives
            print(json.dumps(line))
