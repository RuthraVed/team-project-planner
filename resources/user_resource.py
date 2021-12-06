"""
This is module supports all the REST actions for querying Users data/details.
"""

from sqlalchemy import func
from app_config import db
from models import Team, User, teams_m2m_users
from resources import team_resource

"""
A helper method to convert JSON To Python Objects & save to DB

"""
def db_add(user_json, user_obj=None, user_id=None):
    # To update an user
    if user_obj is not None:
        user_obj.user_disp_name = user_json.get("user").get("display_name")
        user_obj.user_desc = user_json.get("user").get("description")
        db.session.add(user_obj)
        db.session.commit()
        return User.query.filter(User.id == user_id).one_or_none()  # Returns the updated user
    # To add a new user
    else:
        
        # Creating a new User obj
        user_obj = User(  user_name=user_json.get("name"),
                          user_disp_name=user_json.get("display_name"),
                          user_desc=user_json.get("description"),
                        )
        
        # Saving the new User to DB
        db.session.add(user_obj)
        db.session.commit()
        new_user_id = db.session.query(func.max(User.id)).scalar()
        return new_user_id  # Returns the new user_id


"""
A method to take in user details.
from a json string and save to a DB.

:request: A JSON string with the user details
:return:  A JSON string as {"id" : "<user_id>"}
"""
def create_user(user_json):
  return { "id": db_add(user_json)}, 201


"""
A method to serialize a objects' list into
JSON compatible string, i.e Python dict{}
"""
def serialize_objects_list(users_obj_list):
    users_list = []
    for user_obj in users_obj_list:        
        users_list.append(serialize_object(user_obj))
    return users_list

"""
A helper method to serialize a single object into
JSON compatible string, i.e Python dict{}
"""
def serialize_object(user_obj):
  user_dict = {}
  user_dict["name"] = user_obj.user_name
  user_dict["display_name"] = user_obj.user_disp_name
  user_dict["description"] = user_obj.user_desc
  user_dict["creation_time"] = user_obj.user_creation_time
  return user_dict


"""
A helper method to check if an user exists in DB or not.
:return: user_obj if exists, else an error message
"""
def does_user_exists(user_id):
  user_obj = User.query.filter(User.id == user_id).one_or_none()
  if user_obj is None:
    error_message = f'UserId {user_id} does not exits.'
    return error_message
  else:
    return user_obj


"""
A method to display all the user details.

:return: A JSON list with user details from DB
      Eg.
          [{  "name" : <user_name>,
              "display_name" : <display name>,
              "creation_time" : <date:time format>
            },
          ]
"""
def list_users(_limit=None):
  users_obj_list = db.session.query(User).order_by(User.id).limit(_limit).all()
  return serialize_objects_list(users_obj_list)


"""
A method to get details of a single user.

:request: A JSON string with the desired user_id
      Eg. { "id" : <user_id> }

:return: A JSON string with the user details
      Eg. { "name" : "<user_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>"
          }

"""
def describe_user(user_id_json):
  try: 
        user_id = int(user_id_json.get("id"))
  except ValueError as ve:
    return {"message": "userId should be numeric."}, 400

  user_obj = does_user_exists(user_id)
  if isinstance(user_obj, User):
    return serialize_object(user_obj)
  else:
    return {"message" : user_obj}, 404


"""
A method to update user details.

:request: A JSON string with the user details
      Eg. { "id" : "<user_id>",
            "user" : {
                        "display_name" : <display name>,
                        "description" : <description>
                      }
          }
:return:
  Constraint:
            * user name cannot be updated
            * name can be max 64 characters
            * display name can be max 128 characters
"""
def update_user(new_details_json):
  try: 
      user_id = int(new_details_json.get("id"))
  except ValueError as ve:
    return {"message": "userId should be numeric."}, 400

  user_obj = does_user_exists(new_details_json.get("id"))
  if isinstance(user_obj, User):
    updated_user = db_add(new_details_json, user_obj, user_id)
    return serialize_object(updated_user), 201
  else:
    return {"message" : user_obj}, 404


"""
A method to get all the teams,
which the user is part of.

:request: A JSON string with the desired user_id
      Eg. { "id" : <user_id> }

:return: A JSON list of all the teams.
      Eg.
          [{  "name" : <team_name>,
              "description" : <description>,
              "creation_time" : <date:time format>
            },
          ]

"""
def get_user_teams(user_id_json):  
  try: 
        user_id = int(user_id_json.get("id"))
  except ValueError as ve:
    return {"message": "userId should be numeric."}, 400

  teams_obj_list = Team.query.join(teams_m2m_users).filter_by(user_id=user_id).all()
  return team_resource.serialize_objects_list(teams_obj_list)


