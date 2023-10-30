from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///git_tracker.db'
db = SQLAlchemy(app)

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open')

db.create_all()

@app.route('/')
def index():
    issues = Issue.query.all()
    return render_template('index.html', issues=issues)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        new_issue = Issue(title=title, description=description)
        db.session.add(new_issue)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    issue = Issue.query.get(id)

    if request.method == 'POST':
        issue.title = request.form['title']
        issue.description = request.form['description']
        issue.status = request.form['status']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update.html', issue=issue)

if __name__ == '__main__':
    app.run(debug=True)
