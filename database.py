import sqlite3

#---------------------- create tables --------------------------

def create_connection():
    conn = sqlite3.connect("mydatabase_test.db")
    return conn


def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "users" (
        "user_id"	INTEGER,
        "username"	TEXT,
        PRIMARY KEY("user_id")
    )
        """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cities (
    city_id   INTEGER,
    city_name TEXT,
    PRIMARY KEY (
        city_id AUTOINCREMENT)
    )
        """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "user_cities" (
    	"user_id"	INTEGER,
    	"city_id"	INTEGER,
    	FOREIGN KEY("city_id") REFERENCES "cities"("city_id"),
    	FOREIGN KEY("user_id") REFERENCES "users"("user_id"),
    	PRIMARY KEY("user_id","city_id")
    )
        """)
    conn.commit()

#------------------ insert functions -------------------------

def insert_user(conn, user_id, user_name):
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (user_id, user_name))
    conn.commit()


def insert_city(conn, city_name):
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO cities (city_name) VALUES (?)", [city_name])
    conn.commit()


def insert_selected_city_by_user(conn, user_id, city_id):
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO user_cities VALUES (?,?)", (user_id, city_id))
    conn.commit()


#----------------------- select functions -----------------------------

def check_city_exists(conn, city_name):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cities WHERE city_name = ?", [city_name])
    """
    Этот получает первую строку результата SQL-запроса. 
    Если запрос вернул несколько строк, fetchone() вернет только первую. 
    Если запрос не вернул ни одной строки, fetchone() вернет None.
    """
    data = cursor.fetchone()
    if data is None:
        return False #Если города нет то False
    else:
        return True #Если есть то True


def get_city_id(conn, city_name): #получение ID города когда ввели его название
    cursor = conn.cursor()
    cursor.execute("SELECT city_id FROM cities WHERE city_name = ?", [city_name])
    data = cursor.fetchone()
    if data is None:
        return False
    else:
        return data[0]

def get_user_cities(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("""SELECT cities.city_name FROM user_cities 
                   JOIN cities on user_cities.city_id = cities.city_id 
                   where user_cities.user_id = ?""", [user_id])
    data = cursor.fetchall()
    return list(city[0] for city in data)

#print(get_user_cities(create_connection(), 1945341040))

#---------------------- delete functions -------------------

def delete_selected_city_from_user(conn, user_id, city_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_cities WHERE user_id = ? AND city_id = ?", [user_id, city_id])
    conn.commit()
