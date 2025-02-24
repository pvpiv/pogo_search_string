# app.py
from streamlit_extras.stylable_container import stylable_container
import streamlit as st
import pandas as pd
import streamlit_analytics2
import json
from datetime import date, datetime
import requests
import pytz
from st_aggrid import (
    GridOptionsBuilder,
    AgGrid,
    GridUpdateMode,
    DataReturnMode,
    ColumnsAutoSizeMode,
    AgGridTheme
)

def configure_ag_grid(df, cols=None):
    custom_css = {
	".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "48px !important",
	"font-family": "Roboto, sans-serif !important;"},
	#".ag-header-cell-text": {"color": "#495057 !important;"},
	".ag-header-font-size": {"font-size": "56 px"},
	#".ag-theme-alpine .ag-header .ag-cell": {"font-size" : "32 px;"},
	".ag-theme-alpine .ag-ltr .ag-cell": {"color": "#444 !important;"},
	".ag-theme-alpine .ag-row-odd": {"background": "rgba(243, 247, 249, 0.3) !important;",
	"border": "1px solid #eee !important;"},
	".ag-theme-alpine .ag-row-even": {"border-bottom": "1px solid #eee !important;"},
	".ag-theme-light button": {"font-size": "0 !important;", "width": "auto !important;", "height": "24px !important;",
	"border": "1px solid #eee !important;", "margin": "4px 2px !important;",
	"background": "#3162bd !important;", "color": "#fff !important;",
	"border-radius": "3px !important;"},
	".ag-theme-light button:before": {"content": "‘Confirm’ !important", "position": "relative !important",
	"z-index": "1000 !important", "top": "0 !important",
	"font-size": "48px !important", "left": "4 !important",
	"padding": "4px !important"},
	
	}

    if cols is None:
        cols = df.columns
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options()
    
    for col in cols:
        if col == "MoveSet":
            # Enable wrap on the MoveSet column:
            gb.configure_column(
                col,
                wrapText=True,
               # autoHeight=True,
                cellStyle={'white-space': 'normal','font-size': '32px'},
            )

    
    gridOptions = gb.build()
    AgGrid(
        df,
        gridOptions=gridOptions,
        theme = 'alpine',
       # columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
       # style={},
       
        custom_css=custom_css,
        allow_unsafe_jscode=True
    )





#st.set_page_config(layout = "wide")
st.set_page_config(layout="wide")

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
    get_last_updated_date
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
    upd_inv,
    update_gym_bool,
    little_but,
    great_but,
    ultra_but,
    master_but
)

# Initialize session state
initialize_session_state()



query_params = st.query_params  #st.experimental_get_query_params()

try:
	if st.query_params["comm"] == "True":
		st.session_state['show_custom2'] = True
		upd_cust2()
except:
	pass
	
season_start = date(2024, 9, 3)

# Set GitHub API URL based on 'show_custom' flag
if not st.session_state['show_custom2']:
    GITHUB_API_URL = "https://api.github.com/repos/pvpiv/pogo_search_string/commits?path=pvp_data.csv"
else:
    GITHUB_API_URL = "https://api.github.com/repos/pvpiv/pogo_search_string/commits?path=pvp_data_Mega Master.csv"

# Load data
#if  st.session_state['show_custom1']
if st.session_state['show_custom2']:
    df = pd.read_csv('pvp_data_mega.csv')
else:
    df = pd.read_csv('pvp_data.csv')


       
   
# Replace your existing code that creates 'cols = st.columns((2,5,1))'
# and the toggles/checkboxes with something like this:
with st.container():
    st.subheader("PVP Poké Search Strings")
    # Create one row with three columns
    cola1, cola2, cola3 = st.columns([1, 2, 1])  # adjust ratios as desired

		
 
    with cola1:
        # Put the stylable_container + Settings popover here
        with stylable_container(
            key="Settings",
            css_styles="""
                button {
                    width: 150px;
                    height: 45px;
                    background-color: green;
                    color: white;
                    border-radius: 5px;
                    white-space: nowrap;
                }
            """,
        ):
            popover = st.popover('Settings', use_container_width=True)

            # Example checkboxes inside the popover:
            show_custom_boxz2 = popover.checkbox(
                'Mega Master Cup',
                value=st.session_state['show_custom2'],
                on_change=upd_cust2,
                key='sho_cust2'
            )
            show_shadow_boxz = popover.checkbox(
                'Include Shadow Pokémon',
                on_change=upd_shadow,
                key='sho_shad',
                value=st.session_state['get_shadow']
            )
            if st.session_state['table_string_butt']:
                show_gym_box = popover.checkbox('Gym Attackers/Defenders', on_change=update_gym_bool, key='sho_gym')
                popover.divider()
                topstrin = str(st.session_state.top_num)
                fam_box = popover.checkbox('Include pre-evolutions', value=True)
                show_xl_boxz = popover.checkbox('Include XL Pokémon \n\n(XL Candy needed)', on_change=upd_xl, key='sho_xl', value=st.session_state['show_xl'])
                iv_box = popover.checkbox('Include IV Filter \n\n(Works for Non XL Pokémon)', value=True)
                inv_box = popover.checkbox('Invert strings', value=st.session_state.show_inverse, key='show_inv')
        if st.session_state['table_string_butt']:

            top_nbox = st.number_input(
                'Showing Top:',
                value=st.session_state.top_num,
                key='top_no',
                on_change=update_top_num,
                min_value=5,
                max_value=200,
                step=5
                )
            
    with cola2:    
        if st.session_state['table_string_butt']:
            butt_label = "Switch to Pokémon Lookup"
        	
            
        else:
            butt_label = "Switch to Search Strings"

        st.toggle(
            label=butt_label,
            key="tab_str_butt",
            value=st.session_state['table_string_butt'],
            on_change=upd_tab_str
        )
        
 
        # The toggle for switching between table vs. search strings
       
        

    
