import configparser
import logging
import codecs

from json import loads

log = logging.getLogger(__name__)

CONFIG_FILE = "./data/config.ini"

config = configparser.ConfigParser()
config.read_file(codecs.open(CONFIG_FILE, "r", "utf-8"))

#######
# Bot
#######
BOT_TOKEN = config.get("Bot", "bot_token", fallback=None)
if not BOT_TOKEN:
    raise Exception("'bot_token' is missing!")

BOT_PREFIX = config.get("Bot", "bot_prefix", fallback="!").strip(" ")
SPECIAL_USERS_IDS = [int(id_) for id_ in loads(config.get("Bot", "special_user_ids", fallback="[]"))]

log.info(f"Special users: {', '.join([str(a) for a in SPECIAL_USERS_IDS])}")

#######
# TriggerConfig
#######
GUILD_ID: int = config.getint("TriggerConfig", "guild_id")
VERIFICATION_TRIGGER_CHANNEL_ID: int = config.getint("TriggerConfig", "verification_trigger_channel_id")
VERIFICATION_TRIGGER_MESSAGE_ID: int = config.getint("TriggerConfig", "verification_trigger_message_id")
VERIFICATION_TRIGGER_EMOJI: str = config.get("TriggerConfig", "verification_trigger_emoji")

#######
# AuthConfig
#######
VERIFICATION_CHANNEL_CATEGORY_ID: int = config.getint("AuthConfig", "verification_channel_category_id")
VERIFICATION_SUCCESS_ROLE_ID: int = config.getint("AuthConfig", "verification_success_role_id")

#######
# Logging
#######
LOG_VERIFICATIONS_CONSOLE = config.getboolean("Logging", "log_verification_to_console")
LOG_VERIFICATIONS_CHANNEL = config.get("Logging", "log_verification_to_channel")
try:
    LOG_VERIFICATIONS_CHANNEL = int(LOG_VERIFICATIONS_CHANNEL)
except ValueError:
    LOG_VERIFICATIONS_CHANNEL = None

#######
# Status
#######
DISCORD_STATUS = config.get("Status", "DISCORD_STATUS")
DISCORD_STATUS_TYPE = config.get("Status", "DISCORD_STATUS_TYPE")
DISCORD_TWITCH_URL = config.get("Status", "DISCORD_TWITCH_URL")
