



#!/usr/bin/env python
# coding: utf-8

# In[1]:


print("Шахматная школа — Mini App")


# In[4]:



# In[ ]:


from flask import Flask, request, session

import sqlite3

app = Flask(__name__)
app.secret_key = "chess_school_secret"
ADMIN_PASSWORD = "1234"
conn = sqlite3.connect("chess_school.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM tournaments")
rows = cursor.fetchall()

conn.close()

tournaments_list = []

for row in rows:
    tournaments_list.append({
        "id": row[0],
        "name": row[1],
        "date": row[2],
        "time": row[3],
        "rounds": row[4],
        "control": row[5],
        "max_participants": row[6]
    })

conn = sqlite3.connect("chess_school.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM participants")
rows = cursor.fetchall()

conn.close()

participants = []

for row in rows:
    participants.append({
        "id": row[0],
        "tournament_id": row[1],
        "fio": row[2],
        "birth_year": row[3],
        "fide_id": row[4],
        "rank": row[5],
        "phone": row[6]
    })

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>CHAMPION</title>

        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f7f6f3;
                text-align: center;
            }

            .container {
                max-width: 500px;
                margin: auto;
                padding: 25px 18px;
            }

            .logo {
                width: 100%;
                max-width: 360px;
                margin-bottom: 20px;
            }

            .subtitle {
                color: #777;
                font-size: 17px;
                margin-bottom: 30px;
            }

            .tournament-button {
                display: block;
                width: 100%;
                box-sizing: border-box;
                padding: 20px;
                background: #171717;
                color: white;
                text-decoration: none;
                border-radius: 18px;
                font-size: 24px;
                font-weight: bold;
                border: 2px solid #c99a4a;
                box-shadow: 0 5px 15px #ccc;
            }

            .small-text {
                display: block;
                font-size: 15px;
                font-weight: normal;
                color: #ddd;
                margin-top: 7px;
            }
        </style>
    </head>

    <body>

        <div class="container">

            <img src="/static/logo.jpeg" class="logo">

            <div class="subtitle">
                Шахматы объединяют поколения
            </div>

            <a href="/tournaments" class="tournament-button">
                🏆 ТУРНИРЫ

            </a>

        </div>

    </body>
    </html>
    """

@app.route("/tournaments")
def tournaments():
    html = "<h1>🏆 Турниры</h1>"

    if not tournaments_list:
        html += "<p>Турниров пока нет.</p>"

    for i, tournament in enumerate(tournaments_list):
        html += f"""
        <hr>
        <h2>{tournament['name']}</h2>
        <p>📅 {tournament['date']}</p>
        <p>🕐 {tournament['time']}</p>
        <p>♟ Туров: {tournament['rounds']}</p>
        <p>⏱ Контроль: {tournament['control']}</p>
        <p>👥 Участники: {sum(1 for p in participants if p["tournament_id"] == i)} / {tournament['max_participants']}</p>

        <p>
            <a href="/register/{i}">
                <button>📝 Зарегистрироваться</button>
            </a>
        </p>
        """

        if session.get("admin"):
            html += f"""
            <p>
                <a href="/participants/{i}">
                    <button>📋 Участники</button>
                </a>

                <a href="/create">
                    <button>➕ Создать турнир</button>
                </a>
            </p>
            """

    return html

@app.route("/create", methods=["GET", "POST"])
def create():
    if not session.get("admin"):
        return "<h2>❌ Доступ запрещён</h2><p>Только для администратора.</p>"

    if request.method == "POST":
        name = request.form["name"]
        date = request.form["date"]
        time = request.form["time"]
        rounds = request.form["rounds"]
        control = request.form["control"]
        max_participants = request.form["max_participants"]

        conn = sqlite3.connect("chess_school.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO tournaments
        (name, date, time, rounds, control, max_participants)
         VALUES (?, ?, ?, ?, ?, ?)
        """, (
           name,
           date,
           time,
           rounds,
           control,
           max_participants
        ))
        conn.commit()
        conn.close()

        return "Турнир сохранён! ✅"

    return """
    <h1>➕ Создание турнира</h1>

    <form method="POST">

        <p>Название турнира:</p>
        <input name="name" type="text">

        <p>Дата:</p>
        <input name="date" type="date">

        <p>Время:</p>
        <input name="time" type="time">

        <p>Количество туров:</p>
        <input name="rounds" type="number">
        <p>Максимальное количество участников:</p>
        <input name="max_participants" type="number" required>

        <p>Контроль времени:</p>
        <input name="control" type="text">

        <p>
            <button type="submit">💾 Сохранить турнир</button>
        </p>

    </form>
    """
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form["password"]

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return """
            <h1>🔐 Админ-панель</h1>
            <p>Вы вошли как администратор.</p>

            <p>
                <a href="/tournaments">
                    <button>🏆 Турниры</button>
                </a>
            </p>

            <p>
                <a href="/create">
                    <button>➕ Создать турнир</button>
                </a>
            </p>
            """

        return "<h2>❌ Неверный пароль</h2>"

    return """
    <h1>🔐 Администратор</h1>

    <form method="POST">
        <p>Введите пароль:</p>
        <input name="password" type="password">

        <p>
            <button type="submit">Войти</button>
        </p>
    </form>
    """

