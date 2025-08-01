# app.py
from streamlit_extras.stylable_container import stylable_container
import streamlit as st
import pandas as pd
import streamlit_analytics2
import json
from datetime import date, datetime
import requests
import pytz
st.set_page_config(layout = "wide")
#st.set_page_config(layout="wide") 

# Import utility functions and session state manager
from utils import (
    MyList,
    load_from_firestore,
    save_to_firestore,
    format_data,
    filter_ids,
    get_top_50_ids,
    make_search_string,
    format_data_top,
    calculate_days_since,
    get_last_updated_date,
    swap_columns,
    get_translation,
    TRANSLATIONS_DF
)
from session_state_manager import (
    initialize_session_state,
    update_top_num,
    upd_shadow,
    upd_tab_str,
    upd_xl,
    upd_seas,
    upd_cust,
    upd_cust1,
    upd_cust2,
    upd_cust3,
    upd_inv,
    update_gym_bool,
    little_but,
    great_but,
    ultra_but,
    master_but,
    upd_shad_only,
    update_language,
    AVAILABLE_LANGUAGES
)

# Initialize session state
initialize_session_state()



query_params = st.query_params  #st.experimental_get_query_params()

#try:
#	if st.query_params["new_ranks"] == "true":
	#	st.session_state['show_custom1'] = True
	#	upd_cust1()
#except:
	#pass
	
season_start = date(2025, 3, 4)

# Set GitHub API URL based on 'show_custom' flag
if  st.session_state['show_custom2']:
    GITHUB_API_URL = 'https://api.github.com/repos/pvpiv/pogo_search_string/commits?path=pvp_data_fossil.csv'
    df = pd.read_csv('pvp_data_fossil.csv')
	
elif  st.session_state['show_custom3']:
  GITHUB_API_URL = 'https://api.github.com/repos/pvpiv/pogo_search_string/commits?path=pvp_data_summer.csv'
  df = pd.read_csv('pvp_data_summer.csv')
#elif  st.session_state['show_custom3']:
 # GITHUB_API_URL = 'https://api.github.com/repos/pvpiv/pogo_search_string/commits?path=pvp_data_Fossil.csv'
 # df = pd.read_csv('pvp_data_catch.csv')	
else:
    GITHUB_API_URL = 'https://api.github.com/repos/pvpiv/pogo_search_string/commits?path=pvp_data.csv'
    df = pd.read_csv('pvp_data.csv')

if st.session_state.show_shadow:
     df = df[df['Shadow']]
	
