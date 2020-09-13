import configparser
import codecs

CONFIG_FILE = "./data/config.ini"

config = configparser.ConfigParser()
config.read_file(codecs.open(CONFIG_FILE, "r", "utf-8"))

#######
# Auth
#######
BOT_TOKEN = config.get("Bot", "bot_token", fallback=None)
if not BOT_TOKEN:
    raise Exception("'bot_token' is missing!")

#######
# ServerConfiguration
#######
GUILD_ID: int = config.getint("TriggerConfig", "guild_id")
AUTH_TRIGGER_CHANNEL_ID: int = config.getint("TriggerConfig", "auth_trigger_channel_id")
AUTH_TRIGGER_MESSAGE_ID: int = config.getint("TriggerConfig", "auth_trigger_message_id")
AUTH_TRIGGER_EMOJI: str = config.get("TriggerConfig", "auth_trigger_emoji")

AUTH_CHANNEL_CATEGORY_ID: int = config.getint("AuthConfig", "auth_channel_category_id")
AUTH_SUCCESS_ROLE_ID: int = config.getint("AuthConfig", "auth_success_role_id")
