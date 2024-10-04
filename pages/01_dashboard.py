import streamlit as st 
import json
import pandas as pd 
from Brawlstats import APIrequests
import base64
import plotly.express as px
import os

st.set_page_config(layout="wide")

df_placeholder = pd.DataFrame()
MAX_PLAYER_COUNT = {
    "duels" : 2, ## duels mode yields THREE brawlers chosen. Will have to fix function to allow for multiple brawlers chosen on 'duels' mode
    "trioShowdown": 12,
    "soloShowdown": 10,
    "duoShowdown": 10,
    "roboRumble": 3,
    "bossFight": 3,
    "superCityRampage": 3,
    "gemGrab": 6,
    "brawlBall": 6,
    "bounty": 6,
    "heist": 6,
    "siege": 6,
    "hotZone": 6,
    "knockout": 6,
}

def get_data(player_tag):
    player = api.get_player(player_tag)
    player = json.loads(player)
    player['battle_logs'] = json.loads(api.get_player_battle_log(player_tag))
    player['createdDatetime'] = datetime.now()
    return player

def recursive_items(data, results, parent_key=''):
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{parent_key}{key}" if parent_key == '' else f"{parent_key}_{key}"  # Create a full key
            yield from recursive_items(value, results, full_key)  # Recursively yield from the value
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            # Create a new key for list items
            list_key = f"{parent_key}_{idx}" if parent_key else str(idx)
            yield from recursive_items(item, results, list_key)  # Recursively yield from each item in the list
    else:
        # Only yield if the value is not a dictionary
        if not isinstance(data, dict):
            yield parent_key, data  # Yield the parent key and value if it's neither a list nor a dict

def determine_win(row):
    return 1 if (row['result'] == 'victory' or row['rank'] <= row['max_player_count'] * 0.3) else 0

def get_played_brawlers(df, player_name):  
    played_brawlers = []
    for index, row in df.iterrows():
        if player_name in row.values:
            found_col = row.index[row.values == player_name ].tolist()
            lookup_column = found_col[0].replace('name','brawler_name')
            played_brawlers.append(row[lookup_column])
    return pd.DataFrame(played_brawlers, columns=['played_brawler'])

def calc_avg_game_duration(df):
    return df['duration'].mean()

def calc_win_ratio(df):
    if len(df) >= 2:
        wins_and_losses_values_count = df['isWin'].value_counts().to_list()
        return wins_and_losses_values_count[0]/(sum(wins_and_losses_values_count))    
    else:
        get_value = df['isWin'].values
        return float(get_value[0])

def calc_star_player_ratio(df, player_name):
    player_is_star_player = df.query(f"starPlayer_name == '{player_name}'")['starPlayer_name'].count()
    num_star_player_awards = df['starPlayer_name'].value_counts().sum()
    return player_is_star_player/num_star_player_awards

def calc_proportions(df):
    proportions = {}
    value_counts = df['played_brawler'].value_counts()
    brawler_names = value_counts.index
    sum_value_counts =sum(value_counts)
    brawler_picks = tuple(zip(brawler_names,value_counts))
    for brawler_name, pick_count in brawler_picks:
        pick_proportion = pick_count/sum_value_counts
        proportions[brawler_name] = [pick_count, pick_proportion]
    return proportions

def brawler_pick_rate(df):
    picks = calc_proportions(df)
    return picks

def calc_rate_change(df):
    time_taken = df['duration'].sum() / 60 # minutes
    total_ressources = df['trophyChange'].sum()
    num_games = len(df['trophyChange'])
    #print(f"{time_taken = :.0f} minutes, {total_ressources = }, {num_games = }")
    return (time_taken, num_games, total_ressources/num_games, total_ressources/time_taken)  

def get_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
    return encoded_string
