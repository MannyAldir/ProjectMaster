# import dependancy
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Project, Milestone, Task, db
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

# create a Flask object using file name as argument
app = Flask(__name__) 

# set up configuration for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projectmaster.db'

# secret key for session management
app.config['SECRET_KEY'] = 'development-secret-key'

# set connection between Flask app and SQLAlchemy
db.init_app(app)

with app.app_context():
    db.create_all() # create tables in database

# Create flask-Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # set the login view for unauthorized users

# user loader function for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['GET','POST']) # decorator that creates directory path for function
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Query database by email
        user = User.query.filter_by(email=email).first()
        if user:
            # check password hash
            if check_password_hash(user.passwordHash, password):
                # login user and redirect to dashboard
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid password')
        else:
            return render_template('login.html', error='Invalid email or password')


    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    

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

@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/projects', methods=['GET','POST'])
@login_required
def project_page():
    projects = Project.query.filter_by(userId=current_user.userId).all()
    return render_template('projects.html', projects=projects)

@app.route('/project/new', methods=['GET','POST'])
@login_required
def new_project():
    if request.method == 'POST':
        projectName = request.form['projectName']
        description = request.form['description']
        status = request.form['status']
        startDate = request.form['startDate']

        # convert html date input to datetime object
        if startDate:
            startDate = datetime.strptime(startDate, '%Y-%m-%d')
        else:
            startDate = None


        db.session.add(Project(userId=current_user.userId, projectName=projectName, description=description, status=status, startDate=startDate))
        db.session.commit()
        return redirect(url_for('project_page'))
    return render_template('new_project.html')


if __name__ == '__main__':
    app.run(debug=True)