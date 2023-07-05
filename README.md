<div align="center">
<img src="logo.png" width="350"">

# Bongo Bot
<br>

[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/Redhawk18/Bongo-Bot/.github%2Fworkflows%2Fdocker.yml)](https://github.com/Redhawk18/Bongo-Bot/pkgs/container/bongo-bot)
[![License](https://img.shields.io/github/license/Redhawk18/Bongo-Bot)](https://github.com/Redhawk18/Bongo-Bot/blob/main/LICENSE)

Designed to be a simple discord bot that play audios, inspiration is taken from the original [Rythm](https://rythm.fm/) bot.
</div>

## Usage
All commands are slash commands and are self-documenting, regardless here are some examples. 
`/play query: chainsaw man ending 4`

## Setup
* First create a `.env` with all the the following variables
```
#discord bot
DISCORD_TOKEN=

DATABASE_DATABASE=
DATABASE_USER=
DATABASE_HOST=postgres #docker only
#DATABASE_HOST=localhost #local only
DATABASE_PORT=
DATABASE_PASSWORD=

LAVALINK_HOST=lavalink #docker only
#LAVALINK_HOST=localhost #local only
LAVALINK_PORT=
LAVALINK_PASSWORD=

#postgres
POSTGRES_USER=
POSTGRES_PASSWORD=

#pgadmin
PGADMIN_DEFAULT_EMAIL=
PGADMIN_DEFAULT_PASSWORD=
PGADMIN_PORT=
```

---
### Docker option

* Comment out the local lines in `.env` 
* Run `docker compose up -d`

---
### Local option

* Comment out docker lines in `.env`
* Comment out the `discord-bot` container in `docker-compose.yml`
* Run `docker compose up -d`
* Run `pip3 install -r requirements.txt`
* Start the discord bot with `python3 src/main.py`


