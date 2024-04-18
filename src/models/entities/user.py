from werkzeug.security import check_password_hash
from flask_login import UserMixin
# esta importacion permite asegurarnos de que el usuario este activo


class User(UserMixin): 

    def __init__(self, id, email, password, fullname="") -> None:
        self.id = id
        self.email = email
        self.password = password
        self.fullname = fullname
# Es un reflejo de la tabla user que hay 
# en la base de datos y sirve para manejar 
# las entidades de tipo usuario y manejar 
# la autenticacion.
    
    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)
# Un metodo que recibe dos parametros
# (password hasheado, password)
# y se utiliza sin la necesidad de instanciar la clase 
# mediante el decorador arriba indicado


