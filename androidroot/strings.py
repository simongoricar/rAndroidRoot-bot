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

ON_VERIFICATION_BEGIN: str = STRINGS.get("ON_VERIFICATION_BEGIN")
if ON_VERIFICATION_BEGIN is None:
    raise Exception("String ON_VERIFICATION_BEGIN is missing!")

VERIFICATION_HOW: str = STRINGS.get("VERIFICATION_HOW")
if VERIFICATION_HOW is None:
    raise Exception("String VERIFICATION_HOW is missing!")

VERIFY_RANDOM_EMOJI_LIST: list = STRINGS.get("VERIFY_RANDOM_EMOJI_LIST")
if VERIFY_RANDOM_EMOJI_LIST is None:
    raise Exception("List VERIFY_RANDOM_EMOJI_LIST is missing!")

VERIFY_FAILED_TIMEOUT: str = STRINGS.get("VERIFY_FAILED_TIMEOUT")
if VERIFY_FAILED_TIMEOUT is None:
    raise Exception("String VERIFY_FAILED_TIMEOUT is missing!")

VERIFY_SUCCESS: str = STRINGS.get("VERIFY_SUCCESS")
if VERIFY_SUCCESS is None:
    raise Exception("String VERIFY_SUCCESS is missing!")
