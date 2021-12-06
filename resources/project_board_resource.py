"""
This is module supports all the REST actions for querying Project Board data/details.
"""
from sqlalchemy import func
from app_config import db
from models import Board, Team, Task
from resources import team_resource
from pathlib import Path
from datetime import datetime
import json

"""
A project board is a unit of delivery for a project.
Each board will have a set of tasks assigned to a user.
"""

"""
A method to serialize a objects' list into
JSON compatible string, i.e Python dict{}
"""
def serialize_objects_list(boards_obj_list):
    board_list = []
    for board_obj in boards_obj_list:        
        board_list.append(serialize_object(board_obj))
    return board_list


"""
A helper method to serialize a single object into
JSON compatible string, i.e Python dict{}
"""
def serialize_object(board_obj):
  board_dict = {}
  board_dict["id"] = board_obj.id
  board_dict["name"] = board_obj.board_name
  return board_dict


"""
A method to take in a board's details.
from a JSON string and save to the DB.

:request: A JSON string with the board details.
    Eg. {   "name" : "<board_name>",
            "description" : "<description>",
            "team_id" : "<team id>"
            "creation_time" : "<date:time when board was created>"
        }
:return: A JSON string with the response {"id" : <board_id>}

Constraint:
        * board name must be unique for a team
        * board name can be max 64 characters
        * description can be max 128 characters
"""
def create_board(new_board_json):
    try: 
        team_id_from_user = int(new_board_json.get("team_id"))
    except ValueError as ve:
        return {"error": "TeamId should be numeric."}, 400

    if team_id_from_user is not None:

        team_obj = team_resource.does_team_exists(team_id_from_user)
        if isinstance(team_obj, Team):
            
            # Creating a new Board obj
            board_obj = Board(
                board_name=new_board_json.get("name"),
                board_desc=new_board_json.get("description"),
                board_team_id=team_id_from_user
            )          
            
            # Saving the new Board to DB
            db.session.add(board_obj)
            db.session.commit()

            # Gets the new board_id
            board_id = db.session.query(func.max(Board.id)).scalar()

            return { "id": board_id}, 201
        else:
            return {"error" : team_obj}, 404
    else:
        return {"error" : "TeamId must be specified."}, 400


"""
A method to add a new task to a specified board.

:request: A JSON string with the task details.
    Note: A Task is assigned to a user_id who works on the task.
        Eg. {   "title" : "<board_name>",
                "description" : "<description>",
                "board_id": <board_id>
                "user_id" : "<user_id>"
                "creation_time" : "<date:time when task was created>"
            }

:return: A JSON string with the response {"id" : <task_id>}

Constraint:
        * task title must be unique for a board
        * title name can be max 64 characters
        * description can be max 128 characters
"""
def add_task(new_task_json):
    new_task_title = new_task_json.get("title")
    new_task_desc = new_task_json.get("description")
    
    try: 
        board_id = int(new_task_json.get("board_id"))
    except ValueError as ve:
        return {"error": "BoardId should be numeric."}, 400
    try: 
        user_id = int(new_task_json.get("user_id"))
    except ValueError as ve:
        return {"error": "UserId should be numeric."}, 400

    board_obj = Board.query.filter(Board.id == board_id).one_or_none()
    if board_obj is not None:
        team_obj = team_resource.does_team_exists(board_obj.board_team_id)
        board_team_users_id_list = [x.id for x in team_obj.team_users]
        if user_id in board_team_users_id_list:
            task_obj = Task(
                task_title=new_task_title,
                task_desc=new_task_desc,
                task_board_id=board_id,
                task_user_id=user_id
            )

            db.session.add(task_obj)
            db.session.commit()
            # Gets the new task_id
            task_id = db.session.query(func.max(Task.id)).scalar()

            return { "id": task_id}, 201
        else:
            message = f'UserId {user_id} does not belong to TeamId {team_obj.id}, which owns this board.'
            return {"error" : message}, 400
    else:
        error_message = f'BoardId {board_id} does not exits.'
        return {"error": error_message}, 404


