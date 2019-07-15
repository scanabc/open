import sys
import urllib.parse
import json
import dns.resolver
import time

prev_results = sys.argv[1]
try:
    with open(prev_results) as json_file:
        domains = json.load(json_file)
        num_of_cached_domains=len(domains.keys())
        sys.stderr.write("{} domains loaded\n".format(num_of_cached_domains))
except IOError:
    domains = dict()

i=0
cache=0
interval=100
for line in sys.stdin:
    i += 1

    line = line.rstrip()
    domain = urllib.parse.urlparse(line)
    domain = domain.geturl()
  
    #domain = domain.decode('utf-8')
    if domain not in domains:
        #time.sleep(0.5)
        domains[domain] = {"seen": "2019-07-09", "unquoted": line}
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2
        resolver.lifetime = 2
        try:
            for rdata in resolver.query(line,'MX'):
                if "mx" not in domains[domain]:
                    domains[domain]["mx"] = list()
                domains[domain]["mx"].append({"preference": rdata.preference, "exchange": rdata.exchange.to_text()})
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout, TypeError):
            pass
    else:
        cache += 1
    print(json.dumps(domains[domain]))
    if i % interval == 0:
        sys.stderr.write("Processed: {}, {} from cache\n".format(i,cache))

        with open(prev_results, 'w') as json_file:
            sys.stderr.write("Writing cache....")
            json.dump(domains, json_file)
            sys.stderr.write("done\n")