images_dict = {
    "Brawlify Logo": "https://cdn-old.brawlify.com/front/Star.svg",
    "BrawlTV": "https://cdn-old.brawlify.com/icon/BrawlTV.png",
    "Red Ribbon": "https://cdn-fankit.brawlify.com/icon_calendar_ribbon.png",
    "Brawl Pass": "https://cdn-fankit.brawlify.com/icon_brawl_pass_plus.png",
    "Many Gems": "https://cdn-fankit.brawlify.com/gems_pack_0950.png",
    "Brawl Stars Player Tag": "https://cdn-old.brawlify.com/misc/save-tag.jpg",
    "Switch": "https://cdn-old.brawlify.com/icon/Swap.png",
    "Final Four": "https://cdn-old.brawlify.com/icon/Info-Round.png",
    "Solo Showdown": "https://cdn.brawlify.com/game-modes/regular/48000006.png",
    "Duo Showdown": "https://cdn.brawlify.com/game-modes/regular/48000009.png",
    "Pinball Dreams": "https://cdn-old.brawlify.com/icon/Info-Round.png",
    "Brawl Ball": "https://cdn.brawlify.com/game-modes/regular/48000005.png",
    "Hard Rock Mine": "https://cdn-old.brawlify.com/icon/Info-Round.png",
    "Gem Grab": "https://cdn.brawlify.com/game-modes/regular/48000000.png",
    "Open Business": "https://cdn-old.brawlify.com/icon/Info-Round.png",
    "Hot Zone": "https://cdn.brawlify.com/game-modes/regular/48000017.png",
    "Four Levels": "https://cdn-old.brawlify.com/icon/Info-Round.png",
    "Knockout": "https://cdn.brawlify.com/game-modes/regular/48000020.png",
    "Meadow Of The Crane": "https://cdn-old.brawlify.com/icon/Info-Round.png",
    "Duels": "https://cdn.brawlify.com/game-modes/regular/48000024.png",
    "Rosa": "https://cdn.brawlify.com/brawlers/borderless/16000024.png",
    "Frank": "https://cdn.brawlify.com/brawlers/borderless/16000020.png",
    "Meg": "https://cdn.brawlify.com/brawlers/borderless/16000052.png",
    "Nita": "https://cdn.brawlify.com/brawlers/borderless/16000008.png",
    "Darryl": "https://cdn.brawlify.com/brawlers/borderless/16000018.png",
    "El primo": "https://cdn.brawlify.com/brawlers/borderless/16000010.png",
    "Jacky": "https://cdn.brawlify.com/brawlers/borderless/16000034.png",
    "Gale": "https://cdn.brawlify.com/brawlers/borderless/16000035.png",
    "Bibi": "https://cdn.brawlify.com/brawlers/borderless/16000026.png",
    "Lily": "https://cdn.brawlify.com/brawlers/borderless/16000081.png",
    "Emz": "https://cdn.brawlify.com/brawlers/borderless/16000030.png",
    "8-bit": "https://cdn.brawlify.com/brawlers/borderless/16000027.png",
    "Doug": "https://cdn.brawlify.com/brawlers/borderless/16000071.png",
    "Edgar": "https://cdn.brawlify.com/brawlers/borderless/16000043.png",
    "Bull": "https://cdn.brawlify.com/brawlers/borderless/16000002.png",
    "Ash": "https://cdn.brawlify.com/brawlers/borderless/16000051.png",
    "Buster": "https://cdn.brawlify.com/brawlers/borderless/16000062.png",
    "Chester": "https://cdn.brawlify.com/brawlers/borderless/16000063.png",
    "Leon": "https://cdn.brawlify.com/brawlers/borderless/16000023.png",
    "Jessie": "https://cdn.brawlify.com/brawlers/borderless/16000007.png",
    "Shelly": "https://cdn.brawlify.com/brawlers/borderless/16000000.png",
    "Tick": "https://cdn.brawlify.com/brawlers/borderless/16000022.png",
    "Spike": "https://cdn.brawlify.com/brawlers/borderless/16000005.png",
    "Poco": "https://cdn.brawlify.com/brawlers/borderless/16000013.png",
    "Fang": "https://cdn.brawlify.com/brawlers/borderless/16000054.png",
    "Sandy": "https://cdn.brawlify.com/brawlers/borderless/16000028.png",
    "Rico": "https://cdn.brawlify.com/brawlers/borderless/16000004.png",
    "Bonnie": "https://cdn.brawlify.com/brawlers/borderless/16000058.png",
    "Crow": "https://cdn.brawlify.com/brawlers/borderless/16000012.png",
    "Kenji": "https://cdn.brawlify.com/brawlers/borderless/16000085.png",
    "Carl": "https://cdn.brawlify.com/brawlers/borderless/16000025.png",
    "Colt": "https://cdn.brawlify.com/brawlers/borderless/16000001.png",
    "Tara": "https://cdn.brawlify.com/brawlers/borderless/16000017.png",
    "Griff": "https://cdn.brawlify.com/brawlers/borderless/16000050.png",
    "Moe": "https://cdn.brawlify.com/brawlers/borderless/16000084.png",
    "Surge": "https://cdn.brawlify.com/brawlers/borderless/16000038.png",
    "Buzz": "https://cdn.brawlify.com/brawlers/borderless/16000049.png",
    "Brock": "https://cdn.brawlify.com/brawlers/borderless/16000003.png",
    "Bo": "https://cdn.brawlify.com/brawlers/borderless/16000014.png",
    "Pearl": "https://cdn.brawlify.com/brawlers/borderless/16000072.png",
    "Pam": "https://cdn.brawlify.com/brawlers/borderless/16000016.png",
    "Mortis": "https://cdn.brawlify.com/brawlers/borderless/16000011.png",
    "Dynamike": "https://cdn.brawlify.com/brawlers/borderless/16000009.png",
    "Draco": "https://cdn.brawlify.com/brawlers/borderless/16000080.png",
    "Mico": "https://cdn.brawlify.com/brawlers/borderless/16000075.png",
    "Grom": "https://cdn.brawlify.com/brawlers/borderless/16000048.png",
    "Piper": "https://cdn.brawlify.com/brawlers/borderless/16000015.png",
    "Colette": "https://cdn.brawlify.com/brawlers/borderless/16000039.png",
    "Cordelius": "https://cdn.brawlify.com/brawlers/borderless/16000070.png",
    "Larry & lawrie": "https://cdn.brawlify.com/brawlers/borderless/16000077.png",
    "Chuck": "https://cdn.brawlify.com/brawlers/borderless/16000073.png",
    "Hank": "https://cdn.brawlify.com/brawlers/borderless/16000069.png",
    "Stu": "https://cdn.brawlify.com/brawlers/borderless/16000045.png",
    "Max": "https://cdn.brawlify.com/brawlers/borderless/16000032.png",
    "Gene": "https://cdn.brawlify.com/brawlers/borderless/16000021.png",
    "Clancy": "https://cdn.brawlify.com/brawlers/borderless/16000083.png",
    "Mandy": "https://cdn.brawlify.com/brawlers/borderless/16000065.png",
    "Squeak": "https://cdn.brawlify.com/brawlers/borderless/16000047.png",
    "Melodie": "https://cdn.brawlify.com/brawlers/borderless/16000078.png",
    "Angelo": "https://cdn.brawlify.com/brawlers/borderless/16000079.png",
    "Bea": "https://cdn.brawlify.com/brawlers/borderless/16000029.png",
    "Lola": "https://cdn.brawlify.com/brawlers/borderless/16000053.png",
    "Sam": "https://cdn.brawlify.com/brawlers/borderless/16000060.png",
    "Byron": "https://cdn.brawlify.com/brawlers/borderless/16000042.png",
    "Barley": "https://cdn.brawlify.com/brawlers/borderless/16000006.png",
    "Gus": "https://cdn.brawlify.com/brawlers/borderless/16000061.png",
    "Maisie": "https://cdn.brawlify.com/brawlers/borderless/16000068.png",
    "Penny": "https://cdn.brawlify.com/brawlers/borderless/16000019.png",
    "Mr. p": "https://cdn.brawlify.com/brawlers/borderless/16000031.png",
    "R-t": "https://cdn.brawlify.com/brawlers/borderless/16000066.png",
    "Nani": "https://cdn.brawlify.com/brawlers/borderless/16000036.png",
    "Amber": "https://cdn.brawlify.com/brawlers/borderless/16000040.png",
    "Belle": "https://cdn.brawlify.com/brawlers/borderless/16000046.png",
    "Lou": "https://cdn.brawlify.com/brawlers/borderless/16000041.png",
    "Sprout": "https://cdn.brawlify.com/brawlers/borderless/16000037.png",
    "Kit": "https://cdn.brawlify.com/brawlers/borderless/16000076.png",
    "Gray": "https://cdn.brawlify.com/brawlers/borderless/16000064.png",
    "Eve": "https://cdn.brawlify.com/brawlers/borderless/16000056.png",
    "Willow": "https://cdn.brawlify.com/brawlers/borderless/16000067.png",
    "Berry": "https://cdn.brawlify.com/brawlers/borderless/16000082.png",
    "Janet": "https://cdn.brawlify.com/brawlers/borderless/16000057.png",
    "Otis": "https://cdn.brawlify.com/brawlers/borderless/16000059.png",
    "Charlie": "https://cdn.brawlify.com/brawlers/borderless/16000074.png",
    "Ruffs": "https://cdn.brawlify.com/brawlers/borderless/16000044.png",
    "Search": "https://cdn-old.brawlify.com/icon/Search.png"}

