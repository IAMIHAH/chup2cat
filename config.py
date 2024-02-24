import platform, twitch, random
twclid = ""
twclsc = ""
helix = twitch.Helix(twclid, twclsc)

VERSION = 'v0.0.8a'

SEASON = 'PreSeason-EndofChup2cat'
SEASON_TEXT = 'PRE-SEASON EndofChup2cat'

churList = ["Y" if i>=35 else "N" for i in range(100)]; random.shuffle(churList)

#
# ↑ NEW OPTIONS ARE HERE

SERVER = "TEST" # PRODUCTION or TEST
if f"{platform.system()}" != "Windows": SERVER = "PRODUCTION"

# !!! TOKEN WARNING !!!
# !!! TOKEN WARNING !!!
# !!! TOKEN WARNING !!!
# !!! TOKEN WARNING !!!
# !!! TOKEN WARNING !!!
# !!! TOKEN WARNING !!!
# !!! TOKEN WARNING !!!
# !!! TOKEN WARNING !!!
# !!! TOKEN WARNING !!!






























BOT_TOKEN = {
    "PRODUCTION": "",
    "TEST"      : ""
}