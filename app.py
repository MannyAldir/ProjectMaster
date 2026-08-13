# import dependancy
from datetime import datetime, date, timedelta
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Project, Milestone, Task, db
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy import select, func, case, delete
from validation_forms.edit_task import TaskForm
from validation_forms.registration import RegistrationForm
from validation_forms.login import loginForm
from validation_forms.projectForm import ProjectForm
from calendar_queries import get_all_milestones_from_user, get_all_tasks_from_user
from calendar_helper import *
from config import Config

# create a Flask object using file name as argument
app = Flask(__name__) 

#set up configuration
app.config.from_object(Config)

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
    form = loginForm()
    if form.validate_on_submit():
        user = form.user
        login_user(user)
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        if User.query.filter_by(email=email).first():
            form.email.errors.append("Email already registered")
            return render_template('register.html',form = form)
        user =(
            User(
            firstName = form.first_name.data.strip(),
            lastName = form.last_name.data.strip(),
            passwordHash = generate_password_hash(form.password.data),
            email = email

        ))
        db.session.add(user)
        db.session.commit()
        flash("Registration Successful.", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form = form)

@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
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
            Milestone.status != 'completed',
            Project.userId == current_user.userId,
            Project.status != 'completed',
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
            Task.status != 'completed',
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
        select(Task, func.coalesce(Task.dueDate,Milestone.endDate).label('due_date'))
        .join(Milestone, Task.milestoneId == Milestone.milestoneId)
        .join(Project, Project.projectId == Task.projectId)
        .where(
            Task.milestoneId.is_not(None),
            Task.status != 'completed',
            Project.userId == current_user.userId,
            Project.status != 'completed',
            today <= Milestone.endDate,
            Milestone.status != 'completed',
            Milestone.endDate <= seven_days_later
        )
    )
    upcoming_milestone_tasks = db.session.execute(stmt).all()

    # normalize data
    normalized = []
    
    for m in upcoming_milestones:
        normalized.append({'type':'Milestone', 'name':m.milestoneName, 'due': m.endDate, 'project_link': url_for('project_detail', projectId=m.projectId)})

    for mt, due_date in upcoming_milestone_tasks:
        normalized.append({'type' : 'Task', 'name': mt.taskName, 'due' : due_date, 'project_link' : url_for('project_detail', projectId=mt.projectId)})

    for t in upcoming_standalone_tasks:
        normalized.append({'type' : 'Task', 'name' : t.taskName, 'due' : t.dueDate, 'project_link' : url_for('project_detail',projectId=t.projectId)})

    # sort
    sorted_deliverables = sorted(normalized, key=lambda x:(x['due'], 0 if x['type'] == 'Milestone' else 1))


    stmt = (
        select(
            Project.projectId, Project.projectName,
            func.count(Task.taskId).label('total_tasks'), func.count(Task.taskId).filter(Task.status == 'completed').label('completed_tasks')
        )
        .join(Task, Task.projectId == Project.projectId)
        .where(Project.userId == current_user.userId, Project.status != 'completed')
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
            'percent' : round(percent,1)
            
        })
    percent_and_ttc = sorted(normalized, key=lambda x : (x['percent'],x['ttc']), reverse=True)

    #over due deliverables
    # Milestones, and milestone tasks and standaline tasks that have an end date
    # standalone tasks with no end date shall be ignored?
    # query seperately then concatinate?
    
    # query overdue milestones
    stmt = (
        select(Milestone, Project.projectName.label('projectName'))
        .join(Project,Project.projectId == Milestone.projectId)
        .where(
            Milestone.status != 'completed',
            today > Milestone.endDate,
            Project.userId == current_user.userId
        )
    )

    overdue_milestones = db.session.execute(stmt).all()

    # query overdue milestone tasks
    stmt = (
        select(Task, func.coalesce(Task.dueDate,Milestone.endDate).label('effective_due_date'), Project.projectName.label('projectName'))
        .join(Project, Project.projectId == Task.projectId)
        .join(Milestone, Milestone.milestoneId == Task.milestoneId)
        .where(Task.milestoneId.is_not(None),
               Project.userId == current_user.userId,
               Task.status != 'completed',
               func.coalesce(Task.dueDate,Milestone.endDate) < today

        )
    )

    overdue_milestone_tasks = db.session.execute(stmt).all()

    # query overdue standalone tasks
    stmt = (
        select(Task, Project.projectName.label('projectName'))
        .join(Project, Task.projectId == Project.projectId)
        .where(
            Task.milestoneId.is_(None),
            Task.status != 'completed',
            Task.dueDate < today,
            Project.userId == current_user.userId
        )
    )
    stand_alone_tasks = db.session.execute(stmt).all()

    # standardize overdue deliverables using dictionary
    normalized = []
    for m, p in overdue_milestones:
        dod = (today - m.endDate).days
        normalized.append({'task': m.milestoneName, 'project' : p, 'dod' : dod })

    for mt, dd, p in overdue_milestone_tasks:
        dod = (today - dd).days
        normalized.append({'task' : mt.taskName, 'project' : p, 'dod' : dod})

    for t, p in stand_alone_tasks:
        dod = (today - t.dueDate).days
        normalized.append({'task' : t.taskName, 'project' : p, 'dod' : dod})
    
    overdue_items = sorted(normalized,key = lambda x:x['dod'])
 
    return render_template(
        'dashboard.html', upcoming_deliverables = sorted_deliverables,
        active_projects=num_of_active_project, percent_and_ttc=percent_and_ttc,
        overdue_items = overdue_items
        )

