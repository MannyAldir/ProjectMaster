# import dependancy
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Project, Milestone, Task, db
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from forms import RegistrationForm, LoginForm


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
    # Create form object
    form = LoginForm()

    if form.validate_on_submit():
        # check if user exists by email
        query_user = User.query.filter_by(email=form.email.data).first()

        # Check if query returns a user and password matches database
        if query_user and check_password_hash(query_user.passwordHash,form.password.data):
            # authenticate user
            login_user(query_user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", 'error')
            return render_template('login.html', form=form)

    return render_template('login.html',form=form)
    

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    

@app.route('/register', methods=['GET','POST'])
def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            # Check if user exists
            if not User.query.filter_by(email=form.email.data).first():
                new_user = User(
                    firstName=form.first_name.data,
                    lastName= form.last_name.data,
                    email=form.email.data,
                    # hash/salt password before storing in database
                    passwordHash=generate_password_hash(form.password.data)
                )
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                flash('An account with that email has already been registered.', 'error')
                return render_template('register.html',form=form)
        return render_template('register.html', form=form)

@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html',user=current_user.firstName)

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

@app.route('/project/<int:projectId>/edit', methods=['GET','POST'])
@login_required
def edit_project(projectId):
        
        project = Project.query.filter_by(projectId=projectId, userId=current_user.userId).first()
        if request.method == 'POST':
            project.projectName = request.form['projectName']
            project.description = request.form['description']
            project.status = request.form['status']
            project.startDate = datetime.strptime(request.form['startDate'], '%Y-%m-%d').date() if request.form['startDate'] else None
            db.session.commit()
            return redirect(url_for('project_page'))
        return render_template('edit_project.html', project=project)

@app.route('/project/<int:projectId>', methods=['GET'])
@login_required
def project_detail(projectId):
    
    #query for projects
    project = Project.query.filter_by(
        projectId = projectId, userId=current_user.userId
    ).first_or_404()
    
    # query for milestone that belong to the project
    milestones = Milestone.query.filter_by(projectId = projectId).all()

    # query for tasks that are apart of milestones
    tasks = Task.query.filter(
        Task.projectId == projectId, Task.milestoneId != None
    ).all()

    # query for tasks that are independent of milestones
    independentTasks = Task.query.filter_by(projectId = projectId, milestoneId=None).all()

    return render_template('project_detail.html', milestones=milestones, tasks=tasks,independentTasks=independentTasks, project=project)

@app.route('/project/<int:projectId>/newMilestone', methods=['GET','POST'])
@login_required
def new_milestone(projectId):
    project = Project.query.filter_by(projectId=projectId, userId=current_user.userId).first_or_404()
    
    if request.method == 'POST':
        milestoneName = request.form['milestoneName']
        milestoneStatus = request.form['milestoneStatus']
        milestoneDescription = request.form['milestoneDescription']
        milestoneStartDate = datetime.strptime(request.form['milestoneStartDate'], '%Y-%m-%d').date() if request.form['milestoneStartDate'] else None
        milestoneEndDate = datetime.strptime(request.form['milestoneEndDate'], '%Y-%m-%d').date() if request.form['milestoneEndDate'] else None
        newMilestone=Milestone(
            projectId = projectId, milestoneName = milestoneName, status = milestoneStatus,
            description = milestoneDescription, startDate = milestoneStartDate,
            endDate = milestoneEndDate
        )

        db.session.add(newMilestone)
        db.session.commit()
        return redirect(url_for('project_detail', projectId=project.projectId))
    return render_template('new_milestone.html',project=project)

@app.route('/project/<int:projectId>/<int:milestoneId>/edit', methods=['GET', 'POST'])
@login_required
def edit_milestone(projectId,milestoneId):
    project = Project.query.filter_by(projectId=projectId,userId=current_user.userId).first_or_404()
    milestone = Milestone.query.filter_by(projectId=projectId,milestoneId=milestoneId).first_or_404()

    if request.method == 'POST':
        milestone.milestoneName = request.form['milestoneName']
        milestone.description = request.form['milestoneDescription']
        milestone.status = request.form['milestoneStatus']
        milestone.startDate = datetime.strptime(request.form['milestoneStartDate'], '%Y-%m-%d').date() if request.form['milestoneStartDate'] else None
        milestone.endDate= datetime.strptime(request.form['milestoneEndDate'],'%Y-%m-%d').date() if request.form['milestoneEndDate'] else None
        milestone.status = request.form['milestoneStatus']
        db.session.commit()
        return redirect(url_for('project_detail', projectId=projectId))
    return render_template('edit_milestone.html',milestone=milestone, project=project)

@app.route('/project/<int:projectId>/newTask', methods=['GET', 'POST'])
@login_required
def new_task(projectId):
    project = Project.query.filter_by(projectId=projectId, userId=current_user.userId).first_or_404()
    milestones = Milestone.query.filter_by(projectId=projectId).all()
    
    if request.method == 'POST':
        taskName = request.form['taskName']
        taskDescription = request.form['taskDescription']
        taskDueDate = datetime.strptime(request.form['taskDueDate'], '%Y-%m-%d') if request.form['taskDueDate'] else None
        taskStatus = request.form['taskStatus']
        milestoneId = int(request.form['taskAssignment'])

        newTask = Task(
            projectId = projectId, milestoneId=milestoneId,
            taskName=taskName, description=taskDescription,
            dueDate = taskDueDate, status=taskStatus
        ) if milestoneId != 0 else Task(projectId= projectId, milestoneId=None, taskName = taskName, 
                                        description=taskDescription, dueDate = taskDueDate, status = taskStatus)
        
        db.session.add(newTask)
        db.session.commit()
        return redirect(url_for('project_detail', projectId=projectId))
    return render_template('new_task.html', projectId=projectId, milestones=milestones)

@app.route('/project/<int:projectId>/task/<int:taskId>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(projectId,taskId):
    task = Task.query.filter_by(projectId=projectId, taskId=taskId).first_or_404()
    if request.method == 'POST':
        # extract form input
        task.taskName = request.form['taskName']
        task.description = request.form['taskDescription']
        task.dueDate = datetime.strptime(request.form['taskDueDate'], '%Y-%m-%d').date() if \
        request.form['taskDueDate'] else None
        task.status= request.form['taskStatus']
        db.session.commit()
        return redirect(url_for('project_detail',projectId=projectId))
    return render_template('edit_task.html', task=task)
        

        
if __name__ == '__main__':
    app.run(debug=True)