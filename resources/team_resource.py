"""
This is module supports all the REST actions for querying Teams data/details.
"""
from sqlalchemy import func
from app_config import db
from models import Team, User, teams_m2m_users
from resources import user_resource


"""
A method to serialize a objects' list into
JSON compatible string, i.e Python dict{}
"""
def serialize_objects_list(teams_obj_list):
    teams_list = []
    for team_obj in teams_obj_list:        
        teams_list.append(serialize_object(team_obj))
    return teams_list

"""
A helper method to serialize a single object into
JSON compatible string, i.e Python dict{}
"""
def serialize_object(team_obj):
  team_dict = {}
  team_dict["name"] = team_obj.team_name
  team_dict["description"] = team_obj.team_desc
  team_dict["creation_time"] = team_obj.team_creation_time
  team_dict["admin"] = team_obj.team_admin
  return team_dict


"""
A method to take in a team's details.
from a JSON string and save to the DB.

:request: A JSON string team details.
        Eg. 
            {   "name" : <team_name>,
                "description" : <some description>,
                "admin": <id of a user>
            }
:return:  A JSON string as {"id" : <team_id>}
"""
def create_team(team_json):
    try: 
        admin_id_from_user = int(team_json.get("admin"))
    except ValueError as ve:
        return {"message": "adminId should be numeric."}, 400

    if admin_id_from_user is not None:

        user_obj = user_resource.does_user_exists(admin_id_from_user)
        if isinstance(user_obj, User):
            
            # Creating a new Team obj
            team_obj = Team(
                team_name=team_json.get("name"),
                team_desc=team_json.get("description"),
                team_admin=admin_id_from_user
            )

            # Saving the new Team to DB
            db.session.add(team_obj)
            db.session.commit()

            # 3 Gets the new team_id
            team_id = db.session.query(func.max(Team.id)).scalar()

            # 4 Add the admin as a team user
            add_user_to_team(team_id, admin_id_from_user)

            return { "id": team_id}, 201
        else:
            return {"message" : "An admin must be an existing user."}, 400
    else:
        return {"message" : "Admin must be specified."}, 400


"""
A helper method to check if a team exists in DB or not.
:return: team_obj if exists, else an error message
"""
def does_team_exists(team_id):
  team_obj = Team.query.filter(Team.id == team_id).one_or_none()
  if team_obj is None:
    error_message = f'TeamId {team_id} does not exits.'
    return error_message
  else:
    return team_obj


"""
A helper method to add user to a team.
"""
def add_user_to_team(team_id, user_id):
    team_obj = does_team_exists(team_id)
    if isinstance(team_obj, Team):
        user_obj = user_resource.does_user_exists(user_id)
        if isinstance(user_obj, User):
            team_obj.team_users.append(user_obj)
            # Saving to DB
            db.session.add(team_obj)    
            db.session.commit()
            message = f'UserId {user_id} added to the team.'
            return {"message": message}, 200
        else:
            return {"message" : user_obj}, 404
    else:
        return {"message" : team_obj}, 404

"""
A method to add users to the team.

request: A JSON string with the team details
        Eg. {
                "id" : <team_id>,
                "users" : ["user_id 1", "user_id2"]
            }
:return:
        Constraint:
        * Cap the max users that can be added to 50
"""
def add_users_to_team(team_users_json):
    MAX_USERS = 10
    
    try: 
        team_id = int(team_users_json.get("id"))
    except ValueError as ve:
        return {"message": "TeamId should be numeric."}, 400

    team_obj = does_team_exists(team_id)
    if isinstance(team_obj, Team):
        existing_users_count = len(team_obj.team_users)
        users_id_list = team_users_json.get("users")
        if MAX_USERS >= existing_users_count+len(users_id_list):
            if users_id_list:
                added_users = []
                failed_users = []
                for user_id in users_id_list:
                    try:
                        status = add_user_to_team(int(team_id), int(user_id))
                    except ValueError as ve:
                        pass
                    if status[1] == 200:
                        added_users.append(user_id)
                    else:
                        failed_users.append(user_id)

                success_users_str = ""
                if added_users:
                    success_users_str = ', '.join([str(x) for x in added_users])

                failed_users_str = ""
                if failed_users:
                    failed_users_str = ', '.join([str(x) for x in failed_users])
                
                if success_users_str and not failed_users_str:
                    return {"Users added": success_users_str}, 200
                elif failed_users_str and not success_users_str:
                    return {"Invalid users":failed_users_str}, 400
                else:
                    return {"Users added": success_users_str, "Invalid users":failed_users_str}, 200
            else:
                return {"message": "No users to add."}, 400
        else:
            remaining_users_capacity = MAX_USERS - existing_users_count
            if remaining_users_capacity:
                return {"message" : "Only " + str(remaining_users_capacity) + " user(s) can be added. Please try again."}
            else:
                return {"message" : "Team's users capacity is full."}
    else:
        return {"message" : team_obj}, 404



