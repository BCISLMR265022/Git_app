from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import subprocess
import os
import re

app = Flask(__name__)
app.secret_key = 'xyzsdfg'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/user-system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)
    labels = db.Column(db.String(255))

class Commit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commit_hash = db.Column(db.String(40), nullable=False, unique=True)
    commit_message = db.Column(db.Text)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['loggedin'] = True
            session['userid'] = user.id
            session['name'] = user.name
            session['email'] = user.email
            message = 'Logged in successfully!'
            return render_template('index.html', message=message)
        else:
            message = 'Please enter correct email/password!'
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        user_name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not user_name or not password or not email:
            message = 'Please fill out the form!'
        else:
            new_user = User(name=user_name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            message = 'You have successfully registered!'
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    return render_template('register.html', message=message)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if request.method == 'POST':
        repo_url = request.form['repo_url']
        result = analyze_repository(repo_url)
        return render_template('result.html', result=result)

def analyze_repository(repo_url):
    try:
        subprocess.run(['git', 'clone', repo_url])
        repo_name = repo_url.split('/')[-1].split('.')[0]
        os.chdir(repo_name)

        commit_info = subprocess.check_output(['git', 'log', '--pretty=format:%H,%s']).decode('utf-8').strip().split('\n')

        for commit in commit_info:
            commit_hash, commit_message = commit.split(',', 1)
            if "fix" in commit_message.lower():
                issue = Issue(title=f"Bug Fix - {commit_hash}", description=commit_message, status="Open", labels="Bug")
                db.session.add(issue)
                db.session.commit()

            new_commit = Commit(commit_hash=commit_hash, commit_message=commit_message)
            db.session.add(new_commit)
            db.session.commit()

        commit_count = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'], stderr=subprocess.PIPE).decode('utf-8').strip()
        latest_commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
        latest_commit_message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').strip()

        result = {
            'commit_count': commit_count,
            'latest_commit_hash': latest_commit_hash,
            'latest_commit_message': latest_commit_message,
            'commits': Commit.query.all()
        }

        return result

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8').strip()
        print(f"Error analyzing repository: {error_output}")
        return {'error': f"Error analyzing repository: {error_output}"}

    except Exception as e:
        print(f"Error analyzing repository: {str(e)}")
        return {'error': f"Error analyzing repository: {str(e)}"}

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
