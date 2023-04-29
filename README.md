# Bongo Bot

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

TROLLED_USER_ID=

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


