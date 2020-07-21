from member_updater import Member_Updater
from config import COC_Config
import os

API_KEY = os.environ.get("COC_API_KEY")
CLAN_TAG = os.environ.get("COC_CLAN_TAG") or "#8889L922"
BASE_URL = "https://api.clashofclans.com/v1"


if __name__ == "__main__":
    config = COC_Config()
    updater = Member_Updater(config)
    updater.update()
