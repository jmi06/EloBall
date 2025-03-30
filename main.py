import requests
import json
import os
import subprocess
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import font_manager
import numpy
import time
from datetime import datetime
import createBSPost

current_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(current_dir)



now = datetime.now()
hour = now.hour  # Get the current hour in 24-hour format


api_url = 'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard'

with open('games.json') as file:
    games = json.load(file)

with open('teams.json') as file:
    teams = json.load(file)

keepGoing = True


def fetch_games():



    api_request = requests.get(api_url)
    api_request = api_request.json()
    print('called api')

    game_list = api_request['events']

    keepGoing = False
    for i in game_list:
        if i['status']['type']['name'] != 'STATUS_FINAL':
            keepGoing = True





    for game in game_list:
        # game_identifier = f"{game['id']} {game['date']} {game['competitions'][0]['attendance']} {game['competitions'][0]['competitors'][0]['records'][0]['summary']}"
        game_identifier = game['uid']

        teams[game['competitions'][0]['competitors'][0]['team']['displayName']]['record'] = game['competitions'][0]['competitors'][0]['records'][0]['summary']
        teams[game['competitions'][0]['competitors'][1]['team']['displayName']]['record'] = game['competitions'][0]['competitors'][1]['records'][0]['summary']
            

        if game['season']['slug'] == 'regular-season' and game_identifier not in games and game['status']['type']['name'] == 'STATUS_FINAL':
            
            games[game_identifier] = {'socialpost': False, 'points_diff': abs(   float(game['competitions'][0]['competitors'][0]['score']) - float(game['competitions'][0]['competitors'][1]['score'])   ), 'date': game['date'].split("T")[0] } 

            games[game_identifier]['team_1'] = {'team_name': game['competitions'][0]['competitors'][0]['team']['displayName'],
                                           'winner': game['competitions'][0]['competitors'][0]['winner'],
                                           'score': game['competitions'][0]['competitors'][0]['score'],
                                           'logo': game['competitions'][0]['competitors'][0]['team']['logo'],
                                           

                                           'record': game['competitions'][0]['competitors'][0]['records'][0]['summary']}
            games[game_identifier]['team_2'] = {'team_name': game['competitions'][0]['competitors'][1]['team']['displayName'],
                                           'winner': game['competitions'][0]['competitors'][1]['winner'],
                                           'score': game['competitions'][0]['competitors'][1]['score'],
                                           'logo': game['competitions'][0]['competitors'][1]['team']['logo'],


                                           

                                           'record': game['competitions'][0]['competitors'][1]['records'][0]['summary']}



    with open('games.json', 'w') as file:
        json.dump(games, file)


def calc_elo():

    for game in games:
        games[game]['team_1']['elo_before'] = teams[games[game]['team_1']['team_name']]['elo']
        games[game]['team_2']['elo_before'] = teams[games[game]['team_2']['team_name']]['elo']

        #calc the real elo time!!!!!
        #After you calc it make sure it goes into the teams dict as well!

        team_1_elo_before = float(games[game]['team_1']['elo_before'])
        team_2_elo_before = float(games[game]['team_2']['elo_before'])

        team_1_winprob = 1/(1+10 ** ((team_2_elo_before - team_1_elo_before )/400) )

        team_2_winprob = 1/(1+10 ** ((team_1_elo_before - team_2_elo_before )/400) )

        K = 16 * (1 + 0.1 * games[game]['points_diff'])

        if games[game]['team_1']['winner'] == True:
            team1W = 1
        elif games[game]['team_1']['winner'] == False:
            team1W = 0

        if games[game]['team_2']['winner'] == True:
            team2W = 1
        elif games[game]['team_2']['winner'] == False:
            team2W = 0

        print(team_1_elo_before)
        team_1_newrating = team_1_elo_before + K * (team1W-team_1_winprob)
        team_2_newrating = team_2_elo_before + K * (team2W-team_2_winprob)

        games[game]['team_1']['elo_after'] = round(team_1_newrating, 2)
        games[game]['team_2']['elo_after'] = round(team_2_newrating, 2)

        games[game]['team_1']['delta_elo'] = round( float(games[game]['team_1']['elo_after']) - float(games[game]['team_1']['elo_before'] )   ,2)
        games[game]['team_2']['delta_elo'] =round( float(games[game]['team_2']['elo_after']) - float(games[game]['team_2']['elo_before']    ),2)

        if str(games[game]['team_1']['delta_elo']).startswith('+')  == False and games[game]['team_1']['delta_elo'] > 0:
            games[game]['team_1']['delta_elo'] = f"+{games[game]['team_1']['delta_elo']}"
        if str(games[game]['team_2']['delta_elo']).startswith('+')  == False and games[game]['team_2']['delta_elo'] > 0:
            games[game]['team_2']['delta_elo'] = f"+{games[game]['team_2']['delta_elo']}"
                

        teams[games[game]['team_1']['team_name']]['elo'] = round(team_1_newrating, 2)
        teams[games[game]['team_2']['team_name']]['elo'] = round(team_2_newrating, 2)
        teams[games[game]['team_1']['team_name']]['games'].append(game)
        teams[games[game]['team_2']['team_name']]['games'].append(game)



        with open('games.json', 'w') as file:
            json.dump(games, file)

        with open('teams.json', 'w') as file:
            json.dump(teams, file)
            
        
        determineRanks()
    calc_order()
    
    for game in games:
        if 'socialpost' in games[game]:
            if games[game]['socialpost'] == False:
                socialPost(game)
                print('social')



    with open('games.json', 'w') as file:
        json.dump(games, file)

    with open('teams.json', 'w') as file:
        json.dump(teams, file)
        







