import json
from datetime import datetime
import pandas as pd

START_DATE = "2025-03-18"
END_DATE = datetime.now().strftime("%Y-%m-%d")
GAMES_NUM = 162
team_names = set()



with open('games.json', 'r') as file:
    games = json.load(file)
    
for game in games.values():
    if 'team_1' in game:
        team_names.add(game['team_1']['team_name'])
    if 'team_2' in game:
        team_names.add(game['team_2']['team_name'])

sorted_teams = sorted(list(team_names))



def byGame():

    game_len = {team: 0 for team in sorted_teams}

    df = pd.DataFrame(index=sorted_teams, columns=range(1,GAMES_NUM+1))


    for game in games.values():
        t1_name = game['team_1']['team_name']
        t1_elo = game['team_1']['elo_after']
        
        if t1_name in game_len:
            game_len[t1_name] += 1
            col_idx = game_len[t1_name]
            
            if col_idx <= GAMES_NUM: 
                df.at[t1_name, col_idx] = t1_elo

        t2_name = game['team_2']['team_name']
        t2_elo = game['team_2']['elo_after']

        if t2_name in game_len:
            game_len[t2_name] += 1
            col_idx = game_len[t2_name]

            if col_idx <= 82:
                df.at[t2_name, col_idx] = t2_elo                


        df.to_csv('eloGame.csv')



    return


def byDate():


    date_range = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
    formatted_dates = date_range.strftime("%Y-%m-%d")
    df = pd.DataFrame(index=sorted_teams, columns=date_range)

    teamsGames = {}

    for game in games.values():
        date = game['date']
        if date in df.columns:

            t1_name = game['team_1']['team_name']
            t1_elo = game['team_1']['elo_after']
            df.at[t1_name, date] = t1_elo

            t2_name = game['team_2']['team_name']
            t2_elo = game['team_2']['elo_after']
            df.at[t2_name, date] = t2_elo

            df = df.ffill(axis=1)

        df.to_csv('eloDate.csv')



    return

byDate()
byGame()