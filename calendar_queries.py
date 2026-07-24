from models import Milestone, Task, Project
from sqlalchemy import select
from models import db

# query all milestones and tasks from active projects
def get_all_milestones_from_user(user_id : int)->list[(Milestone,Project)]:
    stmt = (
        select(Milestone,Project)
        .join(Project, Project.projectId == Milestone.projectId)
        .where(
            Project.status == 'active',
            Project.userId == user_id
        )
      
    )

    return db.session.execute(stmt).all()

def get_all_tasks_from_user(user_id : int)->list[(Task,Project)]:
    stmt = (
        select(Task, Project)
        .join(Project, Project.projectId == Task.projectId)
        .where(
            Project.status == 'active',
            Project.userId == user_id,
            Task.dueDate.is_not(None)
        )
    )
    return db.session.execute(stmt).all()