#st.write(images_dict)
@ st.cache_data
def get_img(file):
    with open (file, 'rb') as f:
        data=f.read()
    return base64.b64encode(data).decode()

FILE_ROOT = os.curdir
img = get_img(f"{FILE_ROOT}/assets/wallpaper.jpg")
API_KEY = st.secrets['api']['api_key'] 
api =  APIrequests(api_key=API_KEY)
css = f"""
<style>
img{{vertical-align:bottom;}}
{{text-align: center;}}

</style>
"""

# Apply custom CSS
st.markdown(css, unsafe_allow_html=True)

if st.session_state == {}:
    user_tag='28QLRGQL0U'
else:
    user_tag = st.session_state.user_tag

player_data = api.get_player(user_tag)
battlelog_data = api.get_player_battle_log(user_tag)
#with open('data.json', 'r') as f:
 #   player_data = f.read()
  #  st.write(player_data)
player_data = json.loads(player_data)
#st.write(player_data)
player_name = player_data['name']

battlelog_data = json.loads(battlelog_data)
#st.write(st.session_state)
#battlelog_data = player_data['battle_logs']

battles = battlelog_data['items']
df_battles = pd.DataFrame(battles)
data = df_battles['event'] 
df_events = pd.DataFrame(data, columns=['event'])
flattened_df = pd.json_normalize(df_events['event'], sep='_')
#flattened_df
df_battle_brawler = df_battles['battle']
df_battle_brawler_flat = pd.json_normalize(df_battles['battle'], sep='_')
df_brawls = pd.concat([df_battles['battleTime'], flattened_df, df_battle_brawler_flat.drop(columns=['mode', 'teams'])],axis=1)
#df_brawls
all_df = pd.DataFrame(columns=df_brawls.columns)
all_battles = {}
for idx, battle in enumerate(df_battle_brawler.items()):
    results = {}
    for key, value in recursive_items(battle[1], results):
        results[key] = [value]
    battle_time = df_battles['battleTime'][idx]
    results['battleTime']=[battle_time]
    all_battles[battle_time] = results
    new_df = pd.DataFrame(all_battles[battle_time],index=[idx])
    uncommon_columns = list(set(df_brawls.columns).difference(set(new_df.columns)))
    sf_sll = pd.concat([new_df, df_brawls[uncommon_columns].iloc[[idx]]], axis=1)
    all_df=pd.concat([all_df, sf_sll], axis=0)
    
