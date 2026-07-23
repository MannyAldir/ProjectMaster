f
from models import Milestone, Task, Project
from sqlalchemy import select
from models import db

# query all milestones and tasks from active projects
def get_all_milestones_from_user(user_id : int)->list[Milestone]:
    stmt = (
        select(Milestone)
        .join(Project, Project.projectId == Milestone.projectId)
        .where(
            Project.status == 'active',
            Project.userId == user_id
        )
      
    )

    return db.session.scalars(stmt).all()

def get_all_tasks_from_user(user_id : int)->list[Task]:
    stmt = (
        select(Task)
        .join(Project, Project.projectId == Task.projectId)
        .where(
            Project.status == 'active',
            Project.userId == user_id,
            Task.dueDate.is_not(None)
        )
    )
    return db.session.scalars(stmt).all()