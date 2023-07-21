import sqlite3 

def tabla1():
    connect=sqlite3.connect("horarios.db")
    try:
        cursor= connect.cursor()
        cursor.execute(""" CREATE TABLE usuarios (
            Id integer PRIMARY KEY,
            username VARCHAR(50),
            password VARCHAR(10),
            nombre VARCHAR(10),
            apellido VARCHAR(10),
            cargo VARCHAR(70), 
            tipo_empleado VARCHAR(70), 
            salario_X_hora REAL   
            )""")
        print("se creo la tabla usuarios")  
        connect.commit()                      
    except sqlite3.OperationalError:
        print("La tabla articulos 'usuarios' ya existe")      
        connect.commit()
        connect.close()
    connect.close()


def tabla2():
    connect=sqlite3.connect('horarios.db')
    try:
        cursor= connect.cursor()
        cursor.execute(""" CREATE TABLE horarios (
            ID_horarios INTEGER PRIMARY KEY,
            username VARCHAR(50), 
            fecha DATE,
            hora_entrada TIME,
            hora_salida TIME, 
            hora_trabajada INTEGER
            )""")
        print("se creo la tabla articulos de horarios") 
        connect.commit()                       
    except sqlite3.OperationalError:
        print("La tabla articulos 'horarios' ya existe")      
        connect.commit()
        connect.close()
    connect.close()

def tabla3():
    connect=sqlite3.connect('horarios.db')
    try:
        cursor= connect.cursor()
        cursor.execute(""" CREATE TABLE tipo_empleado (
            ID_tipo_empleado INTEGER PRIMARY KEY,
            username VARCHAR(50), 
            descripcion VARCHAR(100),
            hora_entrada_predeterminada TIME,
            hora_salida_predeterminada TIME, 
            hora_trabajada INTEGER
            )""")
        connect.commit()
        print("se creo la tabla articulos de tipo_empleado")                        
    except sqlite3.OperationalError:
        print("La tabla articulos 'tipo_empleado' ya existe")      
        connect.commit()
        connect.close()
    connect.close()
    
        
tabla1()
tabla2()
tabla3()
