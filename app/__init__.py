from flask import Flask, render_template, session, redirect, make_response, request
from flask_session import Session

from google.auth.transport.requests import Request

app = Flask(__name__)
app.config.from_pyfile('configs.py')
Session(app)

print("Server listening on http://localhost:5000")

from app.api.link.router import link
from app.api.user.router import user
from app.api.admin.router import admin
app.register_blueprint(link, url_prefix="/api/v1/link")
app.register_blueprint(user, url_prefix="/api/v1/user")
app.register_blueprint(admin, url_prefix="/api/v1/admin")

from app.api.link.controller import *
from app.api.user.controller import *
from app.api.admin.controller import *
from .oauth import verify_token

@app.before_request
def check_user():
    if request.path.startswith('/static') or request.path.startswith('/favicon'):
        return
    print(request.method + ' ' + request.path)

    if request.path.startswith('/admin') and session.get('user', { 'user_type' : 'open' })['user_type'] != 'admin':
        print("papalayasin")
        return redirect('/')

    if session.get('user'):
        users = list_users('email', session['user']['email'])
        if len(users) == 1:
            user = users[0]
            session['user'] = { **user, 'name': user.get('given_name') + ' ' + user.get('family_name')}
        else:
            session['user'] = { 'user_type' : 'open' }
    
    return


# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('error/404.html', categories_links = {}), 404


# pages routes
@app.route('/', methods=['GET'])
def index_page():
    categories = list_categories(session.get('user', {'user_type': 'open'})['user_type'])
    categories_links = {}
    for category in categories:
        category_links = links_by_category(category, session.get('user', {'user_type': 'open'})['user_type'])

        if len(category_links) > 0:
            categories_links[category['name']] = category_links

    res = make_response(render_template('index.html',categories_links = categories_links,user=session.get('user', None), category_list = list_all_categories(), privacy_settings = list_user_types()))
    res.headers.set('Referrer-Policy', 'no-referrer-when-downgrade')
    res.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')
    return res



# admin routes
@app.route('/admin', methods=['GET'])
def user_management_page():
    userlist = list_user_data()
    res = make_response(render_template('users.html', categories_links={}, users = userlist, user=session.get('user', None)))

    res.headers.set('Referrer-Policy', 'no-referrer-when-downgrade')
    res.headers.set('Cross-Origin-Opener-Policy', 'same-origin-allow-popups')
    return res



# auth routes
@app.route('/callback', methods=['POST', 'GET'])
def callback():
    credential = request.form.get('credential')
    user_google_data = verify_token(credential)
    if user_google_data:
        if len(list_users('email', user_google_data['email'])) == 1:
            user_google_data = { **user_google_data, 'user_type' : get_user_value(user_google_data['email'], 'user_type')}
        user = upsert_user(user_google_data)
        session['user'] = { **user, "name" : user.get('given_name') + " " + user.get('family_name', '') }

    return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')
