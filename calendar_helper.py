from models import Task, Milestone
from datetime import timedelta

def get_project_color(projectId : int)->str:
    hue = (projectId * 137) % 360

    return f'hsl({hue}, 65%, 50%)'

def convert_task_to_event(task : Task | None)->dict:
    if not task or not task.dueDate :
        return None

    event = {
        'id' : f"task-{task.taskId}",
        'title' : task.taskName,
        'start' : task.dueDate.isoformat(),
        'color' : get_project_color(task.projectId),
        'display' : 'auto'
    }

    return event

def convert_milestone_to_event(milestone: Milestone | None)->dict:
    if not milestone:
        return None
    event = {
        'id' : f"milestone-{milestone.milestoneId}",
        'title' : milestone.milestoneName,
        'start' : milestone.startDate.isoformat(),
        'end' : ( milestone.endDate +  timedelta(days=1) ).isoformat(),
        'color' : get_project_color(milestone.projectId),
        'display' : 'background'
    }

    return event

def get_task_events(tasks : list[Task])->list[dict]:
  events = []
  for task in tasks:
      event = convert_task_to_event(task)
      if event is not None:
          events.append(event)
  return events

def get_milestone_events(milestones : list[Milestone])->list[dict]:
    events = []
    for milestone in milestones:
        event = convert_milestone_to_event(milestone)
        if event is not None:
            events.append(event)
    return events