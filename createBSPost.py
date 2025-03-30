import requests
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv


load_dotenv()

BLUESKY_HANDLE = os.getenv('BLUESKY_USERNAME')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')

def create_post():
        
    mlb_team_hashtags = {
        "Arizona Diamondbacks": ["#Dbacks", "#RattleOn"],
        "Atlanta Braves": ["#BravesCountry"],
        "Baltimore Orioles": ["#Birdland"],
        "Boston Red Sox": ["#DirtyWater"],
        "Chicago Cubs": ["#GoCubsGo"],
        "Chicago White Sox": ["#ChangeTheGame"],
        "Cincinnati Reds": ["#ATOBTTR"],
        "Cleveland Guardians": ["#ForTheLand"],
        "Colorado Rockies": ["#Rockies"],
        "Detroit Tigers": ["#DetroitRoots"],
        "Houston Astros": ["#Ready2Reign"],
        "Kansas City Royals": ["#TogetherRoyal"],
        "Los Angeles Angels": ["#GoHalos"],
        "Los Angeles Dodgers": ["#HereToPlay"],
        "Miami Marlins": ["#MakeItMiami"],
        "Milwaukee Brewers": ["#ThisIsMyCrew"],
        "Minnesota Twins": ["#MNTwins"],
        "New York Mets": ["#LGM"],
        "New York Yankees": ["#RepBX"],
        "Athletics": ["#Athletics"],
        "Philadelphia Phillies": ["#RingTheBell"],
        "Pittsburgh Pirates": ["#LetsGoBucs"],
        "San Diego Padres": ["#BringTheGold"],
        "San Francisco Giants": ["#SFGameUp"],
        "Seattle Mariners": ["#SeaUsRise"],
        "St. Louis Cardinals": ["#STLCards"],
        "Tampa Bay Rays": ["#RaysUp"],
        "Texas Rangers": ["#StraightUpTX"],
        "Toronto Blue Jays": ["#NextLevel"],
        "Washington Nationals": ["#NATITUDE"]
    }





    # Using a trailing "Z" is preferred over the "+00:00" format
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


    postNow = datetime.now()


    formatted_time = postNow.strftime("%I:%M %p")




    resp = requests.post(

        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_PASSWORD},

    )

    session = resp.json()

    accessJwt = session["accessJwt"]



    with open('post.png', "rb") as f:
        img_bytes = f.read()

    if len(img_bytes) > 1000000:
        raise Exception(
            f"image file size too large. 1000000 bytes maximum, got: {len(img_bytes)}"
        )


    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
        headers={
            "Content-Type": 'image/png',
            "Authorization": "Bearer " + session["accessJwt"],
        },
        data=img_bytes,
    )


    blob = resp.json()["blob"]






    postinfo = {}
    with open('post.json') as postfile:
        postinfo = json.load(postfile)


    post = {
        "$type": "app.bsky.feed.post",
        "text": f"MLB EloBall Update as of {formatted_time}: \n{postinfo['winning_team']} beat {postinfo['losing_team']} {postinfo['score']} \n#mlb",
        "createdAt": now,
    }

    post["embed"] = {
        "$type": "app.bsky.embed.images",
        "images": [{
            "alt": "",
            "image": blob,
            "aspectRatio": {"width": 313, "height": 236}
        }],
    }


    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + session["accessJwt"]},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )
