from member_updater import Member_Updater
import os

API_KEY = os.environ.get("COC_API_KEY")
CLAN_TAG = os.environ.get("COC_CLAN_TAG") or "#8889L922"
BASE_URL = "https://api.clashofclans.com/v1"


if __name__ == "__main__":
    updater = Member_Updater(API_KEY, CLAN_TAG)
    updater.update()