all_df = all_df.drop(columns='id')
all_df['duration'] = all_df['duration'].fillna(90)
all_df['trophyChange'] = all_df['trophyChange'].fillna(0)
columns = all_df.columns
if 'played_brawler' not in columns:
    played_brawlers = get_played_brawlers(all_df, player_name)
    all_df = pd.concat([all_df, played_brawlers], axis=1)
    
all_df = all_df.assign(max_player_count = all_df['mode'].map(MAX_PLAYER_COUNT))
all_df = all_df.assign(isWin = all_df.apply(determine_win, axis=1))
df_battles = all_df
#df_battles
#st.write(df_battles.shape)

df_battle_modes = df_battles[['mode', 'isWin']]
df_battle_modes_agg = df_battle_modes.value_counts().reset_index()
#df_battle_modes_agg

df_battle_modes_count = df_battle_modes_agg.groupby(by='mode')['count'].sum().reset_index()
#df_battle_modes_count
df_battle_modes_res = df_battle_modes_agg.groupby(by='isWin')['count'].sum().reset_index()
#df_battle_modes_res

df_battles_trophy_brawler = df_battles[['battleTime', 'trophyChange','played_brawler']].value_counts().reset_index()
#df_battles_trophy_brawler

col = st.columns([3,1,3])
with col[1]:
    st.image(f'{FILE_ROOT}/assets/logo.png')