"""
A method to display all the teams.

:return: A JSON list with user details from DB
      Eg.
          [{  "name" : <team_name>,
              "description" : <description>,
              "admin" : <id of a user>
              "creation_time" : <date:time format>
            },
          ]
"""
def list_teams(_limit=None):
  teams_obj_list = db.session.query(Team).order_by(Team.id).limit(_limit).all()
  return serialize_objects_list(teams_obj_list)


"""
A method to get details of a single team.

:request: A JSON string with the desired team_id
      Eg. { "id" : <team_id> }

:return: A JSON string with the team details
      Eg. 
        {   "name" : <team_name>,
            "description" : <some description>,
            "creation_time" : <some date:time format>,
            "admin": <id of a user>
        }
"""
def describe_team(team_id_json):
    try: 
        team_id = int(team_id_json.get("id"))
    except ValueError as ve:
        return {"message": "TeamId should be numeric."}, 400

    team_obj = does_team_exists(team_id)
    if isinstance(team_obj, Team):
        return serialize_object(team_obj), 200
    else:
        return {"message" : team_obj}, 404


"""
A method to update team details.

:request: A JSON string with the team details
      Eg. { "id" : "<team_id>",
            "team" : {
                        "name" : <team_name>,
                        "description" : <description>,
                        "admin" : <id of a user>
                      }
          }
:return:
  Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
"""
def update_team(new_details_json):
    try: 
        team_id = int(new_details_json.get("id"))
    except ValueError as ve:
        return {"message": "TeamId should be numeric."}, 400
    new_team_name = new_details_json.get("team").get("name")
    new_team_desc = new_details_json.get("team").get("description")

    try: 
        new_team_admin = int(new_details_json.get("team").get("admin"))
    except ValueError as ve:
        return {"message": "adminId should be numeric."}, 400
    
    team_obj = does_team_exists(team_id)
    if isinstance(team_obj, Team):
        user_obj = user_resource.does_user_exists(new_team_admin)
        if isinstance(user_obj, User):
            team_obj.team_name = new_team_name
            team_obj.team_desc = new_team_desc
            team_obj.team_admin = new_team_admin
            # Saving updated team details  
            db.session.add(team_obj)
            db.session.commit()

            # Add the new admin as a team user
            add_user_to_team(team_id, new_team_admin)

            updated_team_obj = does_team_exists(team_id)
            return serialize_object(updated_team_obj), 200
        else:
            return {"message": user_obj+" Cannot be added as admin."}, 404
    else:
        return {"message" : team_obj}, 404


"""
A method to remove users to the team.

request: A JSON string with the team details
        Eg. {
                "id" : <team_id>,
                "users" : ["user_id 1", "user_id2"]
            }
:return:
        Constraint:
        * Cap the max users that can be added to 50
"""
def remove_users_from_team(team_users_json):
    try: 
        team_id = int(team_users_json.get("id"))
    except ValueError as ve:
        return {"message": "TeamId should be numeric."}, 400
    
    team_obj = does_team_exists(team_id)
    users_id_list = team_users_json.get("users")
    removed_users = []
    invalid_users = []
    if isinstance(team_obj, Team):
        if users_id_list:
            removed_users = []
            invalid_users = []
            for user_id in users_id_list:
                try:
                    user_obj = db.session.query(User).get(int(user_id))
                except ValueError as ve:
                    invalid_users.append(user_id)

                if user_obj:
                    team_admin_id = team_obj.team_admin
                    if user_obj.id == team_admin_id:
                        message = f'User {team_admin_id} is an admin & cannot be removed. To remove, update admin first.'
                        return {"error" : message, "extra": "Other users, if valid may have been removed."}, 400
                    team_user_ids = [x.id for x in team_obj.team_users]
                    if user_obj.id in team_user_ids:
                        team_obj.team_users.remove(user_obj)    # Deleteing the user from team
                        db.session.commit()
                        removed_users.append(user_id)
                    else:
                        invalid_users.append(user_id)           # For users not part of Team
                else:
                    invalid_users.append(user_id)               # For users not existing
            
            removed_users_str = ""
            if removed_users:
                removed_users_str = ', '.join([str(x) for x in removed_users])

            failed_users_str = ""
            if invalid_users:
                failed_users_str = ', '.join([str(x) for x in invalid_users])
            
            if removed_users_str and not failed_users_str:
                return {"Users removed": removed_users_str}, 200
            elif failed_users_str and not removed_users_str:
                return {"Invalid users":failed_users_str}, 400
            else:
                return {"Users removed": removed_users_str, "Invalid users":failed_users_str}, 201
        else:
            return {"message": "No users to remove."}, 400
    else:
        return {"message" : team_obj}, 404

   
"""
A method to list all users of the team.
request: A JSON string with the team details
        Eg. {
                "id" : <team_id>,
                "users" : ["user_id 1", "user_id2"]
            }
:return:
        [
          { "id" : <user_id>,
            "name" : <user_name>,
            "display_name" : <display name>
          }
        ]
"""
def list_team_users(team_id_json):
    try: 
        team_id = int(team_id_json.get("id"))
    except ValueError as ve:
        return {"message": "TeamId should be numeric."}, 400
    
    users_obj_list = User.query.join(teams_m2m_users).filter_by(team_id=team_id).all()
    return user_resource.serialize_objects_list(users_obj_list), 200
