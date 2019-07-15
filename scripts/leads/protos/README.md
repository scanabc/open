# Turn domains into leads

In short:

* Get country TLDs from domainlist.io (~250k) (see domains/)
* Check whose MX point to O365
* Scrape company information from Asiakastieto
* Prequalify with turnover
* Fetch http,https web pages for a domain, extrac title, redirects and some errors
* Fetch YTJ details for FI companies
* Qualify further with YTJ info
* Produce the final CSV, assist manual work with score and comparing web title <-> domain <-> YTJ info domain

## How to use

See example.sh for an example.

## References

* Domains from <https://domainlists.io>

## Stats

```console
cat datadir/00-mx.json | python3 stats.py
```

## tenants2atietoresults.py

* This will give false positives too.
* This will also give false negatives. We could reduce the amounts of false negatives, but enough results for now anyway.
* We will narrow down the list in next step.
* Hopefully the final list is small enough for some manual work.

## ytj-augment

Takes "businessId" as input and augments businessline, telephones and companyforms for FI companies with over 5M revenue.

* Does not return data for at least several non-OY-types, such as "Aatteellinen yhdistys" or "R.Y."
* Will not try to augment entires which Asiakastieto has not provided "FI" country code, as there would not be results from YTJ

## rocketreach.py

* Current strategy: grab as many results and filter locally instead of running a query per title.
  * Results seem to be a bit incosistent, running the same command two times sometimes yields different results.
  * Because of this, we might want to consider running company + title searches instead of one big company search with local filtering.
