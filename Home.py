import pandas as pd
import streamlit as st
import glob


conn = st.connection('mysql', type='sql')

if 'conn' not in st.session_state:
    st.session_state.conn = conn

if 'rest_disp_counter' not in st.session_state:
    st.session_state.rest_disp_counter = 6

if 'rest_df_load_counter' not in st.session_state:
    st.session_state.rest_df_load_counter = 30

if st.session_state['rest_disp_counter'] > st.session_state['rest_df_load_counter']:
        st.session_state.rest_df_load_counter += 30

st.title("Restaurants serving now!!")

restaurants_count = st.session_state.rest_df_load_counter


def load_data():
    restaurants = conn.query('''
                             SELECT *
                             FROM restaurants NATURAL JOIN restaurant_services NATURAL JOIN 
                                  (SELECT placeID, COUNT(rating) rating_cnt, ROUND(AVG(rating), 1) rating, ROUND(AVG(food_rating), 1) food_rating, ROUND(AVG(service_rating), 1) service_rating
                                   FROM ratings
                                   GROUP BY placeID) rest_ratings;
                             ''', ttl=0)
    
    restaurants['name'] = restaurants['name'].apply(lambda x: x.replace('_', ' '))

    return restaurants


def img_dir_button(rest_sess_img_var, rest_img_ind, img_cnt, dir):
    if dir == 'prev':
        rest_img_ind = rest_img_ind - 1 if rest_img_ind > 0 else img_cnt - 1
    
    elif dir == 'next':
        rest_img_ind = rest_img_ind + 1 if rest_img_ind < img_cnt - 1 else 0
    
    st.session_state[rest_sess_img_var] = rest_img_ind


def load_more_click_button():
    st.session_state.rest_disp_counter += 6


def display_restaurants(cols, restaurants_df):
    rest_disp = []
    price = {'low': '$', 'medium': '$$', 'high': '$$$'}

    for _ in range(st.session_state.rest_disp_counter // cols):
        rest_disp.extend(st.columns(cols))

    for ind, rest_cont in enumerate(rest_disp):
        with rest_cont:
            rest_id = str(restaurants_df['placeID'][ind])
            rest_name = restaurants_df['name'][ind].title()

            st.markdown('##### ' + rest_name)
            
            img_dir = './images/restaurants/' + rest_id
            images = glob.glob(img_dir + '/*')
            img_cnt = len(images)

            rest_sess_img_var = 'img_' + rest_id
            if rest_sess_img_var not in st.session_state:
                st.session_state[rest_sess_img_var] = 0
            
            rest_img_ind = st.session_state[rest_sess_img_var]
            st.image(images[rest_img_ind])
            
            prev, next = st.columns(2)
            prev_btn_key = 'prev_' + rest_sess_img_var
            next_btn_key = 'next_' + rest_sess_img_var
            prev.button(label='<', key=prev_btn_key, on_click=img_dir_button, args=[rest_sess_img_var, rest_img_ind, img_cnt, 'prev'], use_container_width=True)
            next.button(label='\>', key=next_btn_key, on_click=img_dir_button, args=[rest_sess_img_var, rest_img_ind, img_cnt, 'next'], use_container_width=True)

            st.markdown(f'{restaurants_df["rating"][ind]} :star: ({restaurants_df["rating_cnt"][ind]} ratings) | {price[restaurants_df["price"][ind]]}')

            if st.button(label='Explore more', key='explore_' + rest_id, args=[rest_id], use_container_width=True):
                if 'rest_details_id' not in st.session_state:
                    st.session_state.rest_details_id = rest_id
                
                if 'rest_details' not in st.session_state:
                    st.session_state.rest_details = restaurants_df.iloc[ind, :]
            
                st.session_state.rest_details_id = rest_id
                st.session_state.rest_details = restaurants_df.iloc[ind, :]
                st.session_state.previous_page = 'Home.py'
                st.switch_page('pages/Last_Viewed_Restaurant.py')

data = load_data()

cols = 3
display_restaurants(cols, data)

st.button('Load More', on_click=load_more_click_button)