def setup_teams():
    teams_url = 'http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams'

    teams_data = requests.get(teams_url)
    teams_data =  teams_data.json()


    mlb_teams = {
        "Arizona Diamondbacks": {"league": "NL", "division": "NL West"},
        "Atlanta Braves": {"league": "NL", "division": "NL East"},
        "Baltimore Orioles": {"league": "AL", "division": "AL East"},
        "Boston Red Sox": {"league": "AL", "division": "AL East"},
        "Chicago White Sox": {"league": "AL", "division": "AL Central"},
        "Chicago Cubs": {"league": "NL", "division": "NL Central"},
        "Cincinnati Reds": {"league": "NL", "division": "NL Central"},
        "Cleveland Guardians": {"league": "AL", "division": "AL Central"},
        "Colorado Rockies": {"league": "NL", "division": "NL West"},
        "Detroit Tigers": {"league": "AL", "division": "AL Central"},
        "Houston Astros": {"league": "AL", "division": "AL West"},
        "Kansas City Royals": {"league": "AL", "division": "AL Central"},
        "Los Angeles Angels": {"league": "AL", "division": "AL West"},
        "Los Angeles Dodgers": {"league": "NL", "division": "NL West"},
        "Miami Marlins": {"league": "NL", "division": "NL East"},
        "Milwaukee Brewers": {"league": "NL", "division": "NL Central"},
        "Minnesota Twins": {"league": "AL", "division": "AL Central"},
        "New York Yankees": {"league": "AL", "division": "AL East"},
        "New York Mets": {"league": "NL", "division": "NL East"},
        "Athletics": {"league": "AL", "division": "AL West"},
        "Philadelphia Phillies": {"league": "NL", "division": "NL East"},
        "Pittsburgh Pirates": {"league": "NL", "division": "NL Central"},
        "San Diego Padres": {"league": "NL", "division": "NL West"},
        "San Francisco Giants": {"league": "NL", "division": "NL West"},
        "Seattle Mariners": {"league": "AL", "division": "AL West"},
        "St. Louis Cardinals": {"league": "NL", "division": "NL Central"},
        "Tampa Bay Rays": {"league": "AL", "division": "AL East"},
        "Texas Rangers": {"league": "AL", "division": "AL West"},
        "Toronto Blue Jays": {"league": "AL", "division": "AL East"},
        "Washington Nationals": {"league": "NL", "division": "NL East"},
    }




    for team in teams_data['sports'][0]['leagues'][0]['teams']:
        teams[team['team']['displayName']] = {'elo': 1000, 'games': [], "league": mlb_teams[team['team']['displayName']]['league'], "division": mlb_teams[team['team']['displayName']]['division']}
        

    with open('teams.json', 'w') as file:
        json.dump(teams, file)



