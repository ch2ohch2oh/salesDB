from flask_login import UserMixin
from app import login_manager

users = {'dazhi' : '123456'}

class User(UserMixin):
    @staticmethod
    def check_password(username, password):
        if username not in users:
            return False
        return users[username] == password

@login_manager.user_loader
def user_loader(name):
    if name not in users:
        return None
    
    user = User()
    # `get_id` method of `UserMixin` class will access this `id` attribute
    # to identify the user.
    user.id = name
    user.name = name
    return user

# This enables one to login via API request. 
# We do not need this.
@login_manager.request_loader
def request_loader(request):
    pass

# https://realpython.com/using-flask-login-for-user-management-with-flask/
# https://github.com/maxcountryman/flask-login

