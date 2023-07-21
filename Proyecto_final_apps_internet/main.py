from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import flash
from wtforms.csrf.session import SessionCSRF
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import jsonify
import forms
from wtforms.widgets import html_params
import sqlite3
from sqlite3 import Error
from datetime import time
from datetime import datetime
from datetime import datetime, timedelta


horarios_bd="C:\\Users\\Usuario\\Documents\\Proyecto_final_apps_internet\\static\\db\\horarios.db"


app = Flask(__name__)
app.secret_key = 'mi_clave'
csrf = SessionCSRF()
username=""
@app.route("/", methods=["GET","POST"])
def login():
    titulo = "login"
    login_form = forms.login(request.form)

    if request.method == "POST" and login_form.validate():
        # -----declaracion variables-----------#
        usuario = login_form.usuario.data.lower()
        clave = login_form.clave.data

        # -----conexión con base de datos-------#
        connect = sqlite3.connect(horarios_bd)
        cursor = connect.cursor()
        sentencia = """SELECT username, password FROM usuarios WHERE username = ?"""
        cursor.execute(sentencia, (usuario,))
        fila = cursor.fetchone()
        connect.commit()
        connect.close()
        print(fila)
        if fila:
            username, password = fila
            if password == clave and username == usuario:
                session['user'] = username
                flash('Inicio de secion exitoso', 'green')
                return redirect(url_for('registro'))
            else:
               
                flash('Usuario o contraseña incorrectos', 'red')
        else:
            
            flash('Usuario o contraseña incorrectos', 'red')

    return render_template("Login.html", titulo=titulo, form=login_form)


@app.route("/ingresar", methods=["GET","POST"])
def ingresar():
    titulo="ingresar"
    ingresar_form=forms.usuarios(request.form)
    if request.method == "POST" and ingresar_form:
        # -----declaracion variables-----------#
        nombre = ingresar_form.nombre.data
        apellido = ingresar_form.apellido.data
        cargo = ingresar_form.cargo.data
        tipo_empleado= ingresar_form.tipo_empleado.data
        salario= ingresar_form.salario.data
        descripcion=ingresar_form.descripcion.data
        password= ingresar_form.password.data

        hora_entrada_predeterm = None  # valor predeterminado
        hora_salida_predeterm = None  # valor predeterminado
        

        #-------Conexion base de datos----------#    
        connect=sqlite3.connect(horarios_bd)
        cursor= connect.cursor()
        
        global username
        username=nombre+"_"+apellido
        if tipo_empleado:
            if tipo_empleado=="obrero":
                hora_entrada_predeterm=time(7, 0, 0)
                hora_salida_predeterm= time(14, 0, 0)
                hora_entrada_predeterm=hora_entrada_predeterm.strftime('%H:%M:%S')
                hora_salida_predeterm= hora_salida_predeterm.strftime('%H:%M:%S')
            elif tipo_empleado=="empleado":
                hora_entrada_predeterm=time(8, 30, 0)
                hora_salida_predeterm= time(15, 30, 0)
                hora_entrada_predeterm=hora_entrada_predeterm.strftime('%H:%M:%S')
                hora_salida_predeterm= hora_salida_predeterm.strftime('%H:%M:%S')
              

        sentencia= (""" INSERT INTO usuarios (username, password, nombre, apellido, cargo, tipo_empleado, salario_X_hora, descripcion, hora_entrada_predeterm, hora_salida_predeterm) VALUES (?,?,?,?,?,?,?, ?, ?, ?)""" )
        
        print(nombre)
        print(apellido)
        titulo=username
        cursor.execute( sentencia, ( username, password, nombre, apellido, cargo, tipo_empleado, salario, descripcion, hora_entrada_predeterm, hora_salida_predeterm))
        connect.commit()
        connect.close()
        flash('Ingreso exitoso', 'green')
        return redirect('/')
    return render_template("usuarios.html", titulo=titulo, ingresar_form=ingresar_form)

