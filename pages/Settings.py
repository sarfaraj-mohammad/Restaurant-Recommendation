import pandas as pd
import streamlit as st
import glob
import os
import time
import datetime
from sqlalchemy.sql import text
from pages.Sign_In import validate_required_fields

if 'conn' not in st.session_state:
    conn = st.connection('mysql', type='sql')
else:
    conn = st.session_state.conn

if 'userid' not in st.session_state:
    st.info('Please Log In to your account first! Redirecting to Sign-In Page...')
    st.session_state.previous_page = 'pages/Settings.py'
    time.sleep(3)
    st.switch_page('./pages/Sign_In.py')
else:
    curr_user_id = st.session_state.userid

if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False


settings_result_container = st.empty()


def fetch_user_data():
    fetch_user_data_sql = f'''
        SELECT *
        FROM users u LEFT JOIN user_preferences up USING (userID)
        WHERE u.userID = {curr_user_id};
    '''

    user_details = conn.query(fetch_user_data_sql, ttl=0)
    user_details = user_details.applymap(lambda x: '' if x is None else x)
    user_details = user_details.to_dict('records')[0]

    display_user_data(user_details)


def set_edit_mode():
    st.session_state.edit_mode = not st.session_state.edit_mode


def delete_account(user_id):
    delete_sql = f'DELETE FROM users WHERE userID = {user_id};'
    with conn.session as session:
        try:
            result = session.execute(text(delete_sql))
            settings_result_container.success('Your account has been deleted successfully! Redirecting to Sign In page...')
            session.commit()
            time.sleep(2)
            del st.session_state.userid

        except Exception as e:
            settings_result_container.error('Sorry, something went wrong. Please try again.')


def confirm_delete_account(user_id):
    with confirm_delete_cont.container():
        st.markdown('### Are you sure you want to delete your account permanently?')
        yes_cont, no_cont = st.columns(2)
        yes = yes_cont.button('Yes', on_click=delete_account, args=[user_id])
        no = no_cont.button('No', type='primary')

        st.stop()


def display_user_data(user_df):
    st.title(f'Hi, {user_df["first_name"]} {user_df["last_name"]}!')

    if st.session_state.edit_mode == False:
        st.button('Edit/Delete Profile', on_click=set_edit_mode)
    else:
        delete_cont, cancel_cont = st.columns(2)
        deleted = delete_cont.button('Delete Account', type='primary', on_click=confirm_delete_account, args=[user_df['userID']])
        cancelled = cancel_cont.button('Cancel Editing', on_click=set_edit_mode)
        global confirm_delete_cont
        confirm_delete_cont = st.empty()


    with st.form('user_details'):
        editing_disabled = not st.session_state.edit_mode

        fn_cont, ln_cont = st.columns(2)
        first_name_text_val = fn_cont.text_input('First Name', value=user_df['first_name'], disabled=editing_disabled)
        last_name_text_val = ln_cont.text_input('Last Name', value=user_df['last_name'], disabled=editing_disabled)

        phone_cont, email_cont = st.columns(2)
        phone_number_val = phone_cont.text_input('Contact Number', value=user_df['phone_number'], disabled=editing_disabled)
        email_text_val = email_cont.text_input('Email', value=user_df['email'], disabled=True)

        marital_cont, birth_year_cont = st.columns(2)
        marital_status_text_val = marital_cont.text_input('Marital Status', value=user_df['marital_status'], disabled=editing_disabled)
        birth_year_val = birth_year_cont.selectbox('Birth Year', range(datetime.date.today().year, 1990, -1), 
                                                   index=range(datetime.date.today().year, 1990, -1).index(user_df['birth_year']), disabled=editing_disabled)

        hijos_cont, pers_cont = st.columns(2)
        hijos_text_val = hijos_cont.text_input('Hijos', value=user_df['hijos'], disabled=editing_disabled)
        personality_text_val = pers_cont.text_input('Personality', value=user_df['personality'], disabled=editing_disabled)

        rel_cont, col_cont = st.columns(2)
        religion_text_val = rel_cont.text_input('Religion', value=user_df['religion'], disabled=editing_disabled)
        color_text_val = col_cont.text_input('Favorite Color', value=user_df['color'], disabled=editing_disabled)

        weight_cont, height_cont = st.columns(2)
        weight_text_val = weight_cont.text_input('Weight', value=user_df['weight'], disabled=editing_disabled)
        height_text_val = height_cont.text_input('Height', value=user_df['height'], disabled=editing_disabled)

        smoker_cont, drink_level_cont = st.columns(2)
        smoker_text_val = smoker_cont.text_input('Smoker', value=user_df['smoker'], disabled=editing_disabled)
        drink_level_text_val = drink_level_cont.text_input('Drink Level', value=user_df['drink_level'], disabled=editing_disabled)

        dress_cont, ambience_cont = st.columns(2)
        dress_text_val = dress_cont.text_input('Dress Code Preferred', value=user_df['dress_preference'], disabled=editing_disabled)
        ambience_text_val = ambience_cont.text_input('Ambience Preferred', value=user_df['ambience'], disabled=editing_disabled)

        activity_cont, transport_cont = st.columns(2)
        activity_text_val = activity_cont.text_input('Activity(s)', value=user_df['activity'], disabled=editing_disabled)
        transport_text_val = transport_cont.text_input('Transport', value=user_df['transport'], disabled=editing_disabled)

        interest_cont, budget_cont = st.columns(2)
        interest_text_val = interest_cont.text_input('Interest', value=user_df['interest'], disabled=editing_disabled)
        budget_text_val = budget_cont.text_input('Budget', value=user_df['budget'], disabled=editing_disabled)

        saved = st.form_submit_button('Save Changes', on_click=set_edit_mode, disabled=editing_disabled)

        if saved:
            required_fields = [first_name_text_val, last_name_text_val, phone_number_val, email_text_val, marital_status_text_val, birth_year_val]
            required_fields_labels = ['First Name', 'Last Name', 'Contact Number', 'Email', 'Marital Status', 'Birth Year']
            
            if validate_required_fields(required_fields, required_fields_labels):
                update_users_sql = f'''
                    UPDATE users
                    SET first_name = "{first_name_text_val}", last_name = "{last_name_text_val}", phone_number = "{phone_number_val}", marital_status = "{marital_status_text_val}", 
                        hijos = "{hijos_text_val}", birth_year = {birth_year_val}, personality = "{personality_text_val}", religion = "{religion_text_val}", 
                        color = "{color_text_val}", weight = {weight_text_val}, height = {height_text_val}
                    WHERE userID = {user_df["userID"]};
                '''.replace('= ""', '= NULL').replace('= ,', '= NULL,').replace('= \n', '= NULL')

                update_user_preferences_sql = f'''
                    REPLACE INTO user_preferences
                    VALUES ({curr_user_id}, "{smoker_text_val}", "{drink_level_text_val}", "{dress_text_val}", "{ambience_text_val}", 
                            "{activity_text_val}", "{transport_text_val}", "{interest_text_val}", "{budget_text_val}");
                '''.replace(', ""', ', NULL').replace('"",', 'NULL,')

                rating_result_cont_message = 'Your review has been submitted successfully! Redirecting to the Last Viewed Restaurant page...'

                with conn.session as session:
                    try:
                        result = session.execute(text(update_users_sql))
                        result = session.execute(text(update_user_preferences_sql))
                        settings_result_container.success('Your information has been updated successfully!')
                        session.commit()

                    except Exception as e:
                        settings_result_container.error('Sorry, something went wrong. Please try again.')

            
fetch_user_data()



