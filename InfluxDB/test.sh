#!/usr/bin/env bash
influx -database mesures -execute "SHOW MEASUREMENTS"
# ou
curl -G 'http://localhost:8086/query?pretty=true' --data-urlencode "db=mesures" --data-urlencode "q=SHOW MEASUREMENTS"