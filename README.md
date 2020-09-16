# rAndroidRoot-bot
![](https://img.shields.io/badge/python-3.8%2B-blue)

Discord bot for the r/AndroidRoot discord server


## 1. Installation
Before we begin: this project uses **[Poetry](https://python-poetry.org/)** as the package manager, see [this link](https://python-poetry.org/docs/#installation) for installation instructions.
Additionally, **Python 3.8** is required.

When you are ready, run `poetry install` in the directory where you cloned the bot. This will install the dependencies in a virtual env, as opposed to the global Python.

## 2. Configuration
Copy and fill out the provided configuration in `data/config.EXAMPLE.ini`. You will need to enter a bunch of IDs about your server and your bot token.
If you want you can also customize the bot responses in `data/strings.json`, but keep in mind you need to use the name names for *{placeholders}*.

## 3. Running
If you have completed the steps above, it's time to start the bot. Run either `poetry run python bot.py` or the provided shell scripts. 
I personally use [screen](https://linux.die.net/man/1/screen) to manage my bot (something like `screen -dmS AndroidRootBot poetry run python bot.py`), but that's not a requirement.
