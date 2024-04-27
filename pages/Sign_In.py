import pandas as pd
import streamlit as st
import os
import time
import datetime
from sqlalchemy.sql import text

if 'conn' not in st.session_state:
    conn = st.connection('aws_rds', type='sql')
else:
    conn = st.session_state.conn

logged_cont = st.empty()

if 'userid' in st.session_state:
    logged_cont.info('You are already logged in!')
    st.markdown('### Do you want to log out of your account ?')
    yes_cont, no_cont = st.columns(2)
    yes = yes_cont.button('Yes')
    no = no_cont.button('No', type='primary')

    if yes:
        del st.session_state.userid
        logged_cont.success('You have been successfully logged out of your account! Redirecting to Sign-In Page...')
        time.sleep(2)
        st.rerun()

    if no:
        logged_cont.info('Redirecting to Settings Page...')
        time.sleep(2)
        st.session_state.previous_page = 'pages/Sign_In.py'
        st.switch_page('pages/Settings.py')

    st.stop()


st.title('Hi, there!')
st.header('Welcome to our Restaurant Ratings App!')

login_tab, signup_tab = st.tabs(['Log In', 'Sign Up'])

login_result_container = login_tab.empty()

login_tab.subheader('Log in back to your account.')

signup_result_container = signup_tab.empty()
signup_tab.subheader('New user ? Sign up to get the most out of our App.')


def validate_email(email, password):
    validate_email_sql = f'''
        SELECT userID
        FROM users
        WHERE email = "{email}";
    '''

    valid_email = conn.query(validate_email_sql, ttl=0)

    if valid_email.empty:
        login_result_container.info('Sorry, we couldn\'t find an account with that email. Please double-check the email entered and try again.')
    
    else:
        validate_user_credentials(email, password)


def validate_user_credentials(email, password):
    validate_password_sql = f'''
        SELECT userID
        FROM users
        WHERE email = "{email}"
              AND password = SHA2("{password}", 256);
    '''

    valid_password = conn.query(validate_password_sql, ttl=0)

    if not valid_password.empty:
        st.session_state.userid = valid_password['userID'][0]
        login_result_container.success('Successfully logged in! Redirecting to previous page...')
        previous_page = st.session_state.previous_page if st.session_state.get('previous_page') else 'Home.py'
        redirect_page = (previous_page if os.path.basename(previous_page) != os.path.basename(__file__) else 'Home.py')
        st.session_state.previous_page = 'pages/Sign_In.py'
        time.sleep(2)
        st.switch_page(redirect_page)
    else:
        login_result_container.info('The password you entered is incorrect. Please try again.')


def validate_required_fields(fields, labels):
    all_fields_valid = True
    for field, label in zip(fields, labels):
        if not field:
            all_fields_valid = False
            st.info(f'The "{label}" field is required. Please enter a valid value and try again.')

    return all_fields_valid


def check_existing_user(new_user_email):
    check_existing_user_sql = f'''
        SELECT *
        FROM users
        WHERE email = "{new_user_email}";
    '''

    user_found = conn.query(check_existing_user_sql, ttl=0)

    return user_found.empty


with login_tab.form('login_form'):
    email_text_val = st.text_input('Email', placeholder='Required')
    password_text_val = st.text_input('Password', type='password', placeholder='Required')

    log_in = st.form_submit_button('Log In')

    if log_in:
        required_fields = [email_text_val, password_text_val]
        required_fields_labels = ['Email', 'Password']
        if validate_required_fields(required_fields, required_fields_labels):
            validate_email(email_text_val, password_text_val)

with signup_tab.form('sign_up_form'):
    fn_cont, ln_cont, phone_cont = st.columns(3)
    first_name_text_val = fn_cont.text_input('First Name', placeholder='Required')
    last_name_text_val = ln_cont.text_input('Last Name', placeholder='Required')
    phone_number_val = phone_cont.text_input('Contact Number', placeholder='Required')
    email_text_val = st.text_input('Email', placeholder='Required')
    password_text_val = st.text_input('Password', type='password', placeholder='Required')

    marital_cont, birth_year_cont = st.columns(2)
    marital_status_text_val = marital_cont.text_input('Marital Status', placeholder='Required')
    birth_year_val = birth_year_cont.selectbox('Birth Year', range(datetime.date.today().year, 1930, -1), index=None, placeholder='Required')

    hijos_cont, pers_cont = st.columns(2)
    hijos_text_val = hijos_cont.text_input('Hijos', placeholder='Optional')
    personality_text_val = pers_cont.text_input('Personality', placeholder='Optional')

    rel_cont, col_cont = st.columns(2)
    religion_text_val = rel_cont.text_input('Religion', placeholder='Optional')
    color_text_val = col_cont.text_input('Favorite Color', placeholder='Optional')

    weight_cont, height_cont = st.columns(2)
    weight_text_val = weight_cont.text_input('Weight', placeholder='Optional')
    height_text_val = height_cont.text_input('Height', placeholder='Optional')


    sign_up = st.form_submit_button('Sign Up')

    if sign_up:
        required_fields = [first_name_text_val, last_name_text_val, phone_number_val, email_text_val, password_text_val, marital_status_text_val, birth_year_val]
        required_fields_labels = ['First Name', 'Last Name', 'Contact Number', 'Email', 'Password', 'Marital Status', 'Birth Year']
        if validate_required_fields(required_fields, required_fields_labels):
            if not check_existing_user(email_text_val):
                signup_result_container.info('An account already exists with this Email ID! Please use the Log In tab to access your account.')
                st.stop()
            
            insert_new_user_sql = f'''
            INSERT INTO users
            VALUES (NULL, "{first_name_text_val}", "{last_name_text_val}", "{phone_number_val}", "{email_text_val}", SHA2("{password_text_val}", 256), 
                          "{marital_status_text_val}", "{hijos_text_val}", {birth_year_val}, "{personality_text_val}", 
                          "{religion_text_val}", "{color_text_val}", {weight_text_val}, {height_text_val});
            '''.replace(', ""', ', NULL').replace(', ,', ', NULL,').replace(', )', ', NULL)')

            with conn.session as session:
                try:
                    result = session.execute(text(insert_new_user_sql))
                    signup_result_container.success('Thank you for joining our platform! Redirecting to previous page...')
                    session.commit()
                    st.session_state.userid = result.lastrowid
                    redirect_page = st.session_state.previous_page if st.session_state.get('previous_page') else 'Home.py'
                    st.session_state.previous_page = 'pages/Sign_In.py'
                    time.sleep(2)
                    st.switch_page(redirect_page)

                except Exception as e:
                    signup_result_container.error('Sorry, something went wrong. Please double-check the field values entered and try again.')

            

