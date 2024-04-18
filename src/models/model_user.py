from .entities.user import User

class Model_user():

    @classmethod
    def login(self, db, user):
        try:
            cursor=db.connection.cursor()
            sql="""SELECT id, email, password, fullname FROM users 
                WHERE email = '{}'""".format(user.email)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                user = User(row[0], row[1], User.check_password(row[2], user.password), row[3])
                return user
            else: 
                return None
        except Exception as ex:
            raise Exception(ex)   


# Recibe 3 parametros:
# Self referencia la propio objeto
# Variable db, variable de conexion que va a ser enviada desde mi app ppal 
# User para realizar la autenticacion 

# En el Try voy a obtener (de la instancia de la clase model user, parametro user)
# el usuario para a comparar si existe en la base de datos para compara la clave
# Para esto utimo tmb (y es mas aconsejable) se puede usar un
# procedimiento almacenado creado previamente en la base datos 

# el código realiza una verificación de inicio de sesión consultando la base
# de datos y devuelve un objeto de usuario si las credenciales son válidas, 
# de lo contrario, devuelve None


    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor=db.connection.cursor()
            sql="""SELECT id, email, fullname FROM users 
                WHERE id = '{}'""".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2])
            else: 
                return None
        except Exception as ex:
            raise Exception(ex)   

# este código se utiliza para buscar un usuario en la base de datos 
# según su id y devolver una instancia de la clase User si se encuentra, 
# o None si no se encuentra.