cols = st.columns((3,10,1))
with cols[0]:
    # Create a row with two columns for Settings and Language dropdown
    settings_col, lang_col = st.columns([1, 1])
    
    with settings_col:
        with stylable_container(
            key="Settings",
            css_styles="""
                button {
                    width: 100px;
                    height: 45px;
                    background-color: green;
                    color: white;
                    border-radius: 5px;
                    white-space: nowrap;
                }
                """,
        ):
            popover = st.popover('Settings', use_container_width=True)
            popover.divider()
            
            if not st.session_state['table_string_butt']:
                butt_label = "Switch to Search Strings"
               # show_custom_boxz2 = popover.checkbox('Retro Cup', on_change=upd_cust1, key='sho_cust1')
                #show_custom_boxz = popover.checkbox('Great Fossil Cup', on_change=upd_cust1, key='sho_cust2')

               # show_custom_boxz2 = popover.checkbox('Great Fossil Cup', value=st.session_state['show_custom2'], on_change=upd_cust2, key='sho_cust2')
                show_custom_boxz =  popover.checkbox('Great Fossil Cup', value=st.session_state['show_custom2'], on_change=upd_cust2, key='sho_cust2')
                show_custom_boxz2 =  popover.checkbox('Ultra Summer Cup', value=st.session_state['show_custom3'], on_change=upd_cust3, key='sho_cust3')
                show_shadow_boxz = popover.checkbox('Include Shadow Pokémon', on_change=upd_shadow, key='sho_shad', value=st.session_state['get_shadow'])

            else:
                butt_label = "Switch to Pokémon Lookup"
              #  show_custom_boxz2 = popover.checkbox('Great Fossil Cup' , value=st.session_state['show_custom2']  , on_change=upd_cust2, key='sho_cust2')
                show_custom_boxz =  popover.checkbox('Great Fossil Cup', value=st.session_state['show_custom2'], on_change=upd_cust2, key='sho_cust2')
                show_custom_boxz2 =  popover.checkbox('Ultra Summer Cup', value=st.session_state['show_custom3'], on_change=upd_cust3, key='sho_cust3')
                show_gym_box = popover.checkbox('Gym Attackers/Defenders', on_change=update_gym_bool, key='sho_gym')
                popover.divider()
               
                fam_box = popover.checkbox('Include pre-evolutions', value=True)
                show_xl_boxz = popover.checkbox('Include XL Pokémon \n\n(XL Candy needed)', on_change=upd_xl, key='sho_xl', value=st.session_state['show_xl'])
                iv_box = popover.checkbox('Include IV Filter \n\n(Works for Non XL Pokémon)', value=True)
                inv_box = popover.checkbox('Invert strings', value=st.session_state.show_inverse, key='show_inv')# tables_pop = st.popover("League Tables")
                shad_box = popover.checkbox('Shadow Only', value=st.session_state.show_shadow, key='sho_shad', on_change=upd_shad_only)
    

        
    st.toggle(
        label=butt_label,
        key= "tab_str_butt",
        value = st.session_state['table_string_butt'],
        on_change = upd_tab_str
    )
  #  season_box = st.checkbox('Next Season Rankings', value=st.session_state['show_custom1'] , on_change=upd_cust1, key='sho_cust1')
 
    with lang_col:
        st.selectbox(
            "Language",
            options=AVAILABLE_LANGUAGES,
            key="sidebar_lang_choice_box",
            index=AVAILABLE_LANGUAGES.index(st.session_state['language']),
            on_change=update_language,
            label_visibility="collapsed"
        )
 
	
