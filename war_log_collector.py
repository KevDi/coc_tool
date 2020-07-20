import argparse
import os
import requests
import json

from datetime import date, datetime
from dateutil import tz
from urllib.parse import quote

from requests import api


BASE_URL = "https://api.clashofclans.com/v1/clans"


def parseArguments():
    my_parser = argparse.ArgumentParser(
        description="Collect information about current Clan War"
    )
    my_parser.add_argument(
        "--apikey",
        metavar="apikey",
        type=str,
        help="API Key to use the CoC API",
        required=True,
    )
    # my_parser.add_argument(
    #     "--clantag",
    #     metavar="clantag",
    #     type=str,
    #     help="Clan Id Tag should Start with an #",
    #     required=True,
    # )

    args = my_parser.parse_args()

    api_key = args.apikey
    clantag = "#8889L922"

    print(api_key)
    print(encodeClanTag(clantag))
    return api_key, encodeClanTag(clantag)


def encodeClanTag(clantag):
    return quote(clantag)


def get_current_war(api_key, clan_tag):
    url = "{}/{}/currentwar".format(BASE_URL, clan_tag)
    print(url)
    response = requests.get(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(api_key),
        },
    )
    return response


def war_in_preperation(data):
    return data["state"] == "preparation"


def check_war(api_key, clan_tag):
    response = get_current_war(api_key, clan_tag)
    if response.status_code != 200:
        return
    else:
        data = response.json()
        if war_in_preperation(data):
            store_war_to_file(data, "currentwar.json")


def convertToLocalTime(endTime):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(endTime, "%Y%m%dT%H%M%S.%fZ")
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)


def war_ended():
    with open("data/currentwar.json") as json_file:
        data = json.load(json_file)
        endTime = datetime.strptime(data["endTime"], "%Y%m%dT%H%M%S.%fZ")
        return datetime.utcnow() > endTime


def process_war_result(api_key, clan_tag):
    response = get_current_war(api_key, clan_tag)
    if response.status_code != 200:
        return
    data = response.json()
    if data["state"] != "warEnded":
        return
    endTime = convertToLocalTime(data["endTime"])
    store_war_to_file(data, "{}.json".format(endTime.strftime("%Y%m%d%H%M%S")))
    os.remove("data/currentwar.json")


def store_war_to_file(data, filename):
    with open("data/{}".format(filename), "w") as outfile:
        json.dump(data, outfile)


def main():
    api_key, clan_tag = parseArguments()
    if os.path.exists("data/currentwar.json") and war_ended():
        process_war_result(api_key, clan_tag)
    else:
        check_war(api_key, clan_tag)


if __name__ == "__main__":
    main()
