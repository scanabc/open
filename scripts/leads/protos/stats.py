
import sys
import json
import util

def main():
    stats = dict()
    stats["records"] = 0
    stats["mx"] = 0
    stats["office365"] = 0
    stats["google"] = 0
    stats["aggregatetenants"] = 0
    tenants = dict()
    for line in sys.stdin:
        stats["records"] += 1
        line = json.loads(line)
        if "mx" in line:
            stats["mx"] += 1
            for record in line["mx"]:
                provider = util.provider(record["exchange"])
                if provider == "Office365":
                    stats["office365"] += 1
                    tenant = util.get_tenant(record["exchange"])
                    if tenant not in tenants:
                        tenants[tenant] = list()
                    tenants[tenant].append(line["unquoted"])


                elif provider == "Google":
                    stats["google"] += 1
    stats["tenants"] = len(set(tenants.keys()))
    for tenant in tenants:
        if len(tenants[tenant]) > 1:
            stats["aggregatetenants"] += 1
    return stats

if __name__ == "__main__":

    tenants=0
    records=0

    stats = main()
    print("Total records: {}".format(stats["records"]))
    print("Domains with MX-records: {}".format(stats["mx"]))
    print("Domains using Office365: {}".format(stats["office365"]))
    print("  Unique tenants: {}".format(stats["tenants"]))
    print("  Tenants serving more than one domain: {}".format(stats["aggregatetenants"]))
    print("Domains using Google: {}".format(stats["google"]))