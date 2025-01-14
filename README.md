<div align="center">
<img src="logo.png" width="350"">

# Bongo Bot
<br>

[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/Redhawk18/Bongo-Bot/.github%2Fworkflows%2Fdocker.yml)](https://github.com/Redhawk18/Bongo-Bot/pkgs/container/bongo-bot)
[![License](https://img.shields.io/github/license/Redhawk18/Bongo-Bot)](https://github.com/Redhawk18/Bongo-Bot/blob/main/LICENSE)

Due to an increasing harder and harder to deal with youtube source I have decided archive the project. It's fine to have a few hours of maintenance a month but if it breaks every week without a way to test it, it's too much for a free side project to handle. 

Designed to be a simple discord bot that play audios, inspiration is taken from the original [Rythm](https://rythm.fm/) bot.

[Click here to add the bot.](https://discord.com/api/oauth2/authorize?client_id=970048770836402176&permissions=6479220032&scope=applications.commands%20bot)
</div>

## Usage
All commands are slash commands and are self-documenting, regardless here are some examples. 

* `/play query: naruto opening 16`
* `/play query: chocolate insomnia autoplay: true`

The `play` command has three options.
* `autoplay` Continuously play songs without user querys, once enabled disconnect the bot to disable
* `next` If this track should be put at the front of the queue
* `start_time` Time stamp to start the video at, for example `1:34` or `1:21:19`

## Setup
* First create a `.env` with all the the following variables
```
#discord bot
DISCORD_TOKEN=

POSTGRES_DATABASE=bongo
POSTGRES_HOST=postgres
POSTGRES_PASSWORD=
POSTGRES_PORT=5432
POSTGRES_USER=postgres

LAVALINK_HOST=lavalink
LAVALINK_PASSWORD=
LAVALINK_PORT=2333
```

* Then run 
```
docker compose up -d
```

* Finally create the database with 
```
cat bongo.sql | docker exec -i bongo-bot-postgres-1 psql -U postgres
``` 