@app.route("/participants/<int:tournament_id>")
def show_participants(tournament_id):
    if not session.get("admin"):
        return "<h2>❌ Доступ запрещён</h2>"

    tournament = tournaments_list[tournament_id]

    conn = sqlite3.connect("chess_school.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fio, birth_year, fide_id, rank, phone
        FROM participants
        WHERE tournament_id = ?
    """, (tournament_id,))

    rows = cursor.fetchall()
    conn.close()

    html = f"<h1>👥 Участники</h1>"
    html += f"<h2>{tournament['name']}</h2>"
    html += f"<p>Всего участников: {len(rows)}</p>"

    for row in rows:
        html += f"""
        <hr>
        <p>👤 <b>{row[0]}</b></p>
        <p>🎂 Год рождения: {row[1]}</p>
        <p>♟ FIDE ID: {row[2]}</p>
        <p>🏅 Разряд: {row[3]}</p>
        <p>📞 Телефон: {row[4]}</p>
        """

    return html


@app.route("/register/<int:tournament_id>", methods=["GET", "POST"])
def register(tournament_id):

    tournament = tournaments_list[tournament_id]

    registered_count = sum(
        1 for p in participants
        if p["tournament_id"] == tournament_id
    )

    if registered_count >= int(tournament["max_participants"]):
        return """
        <h2>🔴 Регистрация закрыта</h2>
        <p>Все места на этот турнир уже заняты.</p>
        <p><a href="/tournaments">← Вернуться к турнирам</a></p>
        """

    if request.method == "POST":

        fio = request.form["fio"]
        birth_year = request.form["birth_year"]
        fide_id = request.form["fide_id"]
        rank = request.form["rank"]
        phone = request.form["phone"]

        conn = sqlite3.connect("chess_school.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO participants
        (tournament_id, fio, birth_year, fide_id, rank, phone)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
          tournament_id,
          fio,
          birth_year,
          fide_id,
          rank,
          phone
        ))

        conn.commit()
        conn.close()

        return """
        <h2>✅ Регистрация прошла успешно!</h2>
        <p><a href="/tournaments">← Вернуться к турнирам</a></p>
        """

    return f"""
    <h1>📝 Регистрация</h1>

    <h2>{tournament['name']}</h2>

    <p>👥 Свободно мест:
    {int(tournament['max_participants']) - registered_count}
    </p>

    <form method="POST">

        <p>ФИО участника:</p>
        <input type="text" name="fio" required>

        <p>Год рождения:</p>
        <input type="number" name="birth_year" required>

        <p>ID FIDE:</p>
        <input type="text" name="fide_id">

        <p>Спортивное звание / разряд:</p>
        <input type="text" name="rank">

        <p>Номер телефона:</p>
        <input type="tel" name="phone" required>

        <p>
            <button type="submit">
                ✅ Зарегистрироваться
            </button>
        </p>

    </form>

    <p>
        <a href="/tournaments">← Назад</a>
    </p>
    """


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)



# In[12]:


import sqlite3

conn = sqlite3.connect("chess_school.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date TEXT,
    time TEXT,
    rounds INTEGER,
    control TEXT,
    max_participants INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER,
    fio TEXT,
    birth_year INTEGER,
    fide_id TEXT,
    rank TEXT,
    phone TEXT
)
""")

conn.commit()
conn.close()

print("База данных создана! ✅")


# In[13]:


import sqlite3

conn = sqlite3.connect("chess_school.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

tables = cursor.fetchall()

conn.close()

print(tables)


# In[ ]:




