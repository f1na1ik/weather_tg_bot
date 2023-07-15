import sqlite3

conn = sqlite3.connect("mydatabase_test.db")
cursor = conn.cursor()

# Создание таблицы
cursor.execute("""
CREATE TABLE IF NOT EXISTS "users" (
    "user_id"	INTEGER,
    "username"	TEXT,
    PRIMARY KEY("user_id")
)
    """)


cursor.execute("""
CREATE TABLE IF NOT EXISTS "cities" (
    "city_id"	INTEGER,
    "city_name"	TEXT,
    PRIMARY KEY("city_id")
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


# Сохраняем изменения
conn.commit()

# cursor.execute("INSERT INTO users VALUES (?, ?)", (1, 'Korjik'))
# cursor.execute("INSERT INTO users VALUES (?, ?)", (2, 'Koren'))
# cursor.execute("INSERT INTO users VALUES (?, ?)", (3, 'Mashka'))

cursor.execute("INSERT INTO cities VALUES (?, ?)", (1, 'Северодвинск'))
cursor.execute("INSERT INTO cities VALUES (?, ?)", (2, 'Архангельск'))

cursor.execute("INSERT INTO user_cities VALUES (?, ?)", (1, 1))
cursor.execute("INSERT INTO user_cities VALUES (?, ?)", (1, 2))
cursor.execute("INSERT INTO user_cities VALUES (?, ?)", (3, 2))

conn.commit()
