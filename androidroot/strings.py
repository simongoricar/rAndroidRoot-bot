import logging

log = logging.getLogger(__name__)

try:
    from commentjson import loads
except ImportError:
    from json import loads
    log.warning("'commentjson' not found, falling back to built-in 'json'. "
                "Be warned, comments in .json files will cause errors.")

with open("./data/strings.json", "r") as strings_:
    STRINGS = loads(strings_.read())

BOT_ABOUT: str = STRINGS.get("BOT_ABOUT")
if BOT_ABOUT is None:
    raise Exception("String BOT_ABOUT is missing!")

STR_ON_MEMBER_JOIN: str = STRINGS.get("ON_MEMBER_JOIN")
if STR_ON_MEMBER_JOIN is None:
    raise Exception("String ON_MEMBER_JOIN is missing!")

ON_AUTH_BEGIN: str = STRINGS.get("ON_AUTH_BEGIN")
if ON_AUTH_BEGIN is None:
    raise Exception("String ON_AUTH_BEGIN is missing!")

AUTH_HOW: str = STRINGS.get("AUTH_HOW")
if AUTH_HOW is None:
    raise Exception("String AUTH_HOW is missing!")

AUTH_NOT_BOT_TEXT_LIST: list = STRINGS.get("AUTH_NOT_BOT_TEXT_LIST")
if AUTH_NOT_BOT_TEXT_LIST is None:
    raise Exception("List AUTH_NOT_BOT_TEXT_LIST is missing!")

AUTH_RANDOM_EMOJI_LIST: list = STRINGS.get("AUTH_RANDOM_EMOJI_LIST")
if AUTH_RANDOM_EMOJI_LIST is None:
    raise Exception("List AUTH_RANDOM_EMOJI_LIST is missing!")

AUTH_FAILED_TIMEOUT: str = STRINGS.get("AUTH_FAILED_TIMEOUT")
if AUTH_FAILED_TIMEOUT is None:
    raise Exception("String AUTH_FAILED_TIMEOUT is missing!")

AUTH_SUCCESS: str = STRINGS.get("AUTH_SUCCESS")
if AUTH_SUCCESS is None:
    raise Exception("String AUTH_SUCCESS is missing!")