@app.route('/projects', methods=['GET','POST'])
@login_required
def project_page():
    stmt = (
        select(Project)
        .where(Project.userId == current_user.userId)
        .order_by(
            case(
                (Project.status == 'active', 0),
                else_=1
            ),Project.projectName
        )
    )

    projects = db.session.execute(stmt).scalars().all()
    return render_template('projects.html', projects=projects)

@app.route('/project/new', methods=['GET','POST'])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():

        db.session.add(Project(userId=current_user.userId, projectName=form.projectName.data, description=form.description.data, status=form.status.data, startDate=form.startDate.data))
        db.session.commit()
        return redirect(url_for('project_page'))
    return render_template('new_project.html', form=form)

@app.route('/project/<int:projectId>/edit', methods=['GET','POST'])
@login_required
def edit_project(projectId):
        
        project = Project.query.filter_by(projectId=projectId, userId=current_user.userId).first_or_404()
        form = ProjectForm(existing_data=project, obj=project)
        if form.validate_on_submit():
            form.populate_obj(project)
            db.session.commit()
            return redirect(url_for('project_page'))
        return render_template('edit_project.html', form=form)

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

@app.route('/project/<int:projectId>/milestone/<milestoneId>/newTask', methods=['GET', 'POST'])
@login_required
def new_task(projectId, milestoneId):
    stmt = (
        select(Project)
        .where(
            Project.userId == current_user.userId,
            Project.projectId == projectId
        )
    )
    project = db.session.scalar(stmt)
    if project is None:
        abort(404)

    if milestoneId == 'none':
        milestoneId = None
           
    else:
        try:
            int(milestoneId)
        except ValueError:
            abort(404)
        
        # check if milestone exists to the user
        milestoneId = int(milestoneId)
        stmt = (
            select(Milestone)
            .where(Milestone.milestoneId == milestoneId,
                Milestone.projectId == projectId)
            
        )
        milestone = db.session.scalar(stmt)
        if milestone is None:
            abort(404)
    form = TaskForm(existing_data=None)

    if form.validate_on_submit():
        task = Task(projectId=projectId, milestoneId=milestoneId)
        form.populate_obj(task)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('project_detail', projectId=projectId))
    return render_template('new_task.html', milestoneId=milestoneId, projectId=projectId, form=form)

