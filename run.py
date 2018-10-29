# A minimally viable automated work-flow of VA Automation that we can incrementally improve on...
import sys
import os
import time
import re

def grep_file(filepath, term):
    """
    Simple grep-like function for files
    """
    with open(filepath) as fd:
        for line in fd:
            if re.search(term, line):
                return True
    return False

# Get targeting info
fqdn = sys.argv[1]

# Poor man's FQDN checking
if not fqdn:
  print("FQDN was not provided, please provide an FQDN (Example: foo.example.com)")
  exit(1) 

if "http" in fqdn:
  print("FQDN provided is not an FQDN, please use an FQDN (Example: foo.example.com)")
  exit(1) 

output_path = "/app/results/" + fqdn + "/"

# Create a location to store our outputs
try:
  os.stat(output_path)
except:
  os.mkdir(output_path) 

# Do procedure NMAP scans (save output to /app/results)
os.system("nmap -v -Pn -sT -n --top-ports 1000 --open -T4 -oA " + output_path + "scan_tcp_" + fqdn + " " + fqdn)
os.system("nmap -v -Pn -sU -sV -n -p 17,19,53,67,68,123,137,138,139,161,162,500,520,646,1900,3784,3785,5353,27015,27016,27017,27018,27019,27020,27960 --open -T4 -oA " + output_path + "scan_udp_" + fqdn + " " + fqdn)

# Do procedure dirb/ssh scans (save output to directory outside container)
nmap_tcp_gnmap_file = open("/app/results/" + fqdn + "/scan_tcp_" + fqdn + ".gnmap", "r")
lines = nmap_tcp_gnmap_file.readlines()
for line in lines:
  if (("Host:" in line) and ("Ports:" in line) and ("443/open/tcp" in line)):
    print("https is open, so we'll dirb it...")
    command = "/app/vendor/dirb222/dirb https://" + fqdn + "/ /app/vendor/dirb222/wordlists/common.txt -o /app/results/" + fqdn + "/https_dirb_common.txt"
    os.system(command)
  if (("Host:" in line) and ("Ports:" in line) and ("80/open/tcp" in line)):
    print("http is open, so we'll dirb it...")
    command = "/app/vendor/dirb222/dirb http://" + fqdn + "/ /app/vendor/dirb222/wordlists/common.txt -o /app/results/" + fqdn + "/http_dirb_common.txt"
    os.system(command)
  if (("Host:" in line) and ("Ports:" in line) and ("80/open/tcp" in line or "443/open/tcp" in line)):
    print("http/https is open, so we'll observatory it...")
    command = "curl -X POST -d '' https://http-observatory.security.mozilla.org/api/v1/analyze?host=" + fqdn + " > /app/results/" + fqdn + "/observatory.txt"
    max_retries = 300
    cur_retries = 0
    while (grep_file("/app/results/{}/observatory.txt".format(fqdn), "PENDING") and cur_retries < max_retries):
        cur_retries = cur_retries + 1
        os.system(command)
        time.sleep(1)
        print("Waiting for observatory scan results... (attempt {} of {})".format(cur_retries, max_retries))
  if (("Host:" in line) and ("Ports:" in line) and ("22/open/tcp" in line)):
    print("ssh is open, so we'll ssh_scan it...")
    command = "ssh_scan -t " + fqdn + " -o /app/results/" + fqdn + "/ssh_scan.txt"
    os.system(command)
