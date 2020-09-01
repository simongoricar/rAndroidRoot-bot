from json import loads

with open("./data/strings.json", "r") as strings_:
    STRINGS = loads(strings_.read())

STR_ON_MEMBER_JOIN: str = STRINGS.get("ON_MEMBER_JOIN")
if STR_ON_MEMBER_JOIN is None:
    raise Exception("String ON_MEMBER_JOIN is missing!")
