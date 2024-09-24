import streamlit as st 
import json
import pandas as pd 

from dags.brawl_reqs import get_player, get_playerBattleLog

st.title('BrawlStats')
st.write('A Brawl Stars Stats App')

user_tag = st.text_input('Tag here')

if user_tag:
    player_data = get_player(user_tag)
    battlelog_data = get_playerBattleLog(user_tag)

    player_data = json.loads(player_data)
    battlelog_data = json.loads(battlelog_data)
    
    player_data
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image('https://cdn-old.brawlify.com/trophies.png')
            st.metric('trophies', player_data['trophies'])
        with col2:
            st.metric('expLevel', player_data['expLevel'])
        with col3:
            st.image('https://cdn-old.brawlify.com/icon/PowerPoint.png')
            st.metric('expPoints', player_data['expPoints'])

    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Number of Brawlers', len(player_data['brawlers']))
        with col2:
            st.metric('3vs3Victories', player_data['3vs3Victories'])
        with col3:
            st.metric('CLub', player_data['club']['name'])

    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Number of Battles', len(battlelog_data['items']))
        with col2:
            st.metric('soloVictories', player_data['soloVictories'])
        with col3:
            st.metric('duoVictories', player_data['duoVictories'])

    battles = battlelog_data['items']
    battles_out = []
    battlelog_data
    
    for battle in battles:
        battle_params = battle['battle'].keys()
        if 'result' in battle_params:
            battle_results = battle['battle']['result']
        else:
            rank = battle['battle']['rank']
            if rank <= 3:
                battle_results = 'victory'
            else:
                battle_results = 'defeat'

        if 'mode' in battle_params:
            battle_modes = battle['battle']['mode']
        else:
            battle_modes = ""

        if 'duration' in battle_params:
            battle_duration = battle['battle']['duration']
        else:
            battle_duration = ""

        battles_out.append((battle_modes,battle_results,battle_duration))

    df = pd.DataFrame(battles_out, columns=['mode', 'result','duration'])
    df['duration'] = df['duration'].apply(lambda x : '90' if not x else x)
    modes_df = pd.DataFrame(df.value_counts().reset_index())
    st.bar_chart(modes_df, x='mode', y='count')
    st.bar_chart(modes_df, x='result', y='count')
    st.dataframe(modes_df)
    st.scatter_chart(modes_df, x='duration', y='count')

    #df_battles = pd.DataFrame(battles)
    #st.dataframe(df_battles)
