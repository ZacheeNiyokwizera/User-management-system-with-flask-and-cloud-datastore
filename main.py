import secrets

from flask import Flask, request, render_template, redirect, url_for, session
from google.cloud import datastore
from passlib.hash import pbkdf2_sha256

from config import get_datastore_emulator_host, get_google_cloud_project

DATASTORE_EMULATOR_HOST=get_datastore_emulator_host( )
GOOGLE_CLOUD_PROJECT=get_google_cloud_project( )

datastore_client=datastore.Client( )

app=Flask(__name__)
secret_key=secrets.token_hex(16)
app.secret_key=secret_key


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))  #


def create_user(username, email, password):
    key=datastore_client.key('User')
    user=datastore.Entity(key)
    user.update({
        'username':username,
        'email':email,
        'password':pbkdf2_sha256.hash(password)
    })
    datastore_client.put(user)


def query_all_users():
    query=datastore_client.query(kind='User')
    results=list(query.fetch( ))
    return results


@app.route('/users', methods=['GET'])
def users():
    users=query_all_users( )
    for user in users:
        print(f"User ID: {user.key.id}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print("------")
    return render_template('users.html', users=users)


def query_user_by_email(email):
    query=datastore_client.query(kind='User')
    query.add_filter('email', '=', email)
    results=list(query.fetch( ))
    print('From line 60', results)

    if results:
        return results[0]
    else:
        return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')

        existing_user=query_user_by_email(email)
        print(f"Checking if user with email {email} exists.")

        if existing_user:
            print(f"User with email {email} exists.")
            return "Email already in use. Please choose another email."

        # Create and store the user entity in Datastore
        create_user(username, email, password)

        # Log in the user
        session['username']=username

        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user=query_user_by_email(email)
        if user and pbkdf2_sha256.verify(password, user['password']):
            # User exists and the password is correct
            # Create a session to track the user's login status
            session['user_id']=user.key.id
            session['username']=user['username']
            return redirect(url_for('dashboard'))
        else:
            # Invalid login credentials
            error="Invalid email or password"
            print(error)
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username=session['username']
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('login'))


if __name__=='__main__':
    app.run( )