with st.container():
    cols_2 =st.columns([3,1])
    with cols_2[0]:
        st.title(f"{user_tag} - {player_name}")


    cols_10 = st.columns([1,3])
    with cols_10[0]:
        with st.container(border=True, height=380):
            cols_101 = st.columns([1,6])
            with cols_101[0]:
                with st.container(border=False, height=50):
                    st.image(f'{FILE_ROOT}/assets/XP.png')
                with st.container(border=False, height=50):
                    st.image('https://cdn-old.brawlify.com/icon/Club.png', output_format='PNG')
                with st.container(border=False, height=50):
                    st.image('https://cdn-old.brawlify.com/icon/trophy.png')
            with cols_101[1]:
                with st.container(border=False, height=50):
                    st.write(f"{player_data['expPoints']} - Level: {player_data['expLevel']}")
                with st.container(border=False, height=50):
                    st.markdown(f"{player_data['club']['name'] if 'Club' in player_data.keys() else 'No club'}", unsafe_allow_html=True)
                with st.container(border=False, height=50):
                    st.write(f"{player_data['trophies']}")

    with cols_10[1]:
        with st.container(border=True, height=380):
            st.header('Cool stats')
            st.bar_chart(df_battle_modes_count, x='mode', y='count')

cols_102 = st.columns([1,2])
with cols_102[0]:
    with st.container(border=True, height=380):
        st.header('Cool stats2')
        st.bar_chart(df_battle_modes_res, x='isWin', y='count')

with cols_102[1]:
    with st.container(border=True, height=380):
        cols_3 =st.columns(3)
        with cols_3[0]:
            st.image('https://cdn-old.brawlify.com/icon/3v3.png')
            st.metric('3vs3Victories', player_data['3vs3Victories'])
        with cols_3[1]:
            st.image('https://cdn-old.brawlify.com/gamemode/Showdown.png')
            st.metric('soloVictories', player_data['soloVictories'])
        with cols_3[2]:
            st.image('https://cdn-old.brawlify.com/gamemode/Duo-Showdown.png')
            st.metric('duoVictories', player_data['duoVictories'])

