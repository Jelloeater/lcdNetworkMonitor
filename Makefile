default:
	uv export --no-dev --format requirements-txt --no-hashes | sed 's/==.*//' > requirements.txt
	rsync -av --delete --exclude .env --exclude '.env*' . lcd:/opt/lcdNetworkMonitor/
	ssh lcd 'cd /opt/lcdNetworkMonitor/; pip install -r requirements.txt  --break-system-packages'
	ssh lcd 'service lcd-api restart'
	ssh lcd 'service lcd restart'
