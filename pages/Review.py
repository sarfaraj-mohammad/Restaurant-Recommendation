import pandas as pd
import streamlit as st
import glob
import time
from sqlalchemy.sql import text

if 'conn' not in st.session_state:
    conn = st.connection('aws_rds', type='sql')
else:
    conn = st.session_state.conn

if 'rest_details' not in st.session_state:
    st.error('Please choose the restaurant first!')
    st.info('Redirecting to Home Page...')
    st.session_state.previous_page = 'pages/Review.py'
    time.sleep(3)
    st.switch_page('./Home.py')
else:
    curr_rest = st.session_state.rest_details

if 'userid' not in st.session_state:
    st.info('Please Sign In to your account to share your feedback')
    st.info('Redirecting to Sign-In Page...')
    st.session_state.previous_page = 'pages/Review.py'
    time.sleep(3)
    st.switch_page('./pages/Sign_In.py')
else:
    curr_user_id = st.session_state.userid

st.title("Let us know your experience with this restaurant")

def load_data():
    ratings = conn.query(f'''
                             SELECT *
                             FROM ratings NATURAL JOIN users
                             WHERE placeID = {curr_rest['placeID']}
                                   AND userID = {curr_user_id}
                             ''', ttl=0)

    return ratings


def img_dir_button(rest_sess_img_var, rest_img_ind, img_cnt, dir):
    if dir == 'prev':
        rest_img_ind = rest_img_ind - 1 if rest_img_ind > 0 else img_cnt - 1
    
    elif dir == 'next':
        rest_img_ind = rest_img_ind + 1 if rest_img_ind < img_cnt - 1 else 0
    
    st.session_state[rest_sess_img_var] = rest_img_ind


def review_restaurant(rating_df):
    price = {'low': '$', 'medium': '$$', 'high': '$$$'}
    franchise = {'f': 'Independent', 't': 'Franchise'}

    rest_id = str(curr_rest['placeID'])
    rest_name = curr_rest['name'].title()
    
    img_dir = './images/restaurants/' + rest_id
    images = glob.glob(img_dir + '/*')
    img_cnt = len(images)

    rest_sess_img_var = 'img_' + rest_id
    if rest_sess_img_var not in st.session_state:
        st.session_state[rest_sess_img_var] = 0
    
    rest_img_ind = st.session_state[rest_sess_img_var]
    if img_cnt:
        st.image(images[rest_img_ind], use_column_width=True)
    else:
        st.caption('This restaurant hasn\'t uploaded any images.')
    
    prev, next = st.columns(2)
    prev_btn_key = 'prev_' + rest_sess_img_var
    next_btn_key = 'next_' + rest_sess_img_var
    prev.button(label='<', key=prev_btn_key, on_click=img_dir_button, args=[rest_sess_img_var, rest_img_ind, img_cnt, 'prev'], use_container_width=True)
    next.button(label='\>', key=next_btn_key, on_click=img_dir_button, args=[rest_sess_img_var, rest_img_ind, img_cnt, 'next'], use_container_width=True)

    st.markdown('## ' + rest_name)
    st.markdown(f'### {curr_rest["rating"]} :star: ({curr_rest["rating_cnt"]} ratings) | {franchise[curr_rest["franchise"]]} | {price[curr_rest["price"]]}')

    st.markdown('')

    previous_rating =  1 if rating_df.empty else rating_df['rating'][0]
    previous_food_rating =  1 if rating_df.empty else rating_df['food_rating'][0]
    previous_service_rating =  1 if rating_df.empty else rating_df['service_rating'][0]
    previous_comment =  None if rating_df.empty else rating_df['comments'][0]

    rating_result_cont = st.empty()

    if not rating_df.empty:
        rating_result_cont.info('You have already submitted a review for this restaurant! Please go ahead if you\'d like to update it.')

    with st.form('review_form'):
        rating_slider_val = st.slider('#### Rate your overall experience with this restaurant:', 1, 5, previous_rating)
        food_rating_slider_val = st.slider('#### On a scale of 1-10, how much did you enjoy the food:', 1, 5, previous_food_rating)
        service_rating_slider_val = st.slider('#### On a scale of 1-10, how much would you rate the service:', 1, 5, previous_service_rating)
        comment_text_val = st.text_area('#### Is there anything else you\'d like to share ?', value=previous_comment, placeholder='Start typing...')

        submit_cont, cancel_cont = st.columns(2)
        submitted = submit_cont.form_submit_button('Submit', use_container_width=True)
        cancelled = cancel_cont.form_submit_button('Cancel', type='primary', use_container_width=True)

        if submitted:
            if rating_df.empty:
                rating_sql = f'''
                    INSERT INTO ratings
                    VALUES (NULL, {curr_user_id}, {rest_id}, {rating_slider_val}, {food_rating_slider_val}, {service_rating_slider_val}, "{comment_text_val}");
                '''.replace(', ""', ', NULL').replace(', ,', ', NULL,').replace(', )', ', NULL)')
                rating_result_cont_message = 'Your review has been submitted successfully! Redirecting to the Last Viewed Restaurant page...'
            else:
                rating_sql = f'''
                    UPDATE ratings
                    SET rating = {rating_slider_val}, food_rating = {food_rating_slider_val}, service_rating = {service_rating_slider_val}, comments = "{comment_text_val}"
                    WHERE ratingID = {rating_df["ratingID"][0]};
                '''.replace(', ""', ', NULL').replace(', ,', ', NULL,').replace(', )', ', NULL)')
                rating_result_cont_message = 'Your review has been updated successfully! Redirecting to the Last Viewed Restaurant page...'

            with conn.session as session:
                try:
                    result = session.execute(text(rating_sql))
                    rating_result_cont.success(rating_result_cont_message)
                    session.commit()
                    redirect_page = 'pages/Last_Viewed_Restaurant.py'
                    st.session_state.previous_page = 'pages/Review.py'
                    time.sleep(2)
                    st.switch_page(redirect_page)

                except Exception as e:
                    rating_result_cont.error('Sorry, something went wrong. Please try again.')
        
        if cancelled:
            redirect_page = 'pages/Last_Viewed_Restaurant.py'
            st.session_state.previous_page = 'pages/Review.py'
            st.switch_page(redirect_page)


data = load_data()

review_restaurant(data)