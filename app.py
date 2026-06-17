# import dependancy
from flask import Flask, render_template, request
from models import db

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
        print(email,password)
    else:
        print('No POST info')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)