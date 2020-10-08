import logging
from typing import Optional

log = logging.getLogger(__name__)

try:
    from commentjson import loads
except ImportError:
    from json import loads
    log.warning("'commentjson' not found, falling back to built-in 'json'. "
                "Be warned, comments in .json files will cause errors.")

with open("./data/strings.json", "r") as strings_:
    STRINGS = loads(strings_.read())

REQUIRED_STRING_LIST = [
    "BOT_ABOUT",
    "ON_MEMBER_JOIN",
    "ON_VERIFICATION_BEGIN",
    "VERIFICATION_HOW",
    "VERIFY_RANDOM_EMOJI_LIST",
    "VERIFY_FAILED_TIMEOUT",
    "VERIFY_SUCCESS",
    "VERIFYALL_CONFIRMATION",
    "VERIFYALL_TIMEOUT",
    "VERIFYALL_STARTING",
    "VERIFYALL_PROGRESS",
    "VERIFYALL_DONE",
    "CMD_NOT_ALLOWED_FOR_USER",
    "MANUAL_VERIFICATION",
    "MANUAL_VERIFICATION_NO_NEED",
]

# Make sure all required strings are present
for s in REQUIRED_STRING_LIST:
    if STRINGS.get(s) is None:
        raise Exception(f"String {s} is required, but missing!")


class String:
    """
    Contains all known string keys.
    """
    BOT_ABOUT = "BOT_ABOUT"
    ON_MEMBER_JOIN = "ON_MEMBER_JOIN"
    ON_VERIFICATION_BEGIN = "ON_VERIFICATION_BEGIN"
    VERIFICATION_HOW = "VERIFICATION_HOW"
    VERIFY_RANDOM_EMOJI_LIST = "VERIFY_RANDOM_EMOJI_LIST"
    VERIFY_FAILED_TIMEOUT = "VERIFY_FAILED_TIMEOUT"
    VERIFY_SUCCESS = "VERIFY_SUCCESS"
    VERIFYALL_CONFIRMATION = "VERIFYALL_CONFIRMATION"
    VERIFYALL_TIMEOUT = "VERIFYALL_TIMEOUT"
    VERIFYALL_STARTING = "VERIFYALL_STARTING"
    VERIFYALL_PROGRESS = "VERIFYALL_PROGRESS"
    VERIFYALL_DONE = "VERIFYALL_DONE"
    CMD_NOT_ALLOWED_FOR_USER = "CMD_NOT_ALLOWED_FOR_USER"
    MANUAL_VERIFICATION = "MANUAL_VERIFICATION"
    MANUAL_VERIFICATION_NO_NEED = "MANUAL_VERIFICATION_NO_NEED"


def gets(string_name: str) -> Optional[str]:
    return STRINGS.get(string_name)