st.header('Brawler Statistics')
with st.container():
    cols = st.columns(4)
    pick_rate = brawler_pick_rate(df_battles)
    for index, brawler in enumerate(player_data['brawlers']):
        col = cols[index % 4] 
        brawler_name = str(brawler["name"])
        brawler_name = brawler_name.casefold().capitalize()
        img = images_dict[brawler_name]
        with col:
            with st.container(border=True):
                one_wide = st.columns([1,5])
                wide_cols = st.columns([2,3]) 
                with one_wide[0]:
                    rank = brawler["rank"]
                    st.image(f'https://cdn.brawlify.com/ranks/regular/{rank}.png')
                with one_wide[1]:
                    st.header(f'{brawler["name"]}', )
                with wide_cols[0]:
                    st.image(f'{img}')
                played_brawler_list = set(df_battles_trophy_brawler['played_brawler'])
                #st.write(brawler_name.upper(), played_brawler_list)
                with wide_cols[1]:
                    brawler_wr = 0
                    brawler_pr = 0
                    brawler_trophy_rate = (0, 0, 0, 0)
                    if brawler_name.upper() in played_brawler_list:
                        brawler_trophy_rate = calc_rate_change(df_battles[df_battles['played_brawler'] == brawler_name.upper()])
                        brawler_pr = pick_rate[f"{brawler_name.upper()}"][1]
                        brawler_wr = calc_win_ratio(df_battles[df_battles['played_brawler'] == brawler_name.upper()])
                        # Filter DataFrame for the specific brawler
                        df_battles_trophy = df_battles_trophy_brawler[df_battles_trophy_brawler['played_brawler'] == brawler_name.upper()]
                        df_battles_trophy_cumsum = df_battles_trophy['trophyChange'].cumsum()

                        # Create a Plotly line chart
                        fig = px.line(df_battles_trophy, y=df_battles_trophy_cumsum)

                        # Hide axes and customize layout
                        fig.update_xaxes(visible=False, fixedrange=True)
                        fig.update_yaxes(visible=False, fixedrange=True)

                        # Customize the line color and layout
                        fig.update_traces(line=dict(color='lime', width=2))
                        fig.update_layout(
                            showlegend=False,
                            margin=dict(l=0, r=0, t=0, b=0),  # Remove margins to minimize space
                            height=100,  # Set a specific height for consistency
                            width=700    # Optional: Adjust the width to control the overall size
                        )

                        # Display the Plotly chart with a fixed height
                        st.plotly_chart(fig, use_container_width=True, height=100, config={'displayModeBar': False})
                    else:
                        fig = px.line(df_battles['trophyChange'].cumsum())

                        # Hide axes and customize layout
                        fig.update_xaxes(visible=False, fixedrange=True)
                        fig.update_yaxes(visible=False, fixedrange=True)

                        # Customize the line color and layout
                        fig.update_traces(line=dict(color='white', width=2))
                        fig.update_layout(
                            showlegend=False,
                            margin=dict(l=0, r=0, t=0, b=0),  # Remove margins to minimize space
                            height=100,  # Set a specific height for consistency
                            width=700    # Optional: Adjust the width to control the overall size
                            )


                        st.plotly_chart(fig, use_container_width=True, height=100, config={'displayModeBar': False})

                more_cols = st.columns([1,11]) 
                with more_cols[0]:
                    
                    st.image(f'{FILE_ROOT}/assets/Power_Points.png')
                    st.image('https://cdn-old.brawlify.com/icon/trophy.png')
                    st.image(f'{FILE_ROOT}/assets/victory.png')
                    st.image(f'{img}')
                    st.image('https://cdn-old.brawlify.com/icon/Ranking.png')
                    st.image(f'{FILE_ROOT}/assets/stopwatch.png')
                    st.image("https://cdn.brawlify.com/game-modes/regular/48000006.png")
                    st.image('https://cdn-old.brawlify.com/icon/trophy.png')
                    st.image('https://cdn-old.brawlify.com/icon/trophy.png')

                with more_cols[1]:
                    st.write(f'{brawler["power"]}')
                    st.write(f'{brawler["trophies"]}')
                    st.write(f'{brawler["highestTrophies"]}')
                    st.write(f"{brawler_pr*100 :.0f} % pick rate")
                    st.write(f"{brawler_wr*100 :.0f} % win rate")
                    st.write(f"{brawler_trophy_rate[0] :.0f} minutes")
                    st.write(f"{brawler_trophy_rate[1] :.0f} brawls")
                    st.write(f"{brawler_trophy_rate[2] :.1f} trophies per brawl")
                    st.write(f"{brawler_trophy_rate[3] :.1f} trophies per minute")

#st.write(player_data)