with st.container():
# Then continue the rest of your code normally below...
# e.g. the logic for displaying search strings, or for the big table, etc.


    colb1, colb2 =  st.columns([9,1])
    with colb1:

        #str_tab_but = st.button(butett_label,key="tab_str_butt",on_click=upd_tab_str,use_container_width =True)
        
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
                            st.text_input(label=today.strftime("%m/%d/%y"),
                                value=pokemon_choice,
                                disabled=True,
                                label_visibility='hidden'
                            )
                            df_display = pd.DataFrame(family_data)
                            df_display.set_index(['Pokemon'])
                            
                            gb = GridOptionsBuilder.from_dataframe(df_display)
                            other_options = {'suppressColumnVirtualisation': True}
                            gb.configure_grid_options(**other_options)
                            gridOptions = gb.build()
                
                            grid = AgGrid(
                    df_display,
                    gridOptions=gridOptions,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                    )
                            try:
                                
                                save_to_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
                                streamlit_analytics2.stop_tracking(unsafe_password=st.secrets['pass'])
                            except:
                                pass
                        else:
                            st.session_state['get_dat'] = False
            else:
                try:
                    streamlit_analytics2.stop_tracking(unsafe_password=st.secrets['pass'])
                except:
                    pass
            
            st.divider()
        else:
            # Section 2 - Pokemon Search String
            
            


                
                #tables_pop = st.popover("League Tables")
                
                if not (st.session_state['show_custom'] or st.session_state['show_custom1'] or st.session_state['show_custom2'] or st.session_state['gym_bool']):
                    
            
                    try:
                        st.write(f'Great League Top {st.session_state.top_num} Search String:')
                        st.code(make_search_string(df, "great", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz,False))
                        lab_gre = "Show Great Table"
                        if st.session_state['great_clicked']:
                            lab_gre  = "Hide Great Table"
                            st.button(lab_gre,on_click = great_but)
                            family_data_Great = format_data_top(df, 'Great', st.session_state.top_num,show_xl_boxz)
                            df_display_Great = pd.DataFrame(family_data_Great)
                        #  df_display_Great.set_index(['Pokemon'], inplace=True)
                        # AgGrid(

                        # columnDefs = [{"field": "Pokemon", "sortable": False },{"field": "N"},{"field": "IVs"},{"field": "CP"},{"field": "Lvl"},{"field": "Moves"}]
                            configure_ag_grid(df_display_Great)

    #                        other_options = {'suppressColumnVirtualisation': True}
                        #  gb = GridOptionsBuilder.from_dataframe(df_display_Great)
                        #   other_options = {'suppressColumnVirtualisation': True,'wrapText':True,'fit_columns_on_grid_load':True,'height':None}
                        # gb.configure_grid_options(**other_options)

                            # Configure the MoveSet column to wrap text and adjust height
                    #     gb.configure_column("MoveSet", wrapText=True)

                        #   gridOptions = gb.build()
                        #  grid = AgGrid(
                        #      df_display_Great,
                            #  gridOptions=gridOptions)
                        else:
                            st.button(lab_gre,on_click = great_but)
                        
                    except:
                        pass
            
                    try:
                        st.write(f'Ultra League Top {st.session_state.top_num} Search String:')
                        st.code(make_search_string(df, "ultra", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz))
                        lab_ult = "Show Ultra Table"
                        if st.session_state['ultra_clicked']:
                            lab_ult  = "Hide Ultra Table"
                            family_data_Ultra = format_data_top(df, 'Ultra', st.session_state.top_num,show_xl_boxz)
                            df_display_Ultra = pd.DataFrame(family_data_Ultra)
                            df_display_Ultra.set_index(['Pokemon'], inplace=True)
                            st.button(lab_ult,on_click = ultra_but)
                    
                            gb = GridOptionsBuilder.from_dataframe(df_display_Ultra)
                            other_options = {'suppressColumnVirtualisation': True}
                            gb.configure_grid_options(**other_options)
                            gridOptions = gb.build()
                
                            grid = AgGrid(
                    df_display_Ultra,
                    gridOptions=gridOptions,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                    )

                        else:
                            st.button(lab_ult,on_click = ultra_but)
                        
                    except:
                        pass
            
                    try:
                        st.write(f'Master League Top {st.session_state.top_num} Search String:')
                        st.code(make_search_string(df, "master", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz))
                        lab_mast = "Show Master Table"
                        if st.session_state['master_clicked']:
                            lab_mast  = "Hide Master Table"
                            family_data_master = format_data_top(df, 'Master', st.session_state.top_num,True)
                            df_display_master = pd.DataFrame(family_data_master)
                        # df_display_master.set_index(['Pokemon'])
                            st.button(lab_mast, on_click = master_but)

                            gb = GridOptionsBuilder.from_dataframe(df_display_master)
                            other_options = {'suppressColumnVirtualisation': True}
                            gb.configure_grid_options(**other_options)
                            gridOptions = gb.build()
                
                            grid = AgGrid(
                    df_display_master,
                    gridOptions=gridOptions,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                    )                #  df_display_Great.set_index(['Pokemon'], inplace=True)
    
                        
                        else:
                            st.button(lab_mast,on_click = master_but)
                        
                    except:
                        pass
                    try:
                        st.write(f'Little League Top {st.session_state.top_num} Search String:')
                        st.code(make_search_string(df, "little", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz))
                        lab_lit = "Show Little Table"
                        if st.session_state['little_clicked']:
                            lab_lit = "Hide Little Table"
                            st.button(lab_lit,on_click = little_but)
                            family_data_Little = format_data_top(df, 'Little', st.session_state.top_num,show_xl_boxz)
                            df_display_Little = pd.DataFrame(family_data_Little)
                            df_display_Little.set_index(['Pokemon'], inplace=True)

                            gb = GridOptionsBuilder.from_dataframe(df_display_Little)
                            other_options = {'suppressColumnVirtualisation': True}
                            gb.configure_grid_options(**other_options)
                            gridOptions = gb.build()
                
                            grid = AgGrid(
                    df_display_Little,
                    gridOptions=gridOptions,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                    )         
                        else: 
                            st.button(lab_lit,on_click = little_but)     
                        
                    except:
                        pass
                    try:
                        st.write(f'All Leagues Top {st.session_state.top_num} Search String:')
                        st.code(make_search_string(df, "all", st.session_state.top_num, fam_box, False, inv_box,show_xl_boxz,True))
                    except:
                        pass
                elif st.session_state['gym_bool']: 
                    attackers = pd.read_csv('attackers.csv')
                    defenders = pd.read_csv('defenders.csv')
                    try:
                        st.write(f'Defenders Search String:')
                        st.code(make_search_string(defenders, "master", st.session_state.top_num, fam_box, False, inv_box,show_xl_boxz))
                        lab_def = "Show Defenders Table"
                        if st.session_state['master_clicked']:
                            lab_def = "Hide Defenders Table"
                            st.button(lab_def,on_click = master_but)
                            family_data_def = format_data_top(defenders, 'Master', st.session_state.top_num,show_xl_boxz)
                            df_display_def = pd.DataFrame(family_data_def)
                            df_display_def.set_index(['Pokemon'], inplace=True)

                            gb = GridOptionsBuilder.from_dataframe(df_display_def)
                            other_options = {'suppressColumnVirtualisation': True}
                            gb.configure_grid_options(**other_options)
                            gridOptions = gb.build()
                
                            grid = AgGrid(
                    df_display_def,
                    gridOptions=gridOptions,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                    )    
                        else:
                            st.button(lab_def,on_click = master_but)
                    except:
                        pass
                    try:
                        st.write(f'Attackers Search String:')
                        st.code(make_search_string(attackers, "master", st.session_state.top_num, fam_box, False, inv_box,show_xl_boxz))
                        lab_att = "Show Attackers Table"
                        if st.session_state['ultra_clicked']:
                            lab_att = "Hide Attackers Table"
                            st.button(lab_att,on_click = ultra_but)
                            family_data_att = format_data_top(attackers, 'Master', st.session_state.top_num,show_xl_boxz)
                            df_display_att = pd.DataFrame(family_data_att)
                            df_display_att.set_index(['Pokemon'], inplace=True)

                            gb = GridOptionsBuilder.from_dataframe(df_display_att)
                            other_options = {'suppressColumnVirtualisation': True}
                            gb.configure_grid_options(**other_options)
                            gridOptions = gb.build()
                
                            grid = AgGrid(
                    df_display_att,
                    gridOptions=gridOptions,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                    )
                        else:
                            st.button(lab_att,on_click = ultra_but)
                    except:
                        pass
                elif st.session_state['show_custom'] or st.session_state['show_custom2']: 
                    try:
                        #popover.button("Show Sunshine Cup Table", key='sun_table', on_click=great_but)
                        days_since_date = calculate_days_since(season_start)
                        age_string = f"age0-{days_since_date}&"
                        st.write(f'Custom Cup Top {st.session_state.top_num} Search String:')
                        st.code(make_search_string(df, "master", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz))
                        lab_mast = "Show Custom Table"
                        if st.session_state['master_clicked']:
                            lab_mast  = "Hide Master Table"
                            family_data_master = format_data_top(df, 'Master', st.session_state.top_num,True)
                            df_display_master = pd.DataFrame(family_data_master)
                            df_display_master.set_index(['Pokemon'], inplace=True)
                            st.button(lab_mast, on_click = master_but)

                            gb = GridOptionsBuilder.from_dataframe(df_display_master)
                            other_options = {'suppressColumnVirtualisation': True}
                            gb.configure_grid_options(**other_options)
                            gridOptions = gb.build()
                
                            grid = AgGrid(
                    df_display_master,
                    gridOptions=gridOptions,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                    )
                        else:
                            st.button(lab_mast,on_click = master_but)
                        
                    except:
                        pass
                elif st.session_state['show_custom1']: 


                    lab_gre = "Show Mega Master Cup Table"
                    st.write(f'Mega Master Cup Top {st.session_state.top_num} Search String:')
                    st.code(make_search_string(df, "great", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz,False))
                    lab_gre = "Show Mega Master Cup Table"
                    if st.session_state['great_clicked']:
                        lab_gre  = "Hide Mega Master Cup Table"
                        st.button(lab_gre,on_click = great_but)
                        family_data_Great = format_data_top(df, 'Great', st.session_state.top_num,show_xl_boxz)
                        df_display_Great = pd.DataFrame(family_data_Great)
                        df_display_Great.set_index(['Pokemon'], inplace=True)
                        
                        gb = GridOptionsBuilder.from_dataframe(df_display_Great)
                        other_options = {'suppressColumnVirtualisation': True}
                        gb.configure_grid_options(**other_options)
                        gridOptions = gb.build()
                
                        grid = AgGrid(
                    df_display_Great,
                    gridOptions=gridOptions,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                    )
                    else:
                        st.button(lab_gre,on_click = great_but)

                
                try:
                    load_from_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
                    streamlit_analytics2.start_tracking()
                    if st.session_state['show_custom1']:
                        copy_val = f'*Click string to show Copy button and Paste Top {topstrin} Mega Master Cup into PokeGO*'
                    elif st.session_state['show_custom2']:
                        copy_val = f'*Click string to show Copy button and Paste Top {topstrin} Mega Master Cup into PokeGO*'
                    else:
                        copy_val = f'*Click string to show Copy button and Paste Top {topstrin} into PokeGO*'
                    st.text_input(
                        label=today.strftime("%m/%d/%y"),
                        value= copy_val,
                        label_visibility='hidden',
                        disabled=True,
                        key="sstring"
                    )
                    st.divider()
                    with st.form('chat_input_form',clear_on_submit =True):
        # Create two columns; adjust the ratio to your liking
                        col3, col4 = st.columns([3,1]) 

        # Use the first column for text input
                        with col3:
                            prompt = st.text_input(placeholder = "Feedback", label="Feedback", key="fstring", label_visibility='collapsed')
                    # Use the second column for the submit button
                        with col4:
                            submitted = st.form_submit_button('Submit')

                        if prompt and submitted:
                    # Do something with the inputted text here
                            st.write(f"Submitted: {prompt}")
                    #st.text_input()
                    save_to_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
                    streamlit_analytics2.stop_tracking(unsafe_password=st.secrets['pass'])
            
                    load_from_firestore(streamlit_analytics2.data, st.secrets["fb_col"])
                    streamlit_analytics2.start_tracking()
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
                    streamlit_analytics2.stop_tracking(unsafe_password=st.secrets['pass'])
            
                # Get the last updated date

                except:
                    pass
        last_updated = get_last_updated_date(GITHUB_API_URL)
        st.write(f"Last updated: {last_updated} (EST)")
    # Custom CSS for mobile view and table fit
    st.markdown("""
    <style>
    button {
        height: 50px;
        width: 200px;
        color: blue;
    }
    """, unsafe_allow_html=True)


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
    .my-header-class .ag-header-cell-label {
        justify-content: center !important;
        font-size: 32px !important;
    }
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
