# Telegram Bot for Willhaben new House Notification

## Build

```shell
echo "BOT_TOKEN=<your bot token>" > .env
```

```shell
docker compose build
docker compose up -d
```

## Render.com

1.	Log in to Render.com (free tier available).
2.	Click “New” → “Web Service” (or Background Worker on paid plans).
3.	Under Environment, choose Docker.
4.	Link your GitHub repo and branch.
5.	Optionally specify a custom Dockerfile path.
6.	Under Environment Variables, set BOT_TOKEN (and any others).
7.	Click Create Service.