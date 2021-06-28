#!venv/bin/python3

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from WorldTimeAPI import service as serv
import datetime
from typing import List, Optional
import discord
import argparse

class TimeZone:
    def __init__(self, tz_str: str) -> None:
        tz_tokens: List[str] = tz_str.split("/")
        self.area: str = tz_tokens[0]
        self.location: str = tz_tokens[1]

    def __repr__(self) -> str:
        "TZ"

def find_timezone(query: str) -> Optional[TimeZone]:
    geolocator = Nominatim(user_agent="wth")
    position = geolocator.geocode(query)
    if not position:
        return None

    tzf = TimezoneFinder()
    tz_str = tzf.timezone_at(lng=position.longitude, lat=position.latitude)
    return TimeZone(tz_str)

def get_current_datetime(tz: TimeZone) -> str:
    myclient = serv.Client('timezone')
    requests = {"area": tz.area, "location": tz.location}
    recv_json = myclient.get(**requests)
    dt_str: str = recv_json.datetime
    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    return dt.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", help="discord bot token")
    args = parser.parse_args()
    token: str = args.token
    if not token:
        print("Please provice discord bot token via --token")
        exit()

    client = discord.Client()

    @client.event
    async def on_ready():
        print(f"We have logged in as {client.user}")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith(')'):
            message_str: str = message.content
            location: str = message_str[1:]
            timezone: Optional[TimeZone] = find_timezone(location)
            if not timezone:
                reply: str = f"I can't find {location}"
            else:
                time_str: str = get_current_datetime(timezone)
                reply: str = f"{location} is now {time_str}"
            user: str = message.author.mention
            await message.channel.send(f"{user}, {reply}")

    client.run(token)