"""
A method to update task status.

:request: A JSON string with the task details
    Eg. 
        {   "id" : <task_id>,
            "status" : <OPEN/IN_PROGRESS/COMPLETE>
        }
:return:
"""
def update_task_status(task_update_json):

    try: 
        task_id = int(task_update_json.get("id"))
    except ValueError as ve:
        return {"error": "TaskId should be numeric."}, 400

    task_status = task_update_json.get("status")
    if task_status not in ["OPEN", "IN_PROGRESS", "COMPLETE"]:
        return {"error": "Status can be either OPEN, IN_PROGRESS or COMPLETE."}, 400

    task_obj = Task.query.filter(Task.id == task_id).one_or_none()
    if task_obj is not None:
        task_obj.task_status = task_status

        db.session.add(task_obj)
        db.session.commit()
        message = f'TaskId {task_id} is now {task_status}.'
        return { "message": message}, 200
    else:
        error_message = f'TaskId {task_id} does not exits.'
        return {"error": error_message}, 404


"""
A method to change baord status to CLOSED,
if all tasks are marked as COMPLETE.
Also, record the closing time as end_time(date:time).

:request: A JSON string with the board id to close.
    Eg. {   "id" : <board_id>}
:return:
"""
def close_board(board_id_json):
    try: 
        board_id = int(board_id_json.get("id"))
    except ValueError as ve:
        return {"error": "BoardId should be numeric."}, 400

    board_obj = Board.query.filter(Board.id == board_id).one_or_none()
    if board_obj is not None:
        for task_obj in board_obj.board_tasks:
            if task_obj.task_status != "COMPLETE":
                message = f'Cannot close this board as TaskId {task_obj.id} is not completed.'
                return {"message" : message}, 405
        
        board_obj.board_status = "CLOSED"

        # Saving the updated Board to DB
        db.session.add(board_obj)
        db.session.commit()
        message = f'BoardId {board_id} is now closed.'
        return {"message" : message}, 200

    else:
        error_message = f'BoardId {board_id} does not exits.'
        return {"error": error_message}, 404


"""
A method to list all the boards of a team

:request: A JSON string with the team identifier
        Eg. {   "id" : <team_id>}

:return: A JSON list of all boards of the team.
        Eg. [
                {   "id" : <board_id>,
                    "name" : <board_name>
                }
            ]
"""
def list_boards(team_id_json):
    try: 
        team_id = int(team_id_json.get("id"))
    except ValueError as ve:
        return {"message": "TeamId should be numeric."}, 400
    
    boards_obj_list = Board.query.join(Team).filter_by(id=team_id).all()
    return serialize_objects_list(boards_obj_list)


"""
Export a board to the out folder.
The output will be a txt file. We want you to be creative. 
Output a presentable view of the board and its tasks with the available data.

:request: A JSON string with the board id to close.
    Eg. {   "id" : <board_id>}

:return:
    Eg. { "out_file" : <name of the file created>}
"""
def export_board(board_id_json):
    board_id = board_id_json.get("id")
    board_obj = Board.query.filter(Board.id == board_id).one_or_none()
    if board_obj is not None:
        
        board_dict = {}
        board_dict["boardId"] = board_obj.id
        board_dict["boardName"] = board_obj.board_name
        board_dict["boardDescription"] = board_obj.board_desc
        board_dict["boardTeamId"] = board_obj.board_team_id
        board_dict["boardStatus"] = board_obj.board_status
        board_dict["boardCreatedTime"] = str(board_obj.board_creation_time)
        board_dict["boardClosedTime"] = str(board_obj.board_end_time)

    
        tasks_list = []
        for task_obj in board_obj.board_tasks:
            task_dict = {}
            task_dict["taskId"] = task_obj.id
            task_dict["taskTitle"] = task_obj.task_title
            task_dict["taskDescription"] = task_obj.task_desc
            task_dict["taskUserId"] = task_obj.task_user_id
            task_dict["taskCreated"] = str(task_obj.task_creation_time)
            tasks_list.append(task_dict)

        # Adding user to Board
        board_dict["tasks"] = tasks_list

        # Saving the Python dict to a file
        base_dir = Path.cwd()
        file_name = "export_board_" + datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p") + ".txt"
        with open(base_dir / 'out'/ file_name, "w") as outfile:
            json.dump(board_dict, outfile, indent = 6)
        
        return {"out_file" : file_name}

        
    else:
        error_message = f'BoardId {board_id} does not exits.'
        return {"error": error_message}, 404
