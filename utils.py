# utils.py
import streamlit_analytics2
import streamlit as st
import pandas as pd
import json
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import date, datetime
import requests
import pytz
from streamlit_toggle import toggle

class MyList(list):
    def last_index(self):
        return len(self) - 1

def load_from_firestore(counts, collection_name):
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
    col = db.collection(collection_name)
    firestore_counts = col.document(st.secrets["fb_col"]).get().to_dict()
    if firestore_counts is not None:
        for key in firestore_counts:
            if key in counts:
                counts[key] = firestore_counts[key]

def save_to_firestore(counts, collection_name):
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
    col = db.collection(collection_name)
    col.document(st.secrets["fb_col"]).set(counts)

def format_data(pokemon_family, shadow_only, df):
    if shadow_only:
        family_data = df[(df['Family'] == pokemon_family)].sort_values(by=['Shadow', 'ID'])
    else:
        family_data = df[(df['Family'] == pokemon_family) & (df['Shadow'] == False)]

    formatted_data = []
    attributes = ['Rank', 'IVs', 'CP', 'Level', 'MoveSet']
    leagues = ['Little', 'Great', 'Ultra', 'Master']

    for _, row in family_data.iterrows():
        for league in leagues:
            entry = {'Pokemon': row['Pokemon'], 'League': league}

            for attr in attributes:
                value = row[f'{league}_{attr}']
                attr = attr.replace("Level","Lvl")
                attr = attr.replace("Rank","#")
                entry[attr] = (
                    f'{int(value):,}' if pd.notna(value) and isinstance(value, (int, float)) else value.replace(',', '\n') if pd.notna(value) else ''
                )
            formatted_data.append(entry)
    return formatted_data



def filter_ids(row):
    current_id = row['ID']
    
    # Split the Evo_Fam into a list and remove everything after '&'
    evo_next_list = [elem.split('&')[0] for elem in row['Evo_Fam'].split(';')]
    
    if str(current_id) in evo_next_list:
        position = evo_next_list.index(str(current_id))
        filtered_list = evo_next_list[:position + 1]
    else:
        filtered_list = evo_next_list

    return list(filtered_list)

def get_top_50_ids(df, rank_column, league, top_n, fam, iv_bool, inv_bool, xl_var=True, all=False):
    df_all = df.sort_values(by=rank_column)
    df_filtered = df.dropna(subset=[rank_column])
    df_filtered = df_filtered[df_filtered[rank_column] <= top_n]

    if not xl_var:
        df_all = df_all[df_all[f'{league.capitalize()}_Level'] <= 40]
        df_filtered = df_filtered[df_filtered[f'{league.capitalize()}_Level'] <= 40]

    top_df = df_filtered.sort_values(by=rank_column).drop_duplicates(subset=['ID'])

    if fam:
        top_df['Filtered_Evo_next'] = top_df.apply(filter_ids, axis=1)
        all_ids_set = set([item for sublist in top_df['Filtered_Evo_next'] for item in sublist])
    else:
        all_ids_set = set(top_df['ID'].astype(str).tolist())

    all_ids = list(all_ids_set)

    if not all:
        prefix = (
            'cp-500&' if league == 'little' else
            'cp-1500&' if league == 'great' else
            'cp-2500&' if league == 'ultra' else
            ''
        )
    else:
        prefix = ''

    if inv_bool:
        if not all:
            cp_cap = (
                '501' if league == 'little' else
                '1501' if league == 'great' else
                '2501' if league == 'ultra' else
                ''
            )
            cp_threshold = f'cp{cp_cap}-'
        else:
            cp_threshold = ''

        # Build the inverted search string
        ids_strings_list = [f'!{id_},{cp_threshold}' for id_ in all_ids]
        ids_string = '&'.join(ids_strings_list)
    else:
        ids_string = prefix + ','.join(all_ids)

    if iv_bool and not inv_bool:
        if league != 'master':
            ids_string += "&0-1attack&3-4defense,3-4hp&2-4defense&2-4hp"
        else:
            ids_string += "&3*,4*"

    return ids_string.replace("&,", "&")


def make_search_string(df, league, top_n, fam, iv_b, inv_b,sho_xl_val, all_pre=False):
    if league == 'little':
        return get_top_50_ids(df, 'Little_Rank', 'little', top_n, fam, iv_b, inv_b, sho_xl_val,all_pre)
    elif league == 'great':
        return get_top_50_ids(df, 'Great_Rank', 'great', top_n, fam, iv_b, inv_b, sho_xl_val,all_pre)
    elif league == 'ultra':
        return get_top_50_ids(df, 'Ultra_Rank', 'ultra', top_n, fam, iv_b, inv_b, sho_xl_val,all_pre)
    elif league == 'master':
        return get_top_50_ids(df, 'Master_Rank', 'master', top_n, fam, iv_b, inv_b,True,all_pre)
    elif league == 'all':
        return (
            get_top_50_ids(df, 'Little_Rank', 'little', top_n, fam, iv_b, inv_b, sho_xl_val,all_pre)
            + ','
            + get_top_50_ids(df, 'Great_Rank', 'great', top_n, fam, iv_b, inv_b, sho_xl_val,all_pre)
            + ','
            + get_top_50_ids(df, 'Ultra_Rank', 'ultra', top_n, fam, iv_b, inv_b, sho_xl_val,all_pre)
            + ','
            + get_top_50_ids(df, 'Master_Rank', 'master', top_n, fam, iv_b, inv_b, True,all_pre)
        )

def format_data_top(df, league, num_rank,xl_var):
    family_data = df.sort_values(by=[f'{league}_Rank'])
    formatted_data = []
    attributes = ['Rank', 'IVs', 'CP', 'Level','MoveSet']

    for _, row in family_data.iterrows():
        if (not xl_var and row[f'{league}_Level'] <= 40) or xl_var:
            rank_value = (
                row[f'{league}_Rank']
                if pd.notna(row[f'{league}_Rank']) and isinstance(row[f'{league}_Rank'], (int, float))
                else row[f'{league}_Rank']
                if pd.notna(row[f'{league}_Rank'])
                else 201
            )
            if num_rank >= int(rank_value):
                entry = {'Pokemon': row['Pokemon']}
                for attr in attributes:
                    value = row[f'{league}_{attr}']
                    attr = attr.replace("Level","Lvl")
                    attr = attr.replace("Rank","#")
                    entry[attr] = (
                        f'{int(value):,}' if pd.notna(value) and isinstance(value, (int, float)) else value.replace(',', '\n') if pd.notna(value) else ''
                    )
                formatted_data.append(entry)
    return formatted_data

def calculate_days_since(xDate):
    start_date = xDate
    end_date = date.today()
    days_since = (end_date - start_date).days
    return days_since

def get_last_updated_date(GITHUB_API_URL):
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        commit_data = response.json()[0]
        commit_date = commit_data['commit']['committer']['date']
        est_time = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
        est_time = est_time.astimezone(pytz.timezone('America/New_York'))
        return est_time
