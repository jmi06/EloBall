import requests
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import tweepy
import time
load_dotenv()

BLUESKY_HANDLE = os.getenv('BLUESKY_USERNAME')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')


TW_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TW_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
TW_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TW_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')



def create_post():
        
    mlb_team_hashtags = {
        "Arizona Diamondbacks": "#Dbacks",
        "Atlanta Braves": "#Braves",
        "Baltimore Orioles": "#orioles",
        "Boston Red Sox": "#RedSox",
        "Chicago Cubs": "#Cubs",
        "Chicago White Sox": "#WhiteSox",
        "Cincinnati Reds": "#Reds",
        "Cleveland Guardians": "#Guardians",
        "Colorado Rockies": "#Rockies",
        "Detroit Tigers": "#tigers",
        "Houston Astros": "#Astros",
        "Kansas City Royals": "#KCRoyals",
        "Los Angeles Angels": "#Angels",
        "Los Angeles Dodgers": "#Dodgers",
        "Miami Marlins": "#Marlins",
        "Milwaukee Brewers": "#Brewers",
        "Minnesota Twins": "#MNTwins",
        "New York Mets": "#Mets",
        "New York Yankees": "#Yankees",
        "Athletics": "#Athletics",
        "Philadelphia Phillies": "#Phillies",
        "Pittsburgh Pirates": "#Pirates",
        "San Diego Padres": "#SDPadres",
        "San Francisco Giants": "#SFGiants",
        "Seattle Mariners": "#Mariners",
        "St. Louis Cardinals": "#STLCards",
        "Tampa Bay Rays": "#Rays",
        "Texas Rangers": "#Rangers",
        "Toronto Blue Jays": "#BlueJays",
        "Washington Nationals": "Nationals"
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

    posttext = f"MLB EloBall Update as of {formatted_time}: \n{postinfo['winning_team']} beat {postinfo['losing_team']} {postinfo['score']} \nSee more at https://eloball.pages.dev/ \n#MLB"
    posttextX = f"MLB EloBall Update as of {formatted_time}: \n{postinfo['winning_team']} beat {postinfo['losing_team']} {postinfo['score']} \nSee more at https://eloball.pages.dev/ \n#MLB\n{mlb_team_hashtags[postinfo['winning_team']]}\n{mlb_team_hashtags[postinfo['losing_team']]}"


    facets = [
        {
            "index": {
                "byteStart": posttext.find("https://eloball.pages.dev/"),
                "byteEnd": posttext.find("https://eloball.pages.dev/") + len("https://eloball.pages.dev/")
            },
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "https://eloball.pages.dev/"}]
        },
        {
            "index": {
                "byteStart": posttext.find("#MLB"),
                "byteEnd": posttext.find("#MLB") + len("#MLB")
            },
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "MLB"}]
        }
    ]










    post = {
        "$type": "app.bsky.feed.post",
        "text": posttext,
        "createdAt": now,
        'facets': facets
    }




    

    post["embed"] = {
        "$type": "app.bsky.embed.images",
        "images": [{
            "alt": "",
            "image": blob,
            "aspectRatio": {"width": 313, "height": 236}
        }],
    }

    attempts = 0
    try:
        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": "Bearer " + session["accessJwt"]},
            json={
                "repo": session["did"],
                "collection": "app.bsky.feed.post",
                "record": post,
            },
        )
    except Exception as e:
        print('bluesky is beefing with us',e)
        attempts+=1
        if attempts < 3:
            create_post()
    twitter_post()


def twitter_post():


    # Using a trailing "Z" is preferred over the "+00:00" format
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


    postNow = datetime.now()


    formatted_time = postNow.strftime("%I:%M %p")

        
    mlb_team_hashtags = {
        "Arizona Diamondbacks": "#Dbacks",
        "Atlanta Braves": "#Braves",
        "Baltimore Orioles": "#orioles",
        "Boston Red Sox": "#RedSox",
        "Chicago Cubs": "#Cubs",
        "Chicago White Sox": "#WhiteSox",
        "Cincinnati Reds": "#Reds",
        "Cleveland Guardians": "#Guardians",
        "Colorado Rockies": "#Rockies",
        "Detroit Tigers": "#tigers",
        "Houston Astros": "#Astros",
        "Kansas City Royals": "#KCRoyals",
        "Los Angeles Angels": "#Angels",
        "Los Angeles Dodgers": "#Dodgers",
        "Miami Marlins": "#Marlins",
        "Milwaukee Brewers": "#Brewers",
        "Minnesota Twins": "#MNTwins",
        "New York Mets": "#Mets",
        "New York Yankees": "#Yankees",
        "Athletics": "#Athletics",
        "Philadelphia Phillies": "#Phillies",
        "Pittsburgh Pirates": "#Pirates",
        "San Diego Padres": "#SDPadres",
        "San Francisco Giants": "#SFGiants",
        "Seattle Mariners": "#Mariners",
        "St. Louis Cardinals": "#STLCards",
        "Tampa Bay Rays": "#Rays",
        "Texas Rangers": "#Rangers",
        "Toronto Blue Jays": "#BlueJays",
        "Washington Nationals": "Nationals"
    }





    with open('post.json') as postfile:
        postinfo = json.load(postfile)

    posttext = f"MLB EloBall Update as of {formatted_time}: \n{postinfo['winning_team']} beat {postinfo['losing_team']} {postinfo['score']} \nSee more at https://eloball.pages.dev/ \n#MLB"
    posttextX = f"MLB EloBall Update as of {formatted_time}: \n{postinfo['winning_team']} beat {postinfo['losing_team']} {postinfo['score']} \nSee more at https://eloball.pages.dev/ \n#MLB\n{mlb_team_hashtags[postinfo['winning_team']]}\n{mlb_team_hashtags[postinfo['losing_team']]}"




    try:
         client = tweepy.Client(
             consumer_key= TW_CONSUMER_KEY,
             consumer_secret= TW_CONSUMER_SECRET,
             access_token = TW_ACCESS_TOKEN,
             access_token_secret= TW_ACCESS_SECRET
         )


         auth = tweepy.OAuth1UserHandler(TW_CONSUMER_KEY, TW_CONSUMER_SECRET, TW_ACCESS_TOKEN, TW_ACCESS_SECRET)
         api_v1 = tweepy.API(auth)
         media = api_v1.media_upload("post.png")


         response = client.create_tweet(
                 text=posttextX,
                 media_ids=[media.media_id]
         )
    except Exception as e:
         print('twitter is beefing with us rn', e)
         time.sleep(30)
         twitter_post()






