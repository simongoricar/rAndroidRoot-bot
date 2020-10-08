# rAndroidRoot-bot
![](https://img.shields.io/badge/python-3.8%2B-blue)
![Docker Build Status](https://img.shields.io/docker/cloud/build/defaltsimon/androidrootbot)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/defaltsimon/androidrootbot)

Discord bot for the r/AndroidRoot discord server


# Setup
## 1. Installation
Before we begin: this project uses **[Poetry](https://python-poetry.org/)** as the package manager, see [this link](https://python-poetry.org/docs/#installation) for installation instructions.
Additionally, **Python 3.8** is required.

When you are ready, run `poetry install` in the directory where you cloned the bot. This will install the dependencies in a virtual env, as opposed to the global Python.

## 2. Configuration
Copy and fill out the provided configuration in `data/config.EXAMPLE.ini`. You will need to enter a bunch of IDs about your server and your bot token. 
If you want you can also customize the bot responses in `data/strings.json`, but keep in mind you need to use the name names for *{placeholders}*.

Also please note, the *Server Members Intent* is required for the `!verifyall` command.

## 3. Running
If you have completed the steps above, it's time to start the bot. Run either `poetry run python bot.py` or the provided shell scripts. 
I personally use [screen](https://linux.die.net/man/1/screen) to manage my bot (something like `screen -dmS AndroidRootBot poetry run python bot.py`), but that's not a requirement.

P.S. There is also a [docker-compose.yml](https://devhints.io/docker-compose) if you prefer using Docker.


# Commands

| Command Name  | Description   |
| ------------- | ------------- |
| !verify       | Starts the verification process (if you are not yet verified)  |
| !unverify     | Removes the verified role from you. Mostly a tester thing.  |
| !verifyall    | [**server owner only**] Gives every member in the current server the verified role.  |
| !about        | A bit about the bot, its version and its maker.  |
| !help         | General help message, just like this table.  |
| !ping         | Pong.  |
