# LCD Network Monitor - Agent Documentation

## Overview
Raspberry Pi HAT LCD network monitor displaying WAN IP, ping times, wakatime, and time.

## Display Layout (16x2 LCD)
```
[WAN] [ping1] [ping2] [ping3]
[status]          [WT time] [clock]
```

## Key Files

- **main.py** - Main display loop, background WAN IP thread
- **utils.py** - Utility functions (ping, WAN IP, wakatime, time)
- **libs.py** - Screen helper functions
- **memcache_client.py** - Status updates from web server
- **web_server.py** - HTTP API for status updates

## Dependencies
```
requests
cachetools
ping3
dotenv
```

## Running
```bash
sudo python3 main.py
# Or with debug:
sudo python3 main.py --debug
```

## Make Commands
```bash
make  # Deploy to Pi (requires 'lcd' host in SSH config)
```

## Features

### WAN IP Display
- Fetches public IP from ifconfig.me (ifconfig.me was more reliable than ip-api.com from the Pi)
- Updated in background thread every 60 seconds
- Displays first octet only (e.g., "67")
- Falls back to "WAN" on failure

### Wakatime
- Requires `WAKATIME_API_KEY` in environment or `~/.wakatime.cfg` file
- Cached for 5 minutes
- Shows "WT ???" if not configured or fails

### Web Server Status
- POST to `/status` to update LCD status line
- memcache used for IPC between web server and main display

## Environment Variables
- `WAKATIME_API_KEY` - Optional, for wakatime tracking
- `.env` file is excluded from rsync (contains secrets)

## Common Issues

### LCD shows "WAN"
- Check network connectivity from the Pi
- ifconfig.me may be blocked - try curl from Pi to verify

### Wakatime shows "???"
- Ensure `WAKATIME_API_KEY` is set or `~/.wakatime.cfg` exists

### Service won't start
- Run with `--debug` to see errors
- Check probeLED.log
