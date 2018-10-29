all: vautomator zap wpscan

vautomator:
	docker build -t vautomator .

zap:
	docker pull owasp/zap2docker-weekly

wpscan:
	docker pull wpscanteam/wpscan
