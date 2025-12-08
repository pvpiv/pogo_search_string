# session_state_manager.py

import streamlit as st
import streamlit_analytics2
import pandas as pd
import random
import string

# Get available languages from translation file
TRANSLATIONS_DF = pd.read_csv('translation.csv')
AVAILABLE_LANGUAGES = [col for col in TRANSLATIONS_DF.columns if col not in ['KEY VALUE']]

def generate_unique_key(base_key):
    """Generate a unique key by appending a random string"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{base_key}_{random_suffix}"

def initialize_session_state():
    # Get language from query params if available
    query_params = st.query_params
    default_language = query_params.get('lang', 'English')
    if default_language not in AVAILABLE_LANGUAGES:
        default_language = 'English'
        
    if 'language' not in st.session_state:
        st.session_state['language'] = default_language
    if 'get_dat' not in st.session_state:
        st.session_state['get_dat'] = False
    if 'get_shadow' not in st.session_state:
        st.session_state['get_shadow'] = True
    if 'show_shadow' not in st.session_state:
        st.session_state['show_shadow'] = False
    if 'show_xl' not in st.session_state:
        st.session_state['show_xl'] = True
    if 'get_season' not in st.session_state:
        st.session_state['get_season'] = False
    if 'last_sel' not in st.session_state:
        st.session_state['last_sel'] = None
    if 'last_n' not in st.session_state:
        st.session_state['last_n'] = 0
    if 'comm' not in st.session_state:
        st.session_state['comm'] = False
    if 'top_num' not in st.session_state:
        st.session_state['top_num'] = 50
        try:
            if st.query_params["comm"] == "true":
                st.session_state['comm'] = "true"
                st.session_state['top_num'] = 2000
        except:
            pass
    if 'show_string' not in st.session_state:
        st.session_state['show_string'] = True
    if 'show_custom' not in st.session_state:
        st.session_state['show_custom'] = False
    if 'show_custom1' not in st.session_state:
        st.session_state['show_custom1'] = False
    if 'show_custom2' not in st.session_state:
        st.session_state['show_custom2'] = False
    if 'show_custom3' not in st.session_state:
        st.session_state['show_custom3'] = False
    if 'show_inverse' not in st.session_state:
        st.session_state['show_inverse'] = False
    if 'little_clicked' not in st.session_state:
        st.session_state['little_clicked'] = False
    if 'great_clicked' not in st.session_state:
        st.session_state['great_clicked'] = False
    if 'ultra_clicked' not in st.session_state:
        st.session_state['ultra_clicked'] = False
    if 'master_clicked' not in st.session_state:
        st.session_state['master_clicked'] = False
    if 'table_gen' not in st.session_state:
        st.session_state['table_gen'] = ''
    if 'table_string_butt' not in st.session_state:
        st.session_state['table_string_butt'] = True
    if 'gym_bool' not in st.session_state:
        st.session_state['gym_bool'] = False
    if "state_dict" not in st.session_state:
        st.session_state.state_dict = {}
    # Store used keys to avoid duplicates
    if "used_keys" not in st.session_state:
        st.session_state.used_keys = set()

def update_language():
    """Update the language in session state and URL"""
    # Check which key was used to trigger the update
    if 'sidebar_lang_choice_box' in st.session_state:
        new_lang = st.session_state.sidebar_lang_choice_box
    else:
        return  # No language selection was made
        
    st.session_state['language'] = new_lang
    # Update URL query parameter
    current_params = st.query_params
    current_params['lang'] = new_lang
    st.query_params = current_params

def update_top_num():
    st.session_state.top_num = st.session_state.top_no

def upd_tab_str():
    st.session_state['table_string_butt'] = not st.session_state['table_string_butt']
    
def upd_shadow():
    st.session_state.get_shadow = st.session_state.sho_shad

def upd_xl():
    st.session_state.show_xl = st.session_state.sho_xl

def upd_seas():
    st.session_state.get_season = st.session_state.sho_seas

def upd_shad_only():
    st.session_state.show_shadow = st.session_state.sho_shad

def upd_cust():
    st.session_state.show_custom = st.session_state.sho_cust

def upd_cust1():
    st.session_state.show_custom1 = st.session_state.sho_cust1

def upd_cust2():
    st.session_state.show_custom2 = st.session_state.sho_cust2

def upd_cust3():
    st.session_state.show_custom3 = st.session_state.sho_cust3

def update_gym_bool():
    st.session_state['gym_bool'] = st.session_state['sho_gym']

def upd_inv():
    st.session_state.show_inverse = st.session_state.sho_inv

def bool_switcher(y):
    y = not (y)

def little_but():
    st.session_state['little_clicked'] = not st.session_state['little_clicked']

def great_but():
    st.session_state['great_clicked'] = not st.session_state['great_clicked']

def ultra_but():
    st.session_state['ultra_clicked'] = not st.session_state['ultra_clicked']

def master_but():
    st.session_state['master_clicked'] = not st.session_state['master_clicked']
