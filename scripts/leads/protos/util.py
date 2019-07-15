import requests
import sys
import time
def query(url, param={}):

    keep_trying=True
    num_try=0
    while keep_trying:
        num_try += 1
        try:
            r = requests.get(url, param)
        except requests.exceptions.ConnectionError:
            sys.stderr.write("Connection error.\n")
            time.sleep(num_try*2)
            if num_try > 10:
                keep_trying=False
                sys.stderr.write("Giving up\n")
                sys.exit(1)
        keep_trying=False
    return r

def provider(record):
    if "protection.outlook.com" in record:
        return "Office365"
    elif "googlemail" in record:
        return "Google"
    else:
        return record

def tenant(exchange):
    return exchange.split(".")[0]

def guessed_tenant(domain):
    appendix = ""
    if "-" in domain:
        index = domain.index("-")
        appendixmap = {1: "0c", 2: "0e",3: "0i", 4: "01b", 5: "01c", 6: "01e", 7: "01i", 8: "02b", 9: "02c", 10: "02e", 11: "02i", 14: "03e", 18: "04e", 30: "07e" }
        if index in appendixmap:
            appendix = appendixmap[index]
    domain = domain.replace("-","")
    domain = domain.replace(".","-")
    domain = domain + appendix
    return domain

def office365_mxs(line):
    if "mx" in line:
        for record in line["mx"]:
            if provider(record["exchange"]) == "Office365":
                yield {"tenant": tenant(record["exchange"]),
                    "unquoted": line["unquoted"],
                    "guessed_tenant": guessed_tenant(line["unquoted"])
                    }

def get_tenant(record):
    return record.split(".")[0]