@app.route("/registro", methods=["GET","POST"])
def registro():
    titulo = "registro"
    marcaje_form= forms.marcaje(request.form)
    

    if 'user' in session:
        username = session['user']

    if request.method == "POST" and marcaje_form:
        #conexion a base de datos
        connect=sqlite3.connect(horarios_bd)
        cursor= connect.cursor()
        sentencia1 = """SELECT hora_entrada_predeterm, hora_salida_predeterm, salario_X_hora, tipo_empleado FROM usuarios WHERE username = ?"""
        entradas=cursor.execute(sentencia1, (username,))
        resultados = entradas.fetchone()
        #Variables a usar del select
        hora_entrada_predeterminada=resultados[0]
        hora_salida_predeterminada=resultados[1]
        salario=resultados[2]
        empleado=resultados[3]



        #inicializo variables
        hora_entrada= marcaje_form.hora_entrada.data
        hora_salida= marcaje_form.hora_salida.data
        fecha_actual = datetime.now().date()
        fecha_formateada = fecha_actual.strftime("%d/%m/%Y")
        hora_entrada_=hora_entrada.strftime('%H:%M:%S')
        hora_salida_=hora_salida.strftime('%H:%M:%S')

        hora_entrada_dt = datetime.combine(fecha_actual, hora_entrada)
        hora_salida_dt = datetime.combine(fecha_actual, hora_salida)

        # Calcular la diferencia entre los dos tiempos
        diferencia = hora_salida_dt - hora_entrada_dt

        # Obtener la diferencia en formato de tiempo
        diferencia_tiempo = timedelta(seconds=diferencia.seconds)
        diferencia_tiempo_str = str(diferencia_tiempo)
        sueldo_base=salario*8.0
        total=sueldo_base

        #para empleado ejecutivo
        if empleado =="ejecutivo":
            if diferencia < timedelta(hours=8):
                flash('Error, No puedes trabajar menos de 8 horas', 'red')
                return redirect('/registro')
            elif diferencia== timedelta(hours=8):
                sentencia= (""" INSERT INTO horarios (username, fecha, hora_entrada, hora_salida, hora_trabajada, pago) VALUES (?, ?, ?, ?, ?, ?)""" )
                cursor.execute( sentencia, ( username, fecha_formateada, hora_entrada_, hora_salida_, diferencia_tiempo_str, total))
                connect.commit()
                connect.close()
                flash('Inreso exitoso', 'green')
                return redirect('/registro')
            elif diferencia>timedelta(hours=8):
                #horas extra
                diferencia_excedente=diferencia-timedelta(hours=8)
                diferencia_horas_decimal = diferencia_excedente.total_seconds() / 3600
                diferencia_formateada = "{:.2f}".format(diferencia_horas_decimal)
                diferencia_float = float(diferencia_formateada)#diferencia de horas trabajadas pero en real
                print(diferencia_float)
                hras_extras=salario*(diferencia_float*1.5)
                sueldo_base=salario*8.0
                total=hras_extras+sueldo_base
                sentencia= (""" INSERT INTO horarios (username, fecha, hora_entrada, hora_salida, hora_trabajada, pago) VALUES (?, ?, ?, ?, ?, ?)""" )
                cursor.execute( sentencia, ( username, fecha_formateada, hora_entrada_, hora_salida_, diferencia_tiempo_str, total))
                connect.commit()
                connect.close()
                flash('Inreso exitoso', 'green')
                return redirect('/registro')
            
        #para trabajador empleado    
        elif empleado=="empleado":
           if hora_entrada < time(8, 30) or hora_entrada > time(8, 40):
                print('bellaco')
                flash('No puede ingresar ya que esta entrando fuera de la hora permitida, comuníquese con recursos humanos', 'red')
                return redirect('/')
           if hora_entrada == time(8, 30):
                if diferencia < timedelta(hours=8):
                    flash('Error, No puedes trabajar menos de 8 horas', 'red')
                    return redirect('/registro')
                elif diferencia== timedelta(hours=8):
                        sentencia= (""" INSERT INTO horarios (username, fecha, hora_entrada, hora_salida, hora_trabajada, pago) VALUES (?, ?, ?, ?, ?, ?)""" )
                        cursor.execute( sentencia, ( username, fecha_formateada, hora_entrada_, hora_salida_, diferencia_tiempo_str, total))
                        connect.commit()
                        connect.close()
                        flash('Inreso exitoso', 'green')
                        return redirect('/registro')
                elif diferencia>timedelta(hours=8):
                        #horas extra
                        diferencia_excedente=diferencia-timedelta(hours=8)
                        diferencia_horas_decimal = diferencia_excedente.total_seconds() / 3600
                        diferencia_formateada = "{:.2f}".format(diferencia_horas_decimal)
                        diferencia_float = float(diferencia_formateada)#diferencia de horas trabajadas pero en real
                        print(diferencia_float)
                        hras_extras=salario*(diferencia_float*1.5)
                        sueldo_base=salario*8.0
                        total=hras_extras+sueldo_base
                        sentencia= (""" INSERT INTO horarios (username, fecha, hora_entrada, hora_salida, hora_trabajada, pago) VALUES (?, ?, ?, ?, ?, ?)""" )
                        cursor.execute( sentencia, ( username, fecha_formateada, hora_entrada_, hora_salida_, diferencia_tiempo_str, total))
                        connect.commit()
                        connect.close()
                        flash('Inreso exitoso', 'green')
                        return redirect('/registro')
                
        elif empleado=="obrero":
            if hora_entrada < time(7, 0) or hora_entrada > time(7, 20):
                print('bellaco')
                flash('No puede ingresar ya que esta entrando fuera de la hora permitida, comuníquese con recursos humanos', 'red')
                return redirect('/')
            if hora_entrada == time(8, 30):
                if diferencia < timedelta(hours=8):
                    flash('Error, No puedes trabajar menos de 8 horas', 'red')
                    return redirect('/registro')
            elif diferencia== timedelta(hours=8):
                sentencia= (""" INSERT INTO horarios (username, fecha, hora_entrada, hora_salida, hora_trabajada, pago) VALUES (?, ?, ?, ?, ?, ?)""" )
                cursor.execute( sentencia, ( username, fecha_formateada, hora_entrada_, hora_salida_, diferencia_tiempo_str, total))
                connect.commit()
                connect.close()
                flash('Inreso exitoso', 'green')
                return redirect('/registro')
            elif diferencia>timedelta(hours=8):
                #horas extra
                diferencia_excedente=diferencia-timedelta(hours=8)
                diferencia_horas_decimal = diferencia_excedente.total_seconds() / 3600
                diferencia_formateada = "{:.2f}".format(diferencia_horas_decimal)
                diferencia_float = float(diferencia_formateada)#diferencia de horas trabajadas pero en real
                print(diferencia_float)
                hras_extras=salario*(diferencia_float*1.5)
                sueldo_base=salario*8.0
                total=hras_extras+sueldo_base
                sentencia= (""" INSERT INTO horarios (username, fecha, hora_entrada, hora_salida, hora_trabajada, pago) VALUES (?, ?, ?, ?, ?, ?)""" )
                cursor.execute( sentencia, ( username, fecha_formateada, hora_entrada_, hora_salida_, diferencia_tiempo_str, total))
                connect.commit()
                connect.close()
                flash('Inreso exitoso', 'green')
                return redirect('/registro')
    return render_template("registro.html", titulo=titulo, form=marcaje_form, user=username)

@app.route("/marcas", methods=["GET","POST"])
def marcas():
    titulo = "marcas"
    marcaje_form= forms.marcaje(request.form)
    if 'user' in session:
        username = session['user']
    #conexion a base de datos
    connect=sqlite3.connect(horarios_bd)
    cursor= connect.cursor()
    sentencia1 = "SELECT * FROM horarios WHERE username = ?"
    entradas = cursor.execute(sentencia1, (username,))
    resultado = entradas.fetchall()

    """datos = []
    for fila in resultado:
        diccionario = {
            'nombre': fila[1],
            'fecha': fila[2],
            'hora_entrada': fila[3],
            'hora_salida': fila[4],
            'hora_trabajada': fila[5],
            'pago': fila[6]
        # Agrega aquí más claves y valores según las columnas de tu tabla
    }
    datos.append(diccionario)
    print(diccionario['nombre'])"""
    connect.commit()
    connect.close()
    
    return render_template("marcas.html", titulo=titulo, form=marcaje_form, user=username, vars=resultado)


if __name__ == "__main__":
	app.run(debug=True, port=5000, host="0.0.0.0")
        
        