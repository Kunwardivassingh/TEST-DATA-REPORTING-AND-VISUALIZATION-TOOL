# utils/auth_middleware.py
from flask import session, redirect, url_for



def login_user(user_id):
    session['user_id'] = user_id
def logout_user():
    session.pop('user', None)

def is_logged_in():
    return 'user' in session

def get_current_user():
    return session.get('user')



