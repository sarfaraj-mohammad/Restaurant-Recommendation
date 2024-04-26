import pandas as pd
import streamlit as st
import glob
import time

if 'conn' not in st.session_state:
    conn = st.connection('mysql', type='sql')
else:
    conn = st.session_state.conn

if 'rest_details' not in st.session_state:
    st.info('You haven\'t visited any restaurants in the current session!')
    st.info('Redirecting to Home Page...')
    time.sleep(3)
    st.session_state.previous_page = 'Last_Viewed_Restaurant'
    st.switch_page('./Home.py')
else:
    curr_rest = st.session_state.rest_details


def load_data():
    restaurants = conn.query(f'''
                             SELECT *
                             FROM ratings NATURAL JOIN users
                             WHERE placeID = {curr_rest['placeID']}
                             ORDER BY ratingID DESC;
                             ''', ttl=0)

    return restaurants


def img_dir_button(rest_sess_img_var, rest_img_ind, img_cnt, dir):
    if dir == 'prev':
        rest_img_ind = rest_img_ind - 1 if rest_img_ind > 0 else img_cnt - 1
    
    elif dir == 'next':
        rest_img_ind = rest_img_ind + 1 if rest_img_ind < img_cnt - 1 else 0
    
    st.session_state[rest_sess_img_var] = rest_img_ind


def display_details(rest_df):
    price = {'low': '$', 'medium': '$$', 'high': '$$$'}
    alcohol = {'No_Alcohol_Served': ':red[No Alcohol Served]', 'Wine-Beer': ':wine: Wine and :beers: Beers only', 'Full_Bar': ':champagne: Full Bar'}
    smoking = {'permitted': ':smoking: :green[Smoking Permitted]', 'not permitted': ':no_smoking: :red[Smoking Prohibited]', 'none': ':no_smoking: :red[Smoking Prohibited]',
               'section': ':smoking: :green[Smoking Section Available]', 'only at bar': ':smoking: :green[Smoking Permitted Only at Bar]'}
    franchise = {'f': 'Independent', 't': 'Franchise'}

    curr_rest['dress_code'] = curr_rest['dress_code'].title()

    with st.container():
        rest_id = str(curr_rest['placeID'])
        rest_name = curr_rest['name'].title()
        rest_addr = f'{curr_rest["address"].title()}, {curr_rest["city"].title()}, {curr_rest["state"].title()}, {curr_rest["country"].title()}'
        
        img_dir = './images/restaurants/' + rest_id
        images = glob.glob(img_dir + '/*')
        img_cnt = len(images)

        rest_sess_img_var = 'img_' + rest_id
        if rest_sess_img_var not in st.session_state:
            st.session_state[rest_sess_img_var] = 0
        
        rest_img_ind = st.session_state[rest_sess_img_var]
        st.image(images[rest_img_ind], use_column_width=True)
        
        prev, next = st.columns(2)
        prev_btn_key = 'prev_' + rest_sess_img_var
        next_btn_key = 'next_' + rest_sess_img_var
        prev.button(label='<', key=prev_btn_key, on_click=img_dir_button, args=[rest_sess_img_var, rest_img_ind, img_cnt, 'prev'], use_container_width=True)
        next.button(label='\>', key=next_btn_key, on_click=img_dir_button, args=[rest_sess_img_var, rest_img_ind, img_cnt, 'next'], use_container_width=True)

        st.markdown('## ' + rest_name, unsafe_allow_html=True)
        st.markdown(f'### {curr_rest["rating"]} :star: ({curr_rest["rating_cnt"]} ratings) | {franchise[curr_rest["franchise"]]} | {price[curr_rest["price"]]}')

        st.markdown(f'#### Cuisines : {curr_rest["cuisines"]}')
        st.markdown(f'#### {alcohol[curr_rest["alcohol"]]} | {smoking[curr_rest["smoking_area"]]} | {curr_rest["area"].title()} Kitchen')
        st.markdown(f'##### Dress Code: {curr_rest["dress_code"].title()}')
        st.markdown(f'##### Ambience: {curr_rest["Rambience"].title()}')
        st.markdown(f'##### Address: {rest_addr}')

        cont1, cont2 = st.columns(2)
        cont1.button(label='Reserve Table :knife_fork_plate:', use_container_width=True)

        if cont2.button(label='Leave Review :spiral_note_pad:', key='review_' + rest_id, args=[rest_id], use_container_width=True):
            if 'rest_details_id' not in st.session_state:
                st.session_state.rest_details_id = rest_id
            
            st.session_state.previous_page = __file__
            st.session_state.rest_details_id = rest_id
            st.session_state.previous_page = 'pages/Last_Viewed_Restaurant.py'
            st.switch_page('./pages/Review.py')

        st.markdown('')

        st.markdown('### Reviews')
        for i in range(len(rest_df)):
            with st.container(border=True):
                st.markdown(f'#### {rest_df["first_name"][i]} {rest_df["last_name"][i]} {rest_df["userID"][i]}')
                rating_cont, comment_cont = st.columns([0.3, 0.7])
                rating_cont.markdown(f'###### Overall Rating: {rest_df["rating"][i]} :star:')
                rating_cont.markdown(f'###### Food Rating: {rest_df["food_rating"][i]} :star:')
                rating_cont.markdown(f'###### Service Rating: {rest_df["service_rating"][i]} :star:')
                comment_cont.write(f'{rest_df["comments"][i]}')



data = load_data()

display_details(data)