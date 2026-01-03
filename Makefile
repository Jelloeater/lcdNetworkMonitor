default:
	uv export --no-dev --format requirements-txt --no-hashes | sed 's/==.*//' > requirements.txt
	rsync -av --delete . lcd:/opt/lcdNetworkMonitor/
	ssh lcd 'cd /opt/lcdNetworkMonitor/; pip install -r requirements.txt  --break-system-packages'
	ssh lcd 'service lcd restart'
