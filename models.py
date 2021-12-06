from datetime import datetime
from app_config import db
from sqlalchemy import func



# -------USER MODEL-------------------------
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64), unique=True, nullable=False)
    user_disp_name = db.Column(db.String(64), nullable=False)
    user_desc = db.Column(db.String(128))
    user_creation_time = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return f"[{self.id},\t{self.user_name},\t{self.user_disp_name},\t{self.user_desc},\t{self.user_creation_time}]"


# A helper table for (N:N) relationship (N users: N teams)
teams_m2m_users = db.Table(
    'teams_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

# -------TEAM MODEL-------------------------
class Team(db.Model):
    __tablename__ = "team"
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(64), unique=True, nullable=False)
    team_desc = db.Column(db.String(128))
    team_admin = db.Column(db.Integer, nullable=False)
    team_creation_time = db.Column(db.DateTime, default=datetime.utcnow)

    # defining the one to many relationship on Board
    team_boards = db.relationship('Board', backref='team', lazy=True)
    
    # defining the many to many relationship on User
    team_users = db.relationship('User', secondary=teams_m2m_users, lazy='subquery', backref=db.backref('team', lazy=True))
    
    def __repr__(self):
        print(f'Users of Team: {self.team_users}')
        return f"[{self.id},\t{self.team_name},\t{self.team_desc},\t{self.team_admin},\t{self.team_creation_time}"


# -------BOARD MODEL-------------------------
class Board(db.Model):
    __tablename__ = "board"
    id = db.Column(db.Integer, primary_key=True)
    board_name = db.Column(db.String(64), unique=True, nullable=False)
    board_desc = db.Column(db.String(128))

    # A ForeignKey from Team
    board_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    # defining the one to many relationship on Task
    board_tasks = db.relationship('Task', backref='board', lazy=True)

    board_status = db.Column(db.String(12), default="OPEN")
    board_creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    board_end_time = db.Column(db.DateTime, onupdate=datetime.utcnow)


# -------TASK MODEL-------------------------
class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    task_title = db.Column(db.String(64), unique=True, nullable=False)
    task_desc = db.Column(db.String(128))

    # A ForeignKey from Board
    task_board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)

    task_user_id = db.Column(db.Integer, nullable=False)

    task_status = db.Column(db.String(12), default="OPEN")
    task_creation_time = db.Column(db.DateTime, default=datetime.utcnow)