def socialPost(id):

    postInfo = {}
    with open('post.json') as postFile:
        postInfo = json.load(postFile)

    if games[id]['team_1']['winner'] == True:

        postInfo['winning_team'] = games[id]['team_1']['team_name']
        postInfo['losing_team'] = games[id]['team_2']['team_name']

    elif games[id]['team_2']['winner'] == True:
    
        postInfo['winning_team'] = games[id]['team_2']['team_name']
        postInfo['losing_team'] = games[id]['team_1']['team_name']


    score1 = games[id]['team_1']['score']
    score2 = games[id]['team_2']['score']

    if score1 >= score2:
        postInfo['score'] = f"{score1}-{score2}"
    else:
        postInfo['score'] = f"{score2}-{score1}"

    with open('post.json', 'w') as postFile:
        json.dump(postInfo, postFile)

    with open('order.json') as orderFile:
        order = json.load(orderFile)

    print('social Posting', id)
    games[id]['socialpost'] = True


    with open('games.json', 'w') as file:
        json.dump(games, file)

    with open('teams.json', 'w') as file:
        json.dump(teams, file)

    red = '#cc4e4e'
    green ='#4ECCA3' 
    text = '#EEEEEE'

    team_1 = games[id]['team_1']
    team_2 = games[id]['team_2']
    
    font_path = 'assets/Roboto-Bold.ttf' 
    font_prop = font_manager.FontProperties(fname=font_path)
    os.system(f"wget -O team_1.png {team_1['logo']}")
    os.system(f"wget -O team_2.png {team_2['logo']}")


    # os.system(f"inkscape assets/{team_1['team_name']}.svg --export-type=png --export-filename=team_1.png --export-dpi=600")
    # os.system(f"inkscape assets/{team_2['team_name']}.svg --export-type=png --export-filename=team_2.png --export-dpi=600")



    team_list = list(order["all"].keys())

    team_1_rank = team_list.index(team_1["team_name"]) + 1  
    team_2_rank = team_list.index(team_2['team_name']) + 1





    team_1_logo = Image.open("team_1.png").convert("RGBA").resize((200, 200), Image.LANCZOS)
    team_2_logo = Image.open("team_2.png").convert("RGBA").resize((200, 200), Image.LANCZOS)

    team_1_logo = numpy.array(team_1_logo)  # Convert to NumPy array for Matplotlib
    team_2_logo = numpy.array(team_2_logo)  # Convert to NumPy array for Matplotlib

    # Create figure
    fig, ax = plt.subplots(figsize=(16, 12))
    fig.patch.set_facecolor('#232931')
    ax.set_xlim(0, 1600)
    ax.set_ylim(0, 1200)
    ax.axis("off")  # Hide axes

    # Centered Text
    ax.text(800, 1000, f"{games[id]['date']}", fontsize=30, color=text, ha='center', va='center',fontproperties=font_prop)


    ax.text(800, 900, f"{team_1['team_name']} vs. {team_2['team_name']}", fontsize=40, color=text, ha='center', va='center',fontproperties=font_prop)
    ax.text(800, 550, f"{team_1['score']} - {team_2['score']}", fontsize=60, color=text, ha='center', va='center',fontproperties=font_prop)

    # Team stats centered below each other
    # Adjusted position for Team 1 ELO and record

    delta_elo_color_team_1 = red if str(team_1['delta_elo']).startswith('-') else green
    ax.text(300, 400, f"[#{team_1_rank}] {team_1['elo_after']} ({team_1['delta_elo']})", fontsize=30, color=delta_elo_color_team_1, ha='center', va='center',fontproperties=font_prop)
    ax.text(300, 300, f"{team_1['record']}", fontsize=30, color=text, ha='center', va='center',fontproperties=font_prop)

    # Adjusted position for Team 2 ELO and record
    delta_elo_color_team_2 = red if str(team_2['delta_elo']).startswith('-') else green

    ax.text(1300, 400, f"[#{team_2_rank}] {team_2['elo_after']} ({team_2['delta_elo']})", fontsize=30, color=delta_elo_color_team_2, ha='center', va='center',fontproperties=font_prop)
    ax.text(1300, 300, f"{team_2['record']}", fontsize=30, color=text, ha='center', va='center',fontproperties=font_prop)
    
    
    ax.text(800, 0, f"@eloball.bsky.social", fontsize=20, color=text, ha='center', va='center',fontproperties=font_prop)


    # Overlay team logos
    ax.imshow(team_1_logo, extent=[200, 400, 500, 700])  # (x_min, x_max, y_min, y_max)
    ax.imshow(team_2_logo, extent=[1200, 1400, 500, 700])

    # Save and show the image
    plt.savefig(f"post.png", dpi=600, bbox_inches="tight")


    with open('games.json', 'w') as file:
        json.dump(games, file)

    createBSPost.create_post()





def calc_order():
    order = {}

    with open('teams.json') as teamFile:
        teams = json.load(teamFile)

    al_teams = {k: v for k, v in teams.items() if v["league"] == "AL"}
    nl_teams = {k: v for k, v in teams.items() if v["league"] == "NL"}

    alEast = {k: v for k, v in teams.items() if v["division"] == "AL East"}
    alWest = {k: v for k, v in teams.items() if v["division"] == "AL West"}
    alCentral = {k: v for k, v in teams.items() if v["division"] == "AL Central"}

    nlEast = {k: v for k, v in teams.items() if v["division"] == "NL East"}
    nlWest = {k: v for k, v in teams.items() if v["division"] == "NL West"}
    nlCentral = {k: v for k, v in teams.items() if v["division"] == "NL Centrnl"}

    
    order['all'] = dict(sorted(teams.items(), key=lambda x: x[1]['elo'], reverse=True))

    order['AL'] = dict(sorted(al_teams.items(), key=lambda x: x[1]['elo'], reverse=True))
    order['NL'] = dict(sorted(nl_teams.items(), key=lambda x: x[1]['elo'], reverse=True))
    order['NL East'] = dict(sorted(nlEast.items(), key=lambda x: x[1]['elo'], reverse=True))
    order['NL West'] = dict(sorted(nlWest.items(), key=lambda x: x[1]['elo'], reverse=True))
    order['NL Central'] = dict(sorted(nlCentral.items(), key=lambda x: x[1]['elo'], reverse=True))

    order['ALEast'] = dict(sorted(alEast.items(), key=lambda x: x[1]['elo'], reverse=True))
    order['ALWest'] = dict(sorted(alWest.items(), key=lambda x: x[1]['elo'], reverse=True))
    order['ALCentral'] = dict(sorted(alCentral.items(), key=lambda x: x[1]['elo'], reverse=True))
    
    



    with open('order.json', 'w') as orderFile:
        json.dump(order, orderFile)


    add_to_db_rankings(order)