@app.route('/project/<int:projectId>/task/<int:taskId>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(projectId,taskId):
    stmt = (
        select(Task)
        .join(Project, Task.projectId == Project.projectId)
        .where(
            Project.userId == current_user.userId,
            Task.projectId == projectId,
            Task.taskId == taskId
        )
    )
    task = db.session.scalar(stmt)

    if task is None:
        abort(404)
    form = TaskForm(existing_data=task, obj=task)

    if form.validate_on_submit(): # post request and validated
        form.populate_obj(task)
        db.session.commit()
        return redirect(url_for('project_detail' ,projectId=projectId))
    return render_template('edit_task.html', form = form, task=task, projectId=projectId, taskId=taskId)


@app.route('/project/<int:projectId>/delete', methods=['POST'])
@login_required
def delete_project(projectId):
        # try:
        #     validate_csrf(request.form.get('csrf_token'))
        # except ValidationError:
        #     abort(400)
        project_stmt = (
            select(Project)
            .where(
                Project.userId == current_user.userId,
                Project.projectId == projectId
            )
        )
        project = db.session.scalar(project_stmt)

        if project == None:
            abort(404)
               
        milestone_stmt = (
            select(Milestone)
            .where(Milestone.projectId == projectId)
        )

        milestones = db.session.scalars(milestone_stmt).all()

        tasks_stmt = (
            select(Task)
            .where(Task.projectId == projectId)
        )

        tasks = db.session.scalars(tasks_stmt).all()

        for t in tasks:
            db.session.delete(t)
        
        for m in milestones:
            db.session.delete(m)
        
        db.session.delete(project)
        db.session.commit()


        return redirect(url_for('project_page'))

@app.route('/project/<int:projectId>/task/<int:taskId>/delete', methods=['POST'])
@login_required
def delete_task(projectId, taskId):
    
    stmt = (
        select(Task)
        .join(Project, Project.projectId == Task.projectId)
        .where(
            Task.projectId == projectId,
            Task.taskId == taskId,
            current_user.userId == Project.userId
        )
    )
    task = db.session.scalar(stmt)

    if task == None:
        abort(404)
    db.session.delete(task)
    db.session.commit()
        
    return redirect(url_for('project_detail' , projectId=projectId) )

@app.route('/project/<int:projectId>/milestone/<int:milestoneId>/delete', methods=['POST'])
@login_required
def delete_milestone(projectId,milestoneId):
    project_stmt = (
        select(Project)
        .where(Project.userId == current_user.userId, Project.projectId == projectId)
    )

    project = db.session.scalar(project_stmt)
    if project is None:
        abort(404, description='project not found')
    
    milestone_stmt = (
    select(Milestone)
    .where(
        Milestone.milestoneId == milestoneId,
        Milestone.projectId == projectId
    )
        )
    milestone = db.session.scalar(milestone_stmt)

    if milestone is None:
        abort(404, description='milestone not found')

    task_stmt = (
        select(Task)
        .where(Task.projectId == projectId, Task.milestoneId == milestoneId)
    )

    tasks = db.session.scalars(task_stmt).all()

    for t in tasks:
        db.session.delete(t)

    db.session.delete(milestone)
    db.session.commit()
    
    return redirect(url_for('project_detail', projectId=projectId))

@app.route('/calendar', methods=['GET'])
@login_required
def calendar():
    return render_template('calendar.html')

@app.route('/calendar/events', methods=['GET'])
@login_required
def calendar_json():
    userId = current_user.userId
    tasks = get_all_tasks_from_user(userId)
    milestones = get_all_milestones_from_user(userId)
    milestone_events = get_milestone_events(milestones)
    task_events = get_task_events(tasks)
    return jsonify(milestone_events + task_events)
    
if __name__ == '__main__':
    app.run(debug=True)