with cols[1]:

    #str_tab_but = st.button(butt_label,key="tab_str_butt",on_click=upd_tab_str,use_container_width =True)
    
    today = date.today()
    # Section 1 - PVP Pokemon Search Table
    show_shadow = st.session_state['get_shadow']
    pokemon_list = MyList(df[~df['Pokemon'].str.contains("Shadow", na=False)]['Pokemon'].unique())

    if not st.session_state['table_string_butt']:
        if pokemon_list:
            poke_label = 'All League Rankings, IVs, & Moves Table' if not st.session_state['show_custom'] else 'Custom Cup Rankings, IVs, & Moves Table'
            st.subheader(poke_label)
            pokemon_choice = st.selectbox(
                "",
                pokemon_list,
                index=pokemon_list.last_index(),
                key="poke_choice",label_visibility='hidden',
                on_change=lambda: st.session_state.update({'get_dat': True})
            )
        
            if pokemon_choice != "Select a Pokemon" and pokemon_choice != "Select a Shadow Pokemon":
                if st.session_state['get_dat'] and pokemon_choice:
                    if st.session_state['last_sel'] != pokemon_choice or st.session_state['last_sel'] is None:
                        load_from_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
                        streamlit_analytics2.start_tracking()
        
                    st.session_state['last_sel'] = pokemon_choice
                    pokemon_family = df[df['Pokemon'] == pokemon_choice]['Family'].iloc[0]
                    family_data = format_data(pokemon_family, show_shadow, df)
        
                    if family_data:
                        st.text_input(
                            label=today.strftime("%m/%d/%y"),
                            value=pokemon_choice,
                            disabled=True,
                            label_visibility='hidden'
                        )
                        df_display = pd.DataFrame(family_data)
                        df_display.set_index(['Pokemon'])#, inplace=True)
                        #st.markdown(swap_columns(df_display)
                        st.markdown(df_display.style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
                        try:
                            save_to_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
                            streamlit_analytics2.stop_tracking(unsafe_password=st.secrets['pass'])
                        except:
                            pass
                    else:
                        st.session_state['get_dat'] = False
            else:
                try:
                    save_to_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
                    streamlit_analytics2.stop_tracking(unsafe_password=st.secrets['pass'])
                except:
                    pass
        else:
            try:
                save_to_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
                streamlit_analytics2.stop_tracking(unsafe_password=st.secrets['pass'])
            except:
                pass
        st.divider()
    
        # Section 2 - Pokemon Search String
        
        
    elif st.session_state['table_string_butt']:
        st.subheader("PVP Poké Search Strings")
        
        top_nbox = st.number_input(
            label = 'Showing Top:',
            value=st.session_state.top_num,
            key='top_no',
            on_change=update_top_num,
            min_value=5,
            max_value=250,
            step=5
        )
    
        # Check if we're in terminal mode
        is_terminal_mode = st.query_params.get('terminal', 'false').lower() == 'true'
        
        if is_terminal_mode:
            # Add buttons for CSV export and terminal strings
            col1, col2 = st.columns(2)
            
            with col1:
                # Create a list to store all table data
                all_data = []
                
                # Function to get table data for a league
                def get_league_data(league_name, df, top_n, show_xl):
                    data = format_data_top(df, league_name, top_n, show_xl)
                    for row in data:
                        row['League'] = league_name
                        # Split IVs into separate columns
                        if 'IVs' in row and pd.notna(row['IVs']):
                            ivs = row['IVs'].split('/')
                            if len(ivs) == 3:
                                row['Attack'] = ivs[0].strip()
                                row['Defense'] = ivs[1].strip()
                                row['HP'] = ivs[2].strip()
                    return data
                
                # Get data for each league
                leagues = ['Great', 'Ultra', 'Master', 'Little']
                for league in leagues:
                    league_data = get_league_data(league, df, st.session_state.top_num, show_xl_boxz)
                    all_data.extend(league_data)
                
                # Convert to DataFrame
                all_df = pd.DataFrame(all_data)
                
                # Ensure Attack, Defense, HP columns always exist
                for col in ['Attack', 'Defense', 'HP']:
                    if col not in all_df.columns:
                        all_df[col] = ''
                
                # Reorder columns to put Attack, Defense, HP after IVs
                cols = all_df.columns.tolist()
                if 'IVs' in cols:
                    ivs_idx = cols.index('IVs')
                    # Remove if already present
                    for col in ['Attack', 'Defense', 'HP']:
                        if col in cols:
                            cols.remove(col)
                    # Insert after IVs
                    cols[ivs_idx+1:ivs_idx+1] = ['Attack', 'Defense', 'HP']
                    all_df = all_df[cols]
                
                csv = all_df.to_csv(index=False).encode('utf-8')
                
                # Direct download button
                st.download_button(
                    "Download All Tables CSV",
                    csv,
                    "all_leagues_data.csv",
                    "text/csv",
                    key='download-all-csv'
                )
            
            with col2:
                if st.button('Show Terminal Strings'):
                    # Create table data
                    terminal_data = []
                    leagues = ['great', 'ultra', 'master', 'little']
                    
                    # Define IV filter combinations with their display names
                    iv_filters = [
                        ("&0-1attack&2-4defense&2-4hp", "2-4Def&2-4HP"),
                        ("&0-1attack&3-4defense&3-4hp", "3-4Def&3-4HP"),
                        ("&0-1attack&2-4defense&3-4hp", "2-4Def&3-4HP"),
                        ("&0-1attack&3-4defense&2-4hp", "3-4Def&2-4HP")
                    ]
                    
                    for league in leagues:
                        base_string = make_search_string(df, league, st.session_state.top_num, fam_box, False, inv_box, show_xl_boxz, False, shad_only=shad_box, language=st.session_state['language'])
                        # Remove any existing IV filters
                        base_string = base_string.split('&0-1attack')[0] if '&0-1attack' in base_string else base_string
                        
                        for iv_filter, iv_display in iv_filters:
                            terminal_data.append({
                                'League': league.capitalize(),
                                'IV Filter': iv_display,
                                'String': base_string + iv_filter
                            })
                    
                    # Display as table
                    terminal_df = pd.DataFrame(terminal_data)
                    st.dataframe(terminal_df.set_index('League'), use_container_width=True)
                    
                    # Add download button for terminal strings
                    csv = terminal_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Terminal Strings CSV",
                        csv,
                        "terminal_strings.csv",
                        "text/csv",
                        key='download-terminal-csv'
                    )

        if not (st.session_state['show_custom1'] or st.session_state['show_custom3'] or st.session_state['show_custom2'] or st.session_state['gym_bool']):
            
    
            try:
                st.write(f'Great League Top {st.session_state.top_num} Search String:')
                st.code(make_search_string(df, "great", st.session_state.top_num, fam_box, iv_box, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
                lab_gre = "Show Great Table"
                if st.session_state['great_clicked']:
                    lab_gre  = "Hide Great Table"
                    st.button(lab_gre,on_click = great_but)
                    family_data_Great = format_data_top(df, 'Great', st.session_state.top_num,show_xl_boxz)
                    df_display_Great = pd.DataFrame(family_data_Great)
                    df_display_Great.set_index(['#'])#, inplace=True)
                    st.markdown(swap_columns(df_display_Great,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
                    #   st.markdown(swap_columns(df_display_Great)
                else:
                    st.button(lab_gre,on_click = great_but)
                
            except:
                pass
    
            try:
                st.write(f'Ultra League Top {st.session_state.top_num} Search String:')
                st.code(make_search_string(df, "ultra", st.session_state.top_num, fam_box, iv_box, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
                lab_ult = "Show Ultra Table"
                if st.session_state['ultra_clicked']:
                    lab_ult  = "Hide Ultra Table"
                    family_data_Ultra = format_data_top(df, 'Ultra', st.session_state.top_num,show_xl_boxz)
                    df_display_Ultra = pd.DataFrame(family_data_Ultra)
                    df_display_Ultra.set_index(['#'])
                    st.button(lab_ult,on_click = ultra_but)
                    st.markdown(swap_columns(df_display_Ultra,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
                else:
                    st.button(lab_ult,on_click = ultra_but)
                
            except:
                pass
    
            try:
                st.write(f'Master League Top {st.session_state.top_num} Search String:')
                st.code(make_search_string(df, "master", st.session_state.top_num, fam_box, iv_box, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
                lab_mast = "Show Master Table"
                if st.session_state['master_clicked']:
                    lab_mast  = "Hide Master Table"
                    family_data_master = format_data_top(df, 'Master', st.session_state.top_num,True)
                    df_display_master = pd.DataFrame(family_data_master)
                    df_display_master.set_index(['#'])
                    st.button(lab_mast, on_click = master_but)
                    st.markdown(swap_columns(df_display_master,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
                else:
                    st.button(lab_mast,on_click = master_but)
                
            except:
                pass
            try:
                st.write(f'Little League Top {st.session_state.top_num} Search String:')
                st.code(make_search_string(df, "little", st.session_state.top_num, fam_box, iv_box, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
                lab_lit = "Show Little Table"
                if st.session_state['little_clicked']:
                    lab_lit = "Hide Little Table"
                    st.button(lab_lit,on_click = little_but)
                    family_data_Little = format_data_top(df, 'Little', st.session_state.top_num,show_xl_boxz)
                    df_display_Little = pd.DataFrame(family_data_Little)
                    df_display_Little.set_index(['#'])
                    st.markdown(swap_columns(df_display_Little,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)  
                else: 
                    st.button(lab_lit,on_click = little_but)     
                
            except:
                pass
            try:
                st.write(f'All Leagues Top {st.session_state.top_num} Search String:')
                st.code(make_search_string(df, "all", st.session_state.top_num, fam_box, False, inv_box, show_xl_boxz, True,shad_only=shad_box, language = st.session_state['language']))
            except:
                pass
        elif st.session_state['gym_bool']: 
            attackers = pd.read_csv('attackers.csv')
            defenders = pd.read_csv('defenders.csv')
            try:
                st.write(f'Defenders Search String:')
                st.code(make_search_string(defenders, "master", st.session_state.top_num, fam_box, False, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
                lab_def = "Show Defenders Table"
                if st.session_state['master_clicked']:
                    lab_def = "Hide Defenders Table"
                    st.button(lab_def,on_click = master_but)
                    family_data_def = format_data_top(defenders, 'Master', st.session_state.top_num,show_xl_boxz)
                    df_display_def = pd.DataFrame(family_data_def)
                    df_display_def.set_index(['#'])
                    st.markdown(swap_columns(df_display_def,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
                else:
                    st.button(lab_def,on_click = master_but)
            except:
                pass
            try:
                st.write(f'Attackers Search String:')
                st.code(make_search_string(attackers, "master", st.session_state.top_num, fam_box, False, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
                lab_att = "Show Attackers Table"
                if st.session_state['ultra_clicked']:
                    lab_att = "Hide Attackers Table"
                    st.button(lab_att,on_click = ultra_but)
                    family_data_att = format_data_top(attackers, 'Master', st.session_state.top_num,show_xl_boxz)
                    df_display_att = pd.DataFrame(family_data_att)
                    df_display_att.set_index(['#'])
                    st.markdown(swap_columns(df_display_att,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
                else:
                    st.button(lab_att,on_click = ultra_but)
            except:
                pass
        elif st.session_state['show_custom3']:
            try:
                lab_ult = "Show Ultra Summer Cup Table"
                st.write(f'Ultra League Top {st.session_state.top_num} Search String:')
                st.code(make_search_string(df, "ultra", st.session_state.top_num, fam_box, iv_box, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
                lab_ult = "Show Ultra Table"
                if st.session_state['ultra_clicked']:
                    lab_ult  = "Hide Ultra Table"
                    family_data_Ultra = format_data_top(df, 'Ultra', st.session_state.top_num,show_xl_boxz)
                    df_display_Ultra = pd.DataFrame(family_data_Ultra)
                    df_display_Ultra.set_index(['#'])
                    st.button(lab_ult,on_click = ultra_but)
                    st.markdown(swap_columns(df_display_Ultra,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
                else:
                    st.button(lab_ult,on_click = ultra_but)
                
            except:
                pass
        elif st.session_state['show_custom1']: 
            try:
                st.write(f'Little League Top {st.session_state.top_num} Search String:')
                st.code(make_search_string(df, "little", st.session_state.top_num, fam_box, iv_box, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
                lab_lit = "Show Great Fossil Table"
                if st.session_state['little_clicked']:
                    lab_lit = "Hide Great Fossil Table"
                    st.button(lab_lit,on_click = little_but)
                    family_data_Little = format_data_top(df, 'Little', st.session_state.top_num,show_xl_boxz)
                    df_display_Little = pd.DataFrame(family_data_Little)
                    df_display_Little.set_index(['#'])
                    st.markdown(swap_columns(df_display_Little,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)  
                else: 
                    st.button(lab_lit,on_click = little_but)   
                
            except:
                pass
        elif st.session_state['show_custom2']: 


            lab_gre = "Show Great Fossil Cup Table"
            st.write(f'Great Fossil Cup Top {st.session_state.top_num} Search String:')
            st.code(make_search_string(df, "great", st.session_state.top_num, fam_box, iv_box, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
            lab_gre = "Show Great Fossil Cup Table"
            if st.session_state['great_clicked']:
                lab_gre  = "Hide Great Fossil Cup Table"
                st.button(lab_gre,on_click = great_but)
                family_data_Great = format_data_top(df, 'Great', st.session_state.top_num,show_xl_boxz)
                df_display_Great = pd.DataFrame(family_data_Great)
                df_display_Great.set_index(['#'])
                st.markdown(swap_columns(df_display_Great,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
            else:
                st.button(lab_gre,on_click = great_but)
	     
        elif st.session_state['show_custom']: 
            lab_gre = "Show Great Fossil Cup Table"
            st.write(f'Great Fossil Cup Top {st.session_state.top_num} Search String:')
            st.code(make_search_string(df, "great", st.session_state.top_num, fam_box, iv_box, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
            lab_gre = "Show Great Retro Cup Table"
            if st.session_state['great_clicked']:
                lab_gre  = "Hide Great Retro Cup Table"
                st.button(lab_gre,on_click = great_but)
                family_data_Great = format_data_top(df, 'Great', st.session_state.top_num,show_xl_boxz)
                df_display_Great = pd.DataFrame(family_data_Great)
                df_display_Great.set_index(['#'])
                st.markdown(swap_columns(df_display_Great,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
            else:
                st.button(lab_gre,on_click = great_but)
		    
        elif st.session_state['show_custom3']: 

            lab_ult = "Show Ultra Summer Cup Table"
            st.write(f'Ultra League Top {st.session_state.top_num} Search String:')
            st.code(make_search_string(df, "ultra", st.session_state.top_num, fam_box, iv_box, inv_box, show_xl_boxz, False,shad_only=shad_box, language = st.session_state['language']))
            lab_ult = "Show Ultra Table"
            if st.session_state['ultra_clicked']:
                lab_ult  = "Hide Ultra Table"
                family_data_Ultra = format_data_top(df, 'Ultra', st.session_state.top_num,show_xl_boxz)
                df_display_Ultra = pd.DataFrame(family_data_Ultra)
                df_display_Ultra.set_index(['#'])
                st.button(lab_ult,on_click = ultra_but)
                st.markdown(swap_columns(df_display_Ultra,"Pokemon","#").style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
            else:
                st.button(lab_ult,on_click = ultra_but)
        
        try:
            load_from_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
            streamlit_analytics2.start_tracking()
        
        
            topstrin = str(st.session_state.top_num)
            if st.session_state['show_custom']:
                copy_val = f'*Click string to show Copy button and Paste Top {topstrin} Master Premier Cup into PokeGO {st.session_state['language']}*'
            if st.session_state['show_custom1']:
                copy_val = f'*Click string to show Copy button and Paste Top {topstrin} Ultra element Cup into PokeGO {st.session_state['language']}*'
            elif st.session_state['show_custom2']:
                copy_val = f'*Click string to show Copy button and Paste Top {topstrin} Great Fossil Cup into PokeGO {st.session_state['language']}*'
            else:
                copy_val = f'*Click string to show Copy button and Paste Top {topstrin} into PokeGO {st.session_state['language']}*'
            st.text_input(
                label=today.strftime("%m/%d/%y"),
                value= copy_val,
                label_visibility='hidden',
                disabled=True,
                key="sstring"
            )
            st.divider()
            with st.form('chat_input_form',clear_on_submit =True):

                col3, col4 = st.columns([3,1]) 

                with col3:
                    prompt = st.text_input(placeholder = "Feedback", label="Feedback", key="fstring", label_visibility='collapsed')

                with col4:
                    submitted = st.form_submit_button('Submit')

                if prompt and submitted:
            # Do something with the inputted text here
                    st.write(f"Submitted: {prompt}")
            #st.text_input()
            save_to_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
            streamlit_analytics2.stop_tracking(unsafe_password=st.secrets['pass'])
    
           # load_from_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
           # streamlit_analytics2.start_tracking()
            if st.session_state['little_clicked']:
                st.text_input(
                    label=today.strftime("%m/%d/%y"),
                    value='Little Table',
                    label_visibility='hidden',
                    disabled=True,
                    key="little_text"
                )
            if st.session_state['great_clicked']:
                st.text_input(
                    label=today.strftime("%m/%d/%y"),
                    value='Great Table',
                    label_visibility='hidden',
                    disabled=True,
                    key="great_text"
                )
            if st.session_state['ultra_clicked']:
                st.text_input(
                    label=today.strftime("%m/%d/%y"),
                    value='Ultra Table',
                    label_visibility='hidden',
                    disabled=True,
                    key="ultra_text"
                )
            if st.session_state['master_clicked']:
                st.text_input(
                    label=today.strftime("%m/%d/%y"),
                    value='Master Table',
                    label_visibility='hidden',
                    disabled=True,
                    key="master_text"
                )
           # save_to_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
          #  streamlit_analytics2.stop_tracking(unsafe_password=st.secrets['pass'])
    
        # Get the last updated date

        except:
            pass
        last_updated = get_last_updated_date(GITHUB_API_URL)
        st.write(f"Last updated: {last_updated} (EST)")



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}

footer {
	
	visibility: hidden;
	
	}
footer:after {
	content:'goodbye'; 
	visibility: visible;
	display: block;
	position: relative;
	#background-color: red;
	padding: 5px;
	top: 2px;
}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
