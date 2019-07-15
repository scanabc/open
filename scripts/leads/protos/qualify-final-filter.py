# coding=utf-8
import re
import sys
import json
import csv

whitelist = ["Data processing","financial","transport", "Water collection",
    "head offices","Child day-care","power production","Computer facilities",
    "Computer programming","Distribution of electricity","Electrical installation",
    "Gambling", "industrial machinery", "machinery for","pharmaceutical", "petroleum", "weapons",
    "dairies and cheese making","health care","information technology", "medical practice activities",
    "Trade of electricity","Transmission of electricity", "Wireless telecommunications","Private security"]
whitelist = re.compile("|".join(whitelist))


if __name__ == "__main__":

    for line in sys.stdin:
        line = json.loads(line)
        for company in line["results"]:
            company["qualified"] = False

            if "prequalified" not in company:
                sys.stderr.write("{} has not been prequalified. Please prequalify.\n".format(company["name"]))
                sys.exit(1)

            if company["prequalified"] == False:
                continue

            if "businesslines" not in company:
                continue

            if not whitelist.search(" & ".join(company["businesslines"])):
                continue
            company["qualified"] = True
        print(json.dumps(line))