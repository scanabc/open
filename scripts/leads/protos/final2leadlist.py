import sys
import json
import csv

def get_web_item(line, web_target):
    def _dig_item(domain,target):
        targets = list()
        web = domain["web"]
        for schema in ["https", "http"]:
            if target in web[schema]:
                targets.append("{}/{}: {}".format(domain_str, schema, domain["web"][schema][target]))

        return targets

    domains = line["domains"].keys()
    items = list()

    for domain_str in domains:
        domain = line["domains"][domain_str]
        if "web" not in domain:
            continue

        items = _dig_item(domain, web_target)
        if len(items) > 0:
            return " & ".join(items)

    return False

def web_sanitize(line):

    redirects = get_web_item(line,"final dst")
    if redirects:
        line.update({"redirects to": redirects })

    title = get_web_item(line, "title")
    if title:
        line.update({"web info": title})
    else:
        error = get_web_item(line,"error")
        if error:
            line.update({"web info": error})
    return line

def debug(msg):
    sys.stderr.write("DEBUG: "+ msg +"\n")

def score(line, company):
    def _match_title_name(line, company):
        for domain in line["domains"]:

            if "web" not in line["domains"][domain]:
                continue

            for scheme in ["http", "https"]:
                if "title" in line["domains"][domain]["web"][scheme]:
                    title = line["domains"][domain]["web"][scheme]["title"]
                    name = company["name"]
                    for titleword in title.split(" "):
                        if titleword.lower() == "oy":
                            continue
                        if titleword.isdigit() and len(titleword) < 4:
                            continue
                        if len(titleword) < 3:
                            continue

                        for nameword in name.split(" "):
                            if titleword.lower() == nameword.lower():
                                return "title-name-match"
        return False

    def _match_final_web_domain_name(line, company):
        for line_domain in line["domains"]:
            if "web" not in line["domains"][line_domain]:
                continue

            for scheme in ["http", "https"]:
                web = line["domains"][line_domain]["web"][scheme]
                if "final dst" in web and line_domain in web["final dst"]:
                    return "domain-webdomain-match"

        return False

    def _match_ytj_contact_domain(line, company):
        for line_domain in line["domains"]:
            # YTJ uses telephone records for web addresses too
            if "telephones" not in company:
                return False
            for contact in company["telephones"]:
                if line_domain in contact:
                    return "domain-contact-match"
        return False

    company["matches"] = set()

    match = _match_title_name(line, company)
    if match != False:
        company["matches"].add(match)
        company["score"] += 1

    match = _match_final_web_domain_name(line, company)
    if match != False:
        company["matches"].add(match)
        company["score"] += 3

    match = _match_ytj_contact_domain(line, company)
    if match != False:
        company["matches"].add(match)
        company["score"] += 3

    if len(company["matches"]) == 0:
        company.pop("matches")
    else:
        company["matches"] = " & ".join(company["matches"])

    if "qualified" in company and company["qualified"] == True:
        company["score"] += 2
    return company

if __name__ == "__main__":
    fields = ["score", "tenant", "domains_str", "prequalified", "matches","name",
        "businessId","personnel","turnover","turnperperson", "businesslines","city",
        "country","redirects to","web info", "contact_str"]
    writer = csv.DictWriter(sys.stdout, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for line in sys.stdin:
        line = json.loads(line)

        line = web_sanitize(line)


        line["domains_str"] = " & ".join(line["domains"])

        for company in line["results"]:
            company["score"] = 0


            if "name" not in company:
                continue

            if "prequalified" in company and company["prequalified"]:
                company["prequalified"] = "prequalified"
            else:
                reason = ""
                if "reason" in company:
                    reason = company["reason"]
                company["prequalified"] = "unqualified: " + reason

            company = score(line, company)
            if "turnover" in company and "personnel" in company:
                company.update({"turnperperson": round(company["turnover"] / company["personnel"])})
            for merge in ["telephones", "businesslines", "companyforms"]:
                if merge in company:
                    company[merge] = " & ".join(company[merge])

            for copy_value in ["tenant", "domains_str", "web info", "redirects to"]:
                if copy_value in line:
                    company.update({copy_value: line[copy_value]})

            if "contacts" in company:
                for source in company["contacts"]:
                    for contact in company["contacts"][source]:
                        contact_list = list()
                        if "contact_str" not in company:
                            company["contact_str"] = list()
                        for key in ["name", "current_title", "current_employer"]:
                            if key in contact:
                                contact_list.append(contact[key])
                        company["contact_str"].append(" / ".join(contact_list))
            if "contact_str" in company:
                company["contact_str"] = " & ".join(company["contact_str"])
            # choose what to write

            writer.writerow(company)