import requests
import json
import time


with open('games.json') as file:
    games = json.load(file)

with open('teams.json') as file:
    teams = json.load(file)



from datetime import date, timedelta

start_date = date(2025, 3, 18)
end_date = date.today()

delta = timedelta(days=1)
current_date = start_date
dates = []
while current_date <= end_date:
    dates.append(current_date.strftime('%Y%m%d'))
    current_date += delta




#https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates=20250318
def fetch_games(date):

    api_url = f'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={date}'


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
            
            games[game_identifier] = {'socialpost': True, 'points_diff': abs(   float(game['competitions'][0]['competitors'][0]['score']) - float(game['competitions'][0]['competitors'][1]['score'])   ), 'date': game['date'].split("T")[0] } 

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



for i in dates:
    print(i)
    if i != '20250715':
        fetch_games(i)
    time.sleep(1)



