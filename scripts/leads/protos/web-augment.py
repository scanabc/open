import json
import sys
import requests
import re

def check_web(domain):
    result = dict({"https": dict(), "http": dict()})

    def _check(scheme, url):
        url = scheme + "://" + url + "/"
        returndict = dict()
        try:
            r = requests.get(url, timeout=2)
            if len(r.history) > 1:
                first=r.history[0].url
                last=r.history[-1].url
                returndict["history"] = "{} -> {}".format(first, last)
                returndict["final dst"] = last
            title = re.search('(?<=<title>).+?(?=</title>)', r.text, re.DOTALL)
            if title:
                title = title.group().strip()
                returndict.update({"title": title })
            returndict.update({"return code": r.status_code, })
            return returndict
        except requests.exceptions.SSLError as e:
            return {"error": "bad cert"}
        except requests.exceptions.ReadTimeout as e:
            return {"error": "read timeout"}
        except requests.exceptions.ConnectionError as e:
            return {"error": "connection error"}
        except requests.exceptions.TooManyRedirects as e:
            return {"error": "too many redirects"}


        return None
    https_result = _check("https", domain)
    http_result = _check("http", domain)

    return {"https" : https_result, "http": http_result }


if __name__ == "__main__":
    checked_domains = dict()
    i=0

    for line in sys.stdin:
        i+=1
        if i % 10 == 0:
            sys.stderr.write("#")
            sys.stderr.flush()
            sys.stdout.flush()
        if i % 100 == 0:
            sys.stderr.write("{}\n".format(i))
        line = json.loads(line)
        #qualified = False
        #for company in line["results"]:
            #if "prequalified" in company and company["prequalified"] == True:
            #    qualified = True
            #    break
        #if not qualified:
        #    print(json.dumps(line))
        #    continue
        for domain in line["domains"]:
            if domain not in checked_domains:
                web_result = check_web(domain)
                checked_domains[domain] = web_result
            else:
                web_result = checked_domains[domain]
            if web_result != None and len(web_result) > 0:
                line["domains"][domain]["web"] = web_result

        print(json.dumps(line))