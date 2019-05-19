#secure_check.py
from user import User
users = [User(1,'manish','mypass'),
        User(2,'akash','akash123'),
        User(3,'abhishek','rookie69')
         ]
username_table = {u.username: u  for u in users}
userid_table = {u.id: u for u in users}

def authenticate(username,password):
         # check if user exists,if yes return user
    user = username_table.get(username,None)
    if user and password == user.password:
        return user

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id,None)
