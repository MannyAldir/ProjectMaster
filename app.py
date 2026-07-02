# import dependancy
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Project, Milestone, Task, db
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy import select, func


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
    
    # calculate dashboard metrics

    # Calculate total number of active projects
    
    num_of_active_project = db.session.scalar(select(func.count(Project.projectId)).where(
        Project.userId == current_user.userId,
        Project.status == 'active'
    ))


    # find upcoming within 7 days of duedate: milestones,tasks and independent tasks then concatinate them into one list
              #         today<=due_date<=today+7
    today = date.today()
    seven_days_later = today + timedelta(7)


    # query for milestones that are due within 7 days of today
    stmt = (
        select(Milestone)
        .join(Project,Project.projectId == Milestone.projectId)
        .where(
            Milestone.status != 'Completed',
            Project.userId == current_user.userId,
            today <= Milestone.endDate,
            Milestone.endDate <= seven_days_later
        )
    )
    upcoming_milestones = db.session.execute(stmt).scalars().all()

    # query for standalone tasks
    # I need to select all columns in tasks where the task belongs to current user
    # the task should not be completed
    # the task should not have a milestone Id
    # the tasks due date should be between today and today +7
    stmt = (
        select(Task)
        .join(Project, Project.projectId == Task.projectId)
        .where(
            Project.userId == current_user.userId,
            Task.status != 'Completed',
            Task.milestoneId.is_(None),
            today <= Task.dueDate,
            Task.dueDate <= seven_days_later
        )
    )

    upcoming_standalone_tasks = db.session.execute(stmt).scalars().all()

    # Query for milestone tasks
    # 1) the task milestoneId should not be None
    # 2) the task should not be completed
    # 3) the task should belong to the user
    # 4) the milestone due date should be between today and 7 days from today

    # This query needs 2 joins because I need to access milestone table and task table
    stmt = (
        select(Task)
        .join(Milestone, Task.milestoneId == Milestone.milestoneId)
        .join(Project, Project.projectId == Task.projectId)
        .where(
            Task.milestoneId.is_not(None),
            Task.status != 'Completed',
            Project.userId == current_user.userId,
            today <= Milestone.endDate,
            Milestone.status != 'Completed',
            Milestone.endDate <= seven_days_later
        )
    )
    upcoming_milestone_tasks = db.session.execute(stmt).scalars().all()

    # normalize data
    normalized = []
    
    for m in upcoming_milestones:
        normalized.append({'type':'Milestone', 'name':m.milestoneName, 'due': m.endDate, 'project_link': url_for('project_detail', projectId=m.projectId)})

    for mt in upcoming_milestone_tasks:
        normalized.append({'type' : 'Task', 'name': mt.taskName, 'due' : mt.dueDate, 'project_link' : url_for('project_detail', projectId=mt.projectId)})

    for t in upcoming_standalone_tasks:
        normalized.append({'type' : 'Task', 'name' : t.taskName, 'due' : t.dueDate, 'project_link' : url_for('project_detail',projectId=t.projectId)})

    # sort
    sorted_deliverables = sorted(normalized, key=lambda x:(x['due'], 0 if x['type'] == 'Milestone' else 1))


    stmt = (
        select(
            Project.projectId, Project.projectName,
            func(Task.taskId.label('total_tasks'), func(filter(Task.status == 'Completed')).label('completed_tasks'))
        )
        .join(Task, Task.projectId == Project.projectId)
        .where(Project.userId == current_user.userId)
        .group_by(Project.projectId)

    )

    tasks = db.session.execute(stmt).all()

    # normalize data
    normalized = []

    for t in tasks :
        
        percent = ( t.completed_tasks/t.total_tasks ) * 100 if t.total_tasks > 0 else 0
        normalized.append({
            'name' : t.projectName, 'id' : t.projectId,
            'ttc' :  t.total_tasks - t.completed_tasks,
            'link' : url_for('project_detail', projectId=t.projectId),
            'percent' : percent
            
        })
    

 
    return render_template(
        'dashboard.html', upcoming_deliverables = sorted_deliverables,
        active_projects=num_of_active_project
        )

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