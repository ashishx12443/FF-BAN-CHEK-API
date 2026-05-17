# Free Fire Ban Check API

A simple Flask API to check whether a Free Fire player UID is banned or not.

This project checks the ban status from Garena's Free Fire anti-hack endpoint. It also tries to fetch player nickname and region from Shop2Game, but that part is optional because Shop2Game can block datacenter/server IPs.

## Features

- Check ban status using Free Fire UID
- Returns banned / not banned status
- Shows ban period when available
- Tries to fetch nickname and region
- Works with Flask and Gunicorn
- Ready for VPS hosting
- Vercel configuration included

## API Endpoint

```text
GET /bancheck?uid=PLAYER_ID
```

Example:

```text
http://127.0.0.1:5000/bancheck?uid=123456789
```

## Success Response

```json
{
  "uid": "123456789",
  "nickname": "PlayerName",
  "region": "BD",
  "ban_status": "Not banned",
  "ban_period": null
}
```

If the player is banned:

```json
{
  "uid": "123456789",
  "nickname": "PlayerName",
  "region": "BD",
  "ban_status": "Banned for 2 months",
  "ban_period": "2 months"
}
```

## When Player Info Is Blocked

On some hosting providers, Shop2Game may block the server IP. In that case, the API can still return ban status:

```json
{
  "uid": "123456789",
  "nickname": null,
  "region": null,
  "ban_status": "Not banned",
  "ban_period": null,
  "player_info_warning": "Player info API returned HTTP 403"
}
```

## Error Responses

Missing UID:

```json
{
  "error": "UID parameter is required"
}
```

Invalid UID:

```json
{
  "error": "UID must contain only numbers"
}
```

Ban status API failed:

```json
{
  "error": "Ban status API request failed: ..."
}
```

## Local Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask app:

```bash
python app.py
```

Local API URL:

```text
http://127.0.0.1:5000/bancheck?uid=PLAYER_ID
```

## VPS Hosting

VPS hosting is recommended because Vercel and Render use shared datacenter IPs, and those IPs may be blocked by Garena or Shop2Game.

First, test the Garena endpoint from your VPS:

```bash
curl "https://ff.garena.com/api/antihack/check_banned?lang=en&uid=PLAYER_ID"
```

If this returns JSON, the API should work on your VPS.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run with Gunicorn:

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

Your API will be available at:

```text
http://YOUR_VPS_IP:5000/bancheck?uid=PLAYER_ID
```

## Production Setup With Systemd

Create a service file:

```bash
sudo nano /etc/systemd/system/freefire-ban-api.service
```

Example service:

```ini
[Unit]
Description=Free Fire Ban Check API
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/FREE-FIRE-BAN-CHECK-API-SORCE
ExecStart=/usr/local/bin/gunicorn app:app --bind 0.0.0.0:5000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl start freefire-ban-api
sudo systemctl enable freefire-ban-api
```

Check logs:

```bash
sudo journalctl -u freefire-ban-api -f
```

## Optional Nginx Reverse Proxy

Install Nginx:

```bash
sudo apt install nginx
```

Example Nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Vercel / Render Note

This project includes `vercel.json`, but Vercel or Render may not work reliably because:

- They use shared datacenter IPs
- Garena or Shop2Game may block those IPs
- Shop2Game uses DataDome protection
- Hardcoded cookies or tokens can expire

If Vercel/Render returns timeout, 403, invalid JSON, or blocked responses, use a VPS instead.

## Files

```text
app.py            Main Flask API source
requirements.txt  Python dependencies
vercel.json       Vercel deployment config
README.md         Project documentation
```

## Important Notes

- This API depends on third-party endpoints.
- If Garena changes the endpoint, response format, or security rules, the API may need updates.
- Do not depend on hardcoded cookies for long-term production usage.
- VPS IP quality matters. If your VPS IP is blocked, try another VPS provider or IP.

## License

Use this project for educational and personal API testing purposes.
