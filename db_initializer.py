import json
from pathlib import Path
from app_config import db
from datetime import date
from models import User, Team
from resources import user_resource, team_resource, project_board_resource

CURRENT_DIR = Path.cwd()
SQLITE_DB_FILE = CURRENT_DIR / 'db/team_project_planner.db'
DATA_FILES = CURRENT_DIR / 'data_files/'


def db_remove_old():
    # Delete database file if it exists currently
    SQLITE_DB_FILE.unlink(missing_ok=True)

    # Create the database
    db.create_all()


# ----------------ADDING NEW USERS------------------------------------------
def load_users_to_db():

    # Reading from the users.json file
    with open(DATA_FILES / "users.json", "r") as json_file:
        users = json.load(json_file)

    for user in users:
        # Using the method user_resource.create_user()
        print(user_resource.create_user(user))
        
    print("\tINFO: Users' table created.")


# ----------------ADDING NEW TEAMS------------------------------------------
def load_teams_to_db():
    # Reading from the teams.json file
    with open(DATA_FILES / "teams.json", "r") as json_file:
        teams = json.load(json_file)

    for team in teams:
        print(team_resource.create_team(team))
        
    print("\tINFO: Teams' table created.")


# ----------------ADDING NEW BOARDS------------------------------------------
def load_boards_to_db():
    # Reading from the boards.json file
    with open(DATA_FILES / "boards.json", "r") as json_file:
        boards = json.load(json_file)

    for board in boards:
        print(project_board_resource.create_board(board))
        
    print("\tINFO: Boards' table created.")


# ----------------ADDING USERS TO MULTIPLE TEAMS----------------------------------------------
def multiple_team_add_users():
    with open(DATA_FILES / "addUsers.json", "r") as json_file:
        team_users = json.load(json_file)

    for team_user in team_users:
        print(f'\tADD_USERS_TO_TEAM --> {team_resource.add_users_to_team(team_user)}')
        
    print("\tINFO: Team users added to Team table.")


# ----------------REMOVING USERS FROM MULTIPLE TEAMS------------------------------------------
def multiple_team_remove_users():
    with open(DATA_FILES / "removeUsers.json", "r") as json_file:
        team_users = json.load(json_file)
    for team_user in team_users:
        print(f'\tREMOVE_USERS_FROM_TEAM --> {team_resource.remove_users_from_team(team_user)}')
        
    print("\tINFO: Team users removed to Team table.")


# ----------------ADDING NEW TASKS------------------------------------------
def load_tasks_to_db():
    # Reading from the boards.json file
    with open(DATA_FILES / "tasks.json", "r") as json_file:
        tasks = json.load(json_file)

    for task in tasks:
        print(project_board_resource.add_task(task))
        
    print("\tINFO: Tasks' table created.")


# ----------------REMOVING USERS FROM MULTIPLE TEAMS------------------------------------------
def multiple_task_updates():
    with open(DATA_FILES / "updateTaskStatus.json", "r") as json_file:
        tasks = json.load(json_file)
    for task in tasks:
        print(f'\tUPDATE_TASK_STATUS --> {project_board_resource.update_task_status(task)}')
        
    print("\tINFO: Tasks updated to COMPLETE.")


#---------------------MAIN-------------------------------------------------------------------
def db_initialize():

    db_remove_old()

    load_users_to_db()
    load_teams_to_db()
    load_boards_to_db()

    multiple_team_add_users()
    load_tasks_to_db()

    print("\tINFO: Successful DB initialization")


db_initialize()
