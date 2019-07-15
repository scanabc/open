import sys
import json
import util

def csv_out(tenants):
    import csv
    writer = csv.DictWriter(sys.stdout, fieldnames=["tenant","domains","tags"], extrasaction="ignore")
    writer.writeheader()
    for tenant in tenants:
        tenants[tenant]["domains"] = " & ".join(tenants[tenant]["domains"])
        tenants[tenant]["tags"] = " & ".join(tenants[tenant]["tags"])
        writer.writerow(tenants[tenant])

tenants=dict()
if __name__ == "__main__":
    for line in sys.stdin:
        line = json.loads(line)
        for office365 in util.office365_mxs(line):
            tenant = office365["tenant"]

            if tenant not in tenants:
                tenants[tenant] = dict()
            if "domains" not in tenants[tenant]:
                tenants[tenant]["domains"] = set()
            if "tags" not in tenants[tenant]:
                tenants[tenant]["tags"] = set()
            tenants[tenant].update({"tenant": tenant})
            tenants[tenant]["domains"].add(office365["unquoted"])

            if len(tenants[tenant]["domains"]) > 1:
                tenants[tenant]["tags"].add("multiple-domains")

            if office365["guessed_tenant"].lower() != office365["tenant"].lower():
                tenants[tenant]["tags"].add("differing-tenant")
                tenants[tenant].update({"guessed_tenant": office365["guessed_tenant"]})


    if len(sys.argv) == 1 or sys.argv[1] == "json":
        for tenant in tenants:
            tenants[tenant]["tags"] = list(tenants[tenant]["tags"])
            domains = tenants[tenant].pop("domains")
            tenants[tenant]["domains"] = dict()
            for domain in domains:
                tenants[tenant]["domains"][domain] = dict()
            print(json.dumps(tenants[tenant]))
        sys.exit(0)
    if sys.argv[1] == "csv":
        csv_out(tenants)
