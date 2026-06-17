# import dependancy
from flask import Flask, render_template, request, redirect, url_for
from models import db
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Project, Milestone, Task

# create a Flask object using file name as argument
app = Flask(__name__) 

# set up configuration for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projectmaster.db'

# set connection between Flask app and SQLAlchemy
db.init_app(app)

with app.app_context():
    db.create_all() # create tables in database

@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['GET','POST']) # decorator that creates directory path for function
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
    else:
        print('No POST info')
    return render_template('login.html')
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        passwordHash = generate_password_hash(password)
        db.session.add(User(firstName=firstName, lastName=lastName, email=email, passwordHash=passwordHash))
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)