def add_to_db_teams():


    #ADD TEAMS TO THE ELO DB
    TEAMS_API_TOKEN = os.getenv('TEAMS_API_TOKEN')

    TEAMS_ACCOUNT_ID = os.getenv('TEAMS_ACCOUNT_ID')
    TEAMS_NAMESPACE_ID = os.getenv('TEAMS_NAMESPACE_ID')
    TEAMS_KV_KEY = os.getenv('TEAMS_KV_KEY')


    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{TEAMS_ACCOUNT_ID}/storage/kv/namespaces/{TEAMS_NAMESPACE_ID}/values/{TEAMS_KV_KEY}"

    HEADERS = {
        "Authorization": f"Bearer {TEAMS_API_TOKEN}",
        "Content-Type": "application/json"
    }


    response = requests.get(BASE_URL, headers=HEADERS)
    response = requests.put(
        BASE_URL,
        headers=HEADERS,
        data=json.dumps(teams)
    )
    print('Teams Added')



def add_to_db_games():


    #ADD TEAMS TO THE ELO DB
    GAMES_API_TOKEN = os.getenv('GAMES_API_TOKEN')

    GAMES_ACCOUNT_ID = os.getenv('GAMES_ACCOUNT_ID')
    GAMES_NAMESPACE_ID = os.getenv('GAMES_NAMESPACE_ID')
    GAMES_KV_KEY = os.getenv('GAMES_KV_KEY')




    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{GAMES_ACCOUNT_ID}/storage/kv/namespaces/{GAMES_NAMESPACE_ID}/values/{GAMES_KV_KEY}"

    HEADERS = {
        "Authorization": f"Bearer {GAMES_API_TOKEN}",
        "Content-Type": "application/json"
    }


    response = requests.get(BASE_URL, headers=HEADERS)
    response = requests.put(
        BASE_URL,
        headers=HEADERS,
        data=json.dumps(games)
    )
    print('Games Added')




def determineRanks():
    # Not an immediate feature, add it if you have time.
    # Should also create a social media post for it aswell, whenever a team is promoted or demoted
    # 
    # BROWN - TEEBALL - 30-26
    # SILVER - AAA - 25-20
    # GOLD - Gold - 19-15
    # Platinum - Platinum - 14-10
    # Diamond - 9-6
    # Black - Mastery - Top 5
    print()


def check_time():
        if 4<= hour < 13:
                keepGoing = False
                print('end operation')
        else: 
                keepGoing = True
        print('Current Hour', hour)


def add_to_db_rankings(order):
        #ADD TEAMS TO THE ELO DB
    RANKINGS_API_TOKEN = os.getenv('RANKINGS_API_TOKEN')

    RANKINGS_ACCOUNT_ID = os.getenv('RANKINGS_ACCOUNT_ID')
    RANKINGS_NAMESPACE_ID = os.getenv('RANKINGS_NAMESPACE_ID')
    RANKINGS_KV_KEY = os.getenv('RANKINGS_KV_KEY')




    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{RANKINGS_ACCOUNT_ID}/storage/kv/namespaces/{RANKINGS_NAMESPACE_ID}/values/{RANKINGS_KV_KEY}"

    HEADERS = {
        "Authorization": f"Bearer {RANKINGS_API_TOKEN}",
        "Content-Type": "application/json"
    }


    response = requests.get(BASE_URL, headers=HEADERS)
    response = requests.put(
        BASE_URL,
        headers=HEADERS,
        data=json.dumps(order)
    )
    print('Games Added')



def keepContinuing():



    setup_teams()
    fetch_games()
    calc_elo()
    add_to_db_teams()
    add_to_db_games()
    check_time()


    if hour >= 4 and  hour <= 13:
        keepGoing = False    
    

    for i in range(36):
        print('still alive',i)
        time.sleep(30)



while datetime.now().hour > 13 or datetime.now().hour < 4:
        keepContinuing()



if 4 <= datetime.now().hour < 13:
        print('great work soldier, try again tmrw')
