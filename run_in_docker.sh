#!/bin/bash

echo "Running base scans..."
  docker run -v ${PWD}/results:/app/results -it --rm vautomator:latest python /app/run.py $*

# Fix perms..
sudo chown -R $(id -u):$(id -u) results

echo "Running HTTP* scans as appropriate..."
egrep 'open/tcp//*http' results/$*/*gnmap && {
  docker run -it --rm owasp/zap2docker-weekly zap-baseline.py -t https://$* | tee results/$*/zap-baseline.txt
  echo 
  echo "You may want to run:"
  echo "$ docker run -v "$(pwd)":/zap/wrk/:rw --dns 8.8.8.8 -u root -i owasp/zap2docker-weekly zap-full-scan.py -m 1 -T 5  -d -r report.html -t https://$*"
  echo "Manually for a more invasive scan"
}
egrep 'wp-content' results/$*/zap-baseline.txt && {
  docker run -it --rm wpscanteam/wpscan --url $* | tee results/$*/wpscan.txt
}


echo "Tarball'ing results"
tar -zcvf results/$*.tar.gz results/$*
