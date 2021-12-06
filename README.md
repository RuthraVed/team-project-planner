# Team Project Planner - A Restful Team Management Tool

###### tags: `Flask` `RESTful` `SQLAlchemy` `Connexion` `Swagger` `ER Diagrma` `Many to many`

The tool consists of RESTful API's for
* Managing users
* Manging teams
* Managing a team board and tasks within a board 

## :file_cabinet: ER Diagram
![](https://i.imgur.com/rLtmfVP.png)

## Thought process
* I always begin with getting the ER Diagram correct. Once that's set, the rest of the coding part comes together automatically. 
* I started making endpoints for the entity which was less depend on others and gradually progressed to others.
* Also I made use of Swagger, which documents the API as coding progress. And so there is no need for separate documentation on how to use the API.


## :gear: Features Implemented
- [X] CRUD operations on all the four entities, i.e Team, User, Board & Task
        
- [X] Error Handling


## :wrench: Steps To Use The API

### Requirements

The project requires [Python 3.5](https://www.python.org/downloads/release/python-396/) or higher and
the [PIP](https://pip.pypa.io/en/stable/) package manager.


### Choosing a virtual environment

This step is not very important, but if one would want to isolate different Python environments, creating virtual environments is a must. I used conda's virtual.


### Install the project dependencies

Once in a virtual environment, then use pip3 to install the dependencies

`Flask-SQLAlchemy` `flask-marshmallow` `marshmallow-sqlalchemy` `marshmallow` `connexion[swagger-ui]`

Here's a one line command:
```console=1
$ pip3 install Flask-SQLAlchemy flask-marshmallow marshmallow-sqlalchemy marshmallow connexion[swagger-ui]
```

Or install dependencies from the project's requirements.txt as:
```console=1
$ pip3 install -r requirements.txt
```

:::info
**Note:** Put requirements.txt in the directory where the command will be executed. If it is in another directory, specify the path.
:::

### :pushpin: Initialize The Database
This application currently uses SQLiteDB. If needed other databases like MySql or SQLlite or MongoDB may also be used
```console=1
$ python3 db_initializer.py
```

### Finally Run Application

Run the application which will be listening on port `5000`.

```console
$ python3 app.py
```

## API Endpoints

After the app is running and the end points can be accessed using the `Swagger2.0` API documentation at:

```
http://localhost:5000/api/ui
```
