#!/bin/sh

datadir=data-x/
domains=domains/

[ -d ${datadir}  ] || mkdir ${datadir}/

# remove head -100 for full run
echo 'mx'
gzcat ${domains}/fi_full.8ea886b4ca6c928b8f6b85b9657bfbb8.txt.gz |(head -50; egrep 'apotti.fi|kone.fi') |python3 domain2mx.py ${datadir}/cache.json >${datadir}/00-mx.json

echo 'office365'
cat ${datadir}/00-mx.json | python3 office365.py >${datadir}/01-o365.json

echo 'asiakastieto'
time cat ${datadir}/01-o365.json | head -10 | python3 tenants2atietoresults.py  > ${datadir}/02-o365-atieto.json

echo 'pre-qualify'
cat ${datadir}/02-o365-atieto.json  | python3 qualify-pre-filter.py  > ${datadir}/03-o365-atieto-prequalified.json

echo 'web-augment'
time cat ${datadir}/03-o365-atieto-prequalified.json |python3 web-augment.py > ${datadir}/04-o365-atieto-prequalified-web.json

echo 'ytj-augment'
time cat ${datadir}/04-o365-atieto-prequalified-web.json |python3 ytj-augment.py > ${datadir}/05-o365-atieto-prequalified-web-ytj.json

echo 'final-qualify'
cat ${datadir}/05-o365-atieto-prequalified-web-ytj.json |python3 qualify-final-filter.py >${datadir}/06-o365-atieto-prequalified-web-ytj-final.json

echo 'csv'
cat ${datadir}/06-o365-atieto-prequalified-web-ytj-final.json | python3 final2leadlist.py |(head -1 ;grep prequalified | egrep 'title-name|domain-contact') >${datadir}/o365-qualified.csv