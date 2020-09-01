import configparser

CONFIG_FILE = "./data/config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

#######
# Auth
#######
BOT_TOKEN = config.get("Auth", "bot_token", fallback=None)
if not BOT_TOKEN:
    raise Exception("'bot_token' is missing!")

#######
# ServerConfiguration
#######
GUILD_ID: int = config.getint("ServerConfiguration", "guild_id")
AUTH_TRIGGER_CHANNEL_ID: int = config.getint("ServerConfiguration", "auth_trigger_channel_id")
AUTH_TRIGGER_MESSAGE_ID: int = config.getint("ServerConfiguration", "auth_trigger_message_id")
# TODO make sure which format is the right one for reactions
AUTH_REACTION_TRIGGER: str = config.get("ServerConfiguration", "auth_reaction_trigger")