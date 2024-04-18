from flask import Flask, render_template, request, redirect, url_for, flash 
from werkzeug.security import generate_password_hash
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime

from config import config

# Models
from models.model_user import Model_user

# Entities
from models.entities.user import User

app = Flask(__name__)

csrf=CSRFProtect()
""" La clase CSRFProtect generalmente se utiliza en aplicaciones 
    web para proteger contra ataques de falsificación de solicitudes
    entre sitios (CSRF)."""


db = MySQL(app) 
""" En esta variable voy a tener la conexion con la cual voy a poder ejecutar
    mediante el cursor sentencias sql(seleciones, inserciones)"""


login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return Model_user.get_by_id(db, id)


# Sobre Los mensajes recibidos
# Mensaje nuevo
def all_msg():
    fullname = current_user.fullname
    cur = db.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM messages WHERE fullname = %s AND is_new = True", [fullname])
    new_msg = cur.fetchone()[0]
    cur.close()
    return new_msg


# Rutas
@app.route("/")
def index():
    return redirect(url_for('login')) 


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method =='POST':
        user = User(0, request.form['email'], request.form['password'])
        logged_user = Model_user.login(db, user)
        if logged_user != None:
            if logged_user.email == 'romina.gonzalez@yahoo.com.ar':
                if logged_user.password:
                    login_user(logged_user)
                    return redirect(url_for('home_admin'))
                else:
                    flash("Contraseña incorrecta...")
                    return render_template('auth/login.html') 
            elif logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home_users'))
            else:
                flash("Contraseña incorrecta...")
                return render_template('auth/login.html') 
        else:
            flash("Usuaria/o no encontrada...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
 

@app.route('/home_admin', methods=['GET'])
def home_admin():
    cur = db.connection.cursor()   
    cur.execute("SELECT * FROM users")
    alumnos = cur.fetchall()

    insert_object = []
    colum_names = [column [0] for column in cur.description]
    for record in alumnos:
        insert_object.append(dict(zip(colum_names, record)))
    cur.close()

    return render_template('home_admin.html', alumnos = insert_object)


@app.route('/new_user', methods=['POST'])
def new_user():
    email = request.form['email']
    password = request.form['password']
    fullname = request.form['fullname']
    inicio_plan = request.form['inicio_plan']
    finalizo_plan = request.form['finalizo_plan']

    #Genera el password hash, para pasarle el password hasheado a la bbdd
    password_hash =generate_password_hash(password)
 
    if email and password_hash and fullname:
        cur = db.connection.cursor()
        sql = """INSERT INTO users(email, password, fullname, inicio_plan, finalizo_plan)
                VALUES (%s,%s,%s,%s,%s)""" 
        data = (email, password_hash, fullname, inicio_plan, finalizo_plan)
        cur.execute(sql, data)
        db.connection.commit()
    flash("Alumna/o creada")
    return redirect(url_for('home_admin'))


@app.route('/edit_user/<int:id>/', methods=['POST'])
def edit_user(id):
    email = request.form['email']
    fullname = request.form['fullname']
    inicio_plan = request.form['inicio_plan']
    finalizo_plan = request.form['finalizo_plan']

    if email and fullname:
        cur = db.connection.cursor()
        sql = "UPDATE users SET email =%s, fullname =%s, inicio_plan =%s, finalizo_plan =%s WHERE id =%s"
        data = (email, fullname, inicio_plan, finalizo_plan, id)
        cur.execute(sql, data)
        db.connection.commit()
    return redirect(url_for('home_admin'))


@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    cur = db.connection.cursor()
    sql = "DELETE FROM users WHERE id= %s" 
    data = (id,)
    cur.execute(sql, data)
    db.connection.commit()
    flash("Alumna/o eliminada")
    return redirect(url_for('home_admin'))


@app.route('/new_message/<string:fullname>/', methods=['POST'])
def new_message(fullname):
    title = request.form['title']
    description = request.form['description']
    date = datetime.now() 
    date_message = date.strftime("%Y-%m-%d %H:%M:%S")
    is_new = 1

    if title and description:
        cur = db.connection.cursor()
        sql = "INSERT INTO messages (fullname, title, description, date_message, is_new) VALUES (%s, %s, %s, %s, %s)"
        data = (fullname, title, description, date_message, is_new)
        cur.execute(sql, data)
        db.connection.commit()
    flash("Mensaje enviado")
    return redirect(url_for('home_admin'))


@app.route('/home_users', methods=['GET'])
def home_users():
    new_msg= all_msg()
    return render_template('home_users.html', new_msg = new_msg)


@app.route('/messages_users', methods=['GET'])
def messages_users():
    fullname = current_user.fullname
    cur = db.connection.cursor()
    cur.execute("SELECT * FROM messages WHERE fullname= %s ORDER BY date_message DESC", [fullname])
    messages = cur.fetchall()

    insert_object = []
    colum_names = [column [0] for column in cur.description]
    for record in messages:
        insert_object.append(dict(zip(colum_names, record)))
    cur.close()

    return render_template('messages_users.html', messages = insert_object,) 


@app.route('/update_message<int:id>', methods=['GET'])
def update_message(id):
    cur = db.connection.cursor() 
    sql = "UPDATE messages SET is_new = 0 WHERE id = %s"
    data = (id,)
    cur.execute(sql, data)
    db.connection.commit()
    cur.close()
    return redirect(url_for('messages_users'))


@app.route('/delete_message', methods=['POST'])
def delete_message():
    cur = db.connection.cursor()
    id = request.form['id'] 
    sql = "DELETE FROM messages WHERE id = %s"
    data = (id,)
    cur.execute(sql, data)
    db.connection.commit()
    return redirect(url_for('messages_users'))


@app.route('/conscious_w', methods=['GET'])
def conscious_w():
    return render_template('conscious_w.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios atenticados.</h1>"


def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404


if __name__=='__main__':
    app.config.from_object(config['development'])
    
    """Utiliza la configuracion del otro archivo definida en un 
        diccionario. Una forma de organizar las configuraciones 
        para desarrollo."""
    
    csrf.init_app(app)

    app.register_error_handler(401,status_401)
    app.register_error_handler(404,status_404)

    """Esto es un método de Flask que permite registrar un manejador 
        de errores para un código de estado específico. Como parametros
        se pasa el codigo de estado y la funcion correspondiente"""
    app.run()