# session_state_manager.py

import streamlit as st


def initialize_session_state():
    if 'get_dat' not in st.session_state:
        st.session_state['get_dat'] = False
    if 'get_shadow' not in st.session_state:
        st.session_state['get_shadow'] = True
    if 'session_data' not in st.session_state:
        st.session_state['session_data'] = True
    if 'show_xl' not in st.session_state:
        st.session_state['show_xl'] = True
    if 'get_season' not in st.session_state:
        st.session_state['get_season'] = True
    if 'last_sel' not in st.session_state:
        st.session_state['last_sel'] = None
    if 'last_n' not in st.session_state:
        st.session_state['last_n'] = 0
    if 'top_num' not in st.session_state:
        st.session_state['top_num'] = 50
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

def upd_cust():
    st.session_state.show_custom = st.session_state.sho_cust
def upd_cust1():
    st.session_state.show_custom1 = st.session_state.sho_cust1
def upd_cust2():
    st.session_state.show_custom2 = st.session_state.sho_cust2
def upd_cust3():
    st.session_state.show_custom2 = st.session_state.sho_cust3
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
