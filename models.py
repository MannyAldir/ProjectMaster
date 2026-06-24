from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, ForeignKey, DateTime, Date
from datetime import datetime, timezone, date
from typing import Optional
from flask_login import UserMixin

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model, UserMixin):
    userId: Mapped[int] = mapped_column(primary_key=True)
    firstName:Mapped[str] = mapped_column(nullable=False)
    lastName:Mapped[str] = mapped_column(nullable=False)
    passwordHash:Mapped[str] = mapped_column(nullable=False)
    email:Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    createdAt:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) ,nullable=False)

    def get_id(self):
        return str(self.userId)

class Project(db.Model):
    projectId: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey('user.userId'), nullable=False)
    projectName:Mapped[str] = mapped_column(nullable=False)
    description:Mapped[str] = mapped_column(nullable=True)
    startDate: Mapped[Optional[date]] = mapped_column(Date,nullable=True)
    status: Mapped[str] = mapped_column(nullable=False)
    createdAt:Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc) ,nullable=False)

class Milestone(db.Model):
    milestoneId: Mapped[int] = mapped_column(primary_key=True)
    projectId: Mapped[int] = mapped_column(ForeignKey('project.projectId'), nullable=False)
    milestoneName:Mapped[str] = mapped_column(nullable=False)
    description:Mapped[str] = mapped_column(nullable=True)
    startDate: Mapped[date] = mapped_column(Date, nullable=False)
    endDate: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    createdAt:Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc) ,nullable=False)

class Task(db.Model):
    taskId: Mapped[int] = mapped_column(primary_key=True)
    projectId: Mapped[int] = mapped_column(ForeignKey('project.projectId'), nullable=False)
    milestoneId: Mapped[Optional[int]] = mapped_column(ForeignKey('milestone.milestoneId'), nullable=True)
    taskName:Mapped[str] = mapped_column(nullable=False)
    description:Mapped[str] = mapped_column(nullable=True)
    dueDate: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(nullable=False)
    createdAt:Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc),nullable=False)



