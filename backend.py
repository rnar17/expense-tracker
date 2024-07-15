import sqlite3
from datetime import datetime


# --------------------------------------------------- backend functions for login_info database


def connect_user():
    # create/connect to login_info database
    conn = sqlite3.connect("login_info.db")
    # create cursor
    cur = conn.cursor()
    # create table of users
    cur.execute("""CREATE TABLE IF NOT EXISTS user (
                username text,
                password text
        )""")
    # commit changes
    conn.commit()
    # close database
    conn.close()


def insert_user(username, password):
    # connect to login_info database
    conn = sqlite3.connect("login_info.db")
    # create cursor
    cur = conn.cursor()
    # insert user info into table of users
    cur.execute("""INSERT INTO user VALUES (:username_info, :password_info)""",
                {
                    'username_info': username,
                    'password_info': password
                }
                )
    # commit changes
    conn.commit()
    # close database
    conn.close()


def query_user():
    # connect to login_info database
    conn = sqlite3.connect("login_info.db")
    # create cursor
    cur = conn.cursor()
    # query records from the table of users
    cur.execute("SELECT * FROM user")
    rows = cur.fetchall()
    # commit changes
    conn.commit()
    # close database
    conn.close()
    return rows

# ----------------------------------------------------------------------------------------------


# --------------------------------------------------- backend functions for login_info database

def connect_categories():
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # create table of categories
    cur.execute("""CREATE TABLE IF NOT EXISTS categories (
                user text,
                category text
                )""")
    # commit changes
    conn.commit()
    # close database
    conn.close()


def insert_category(user, category):
    # connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # insert category into table of categories
    cur.execute("INSERT INTO categories VALUES (?, ?)", (user, category))
    # commit changes
    conn.commit()
    # close database
    conn.close()


# delete expense information
def delete_category(user, category):
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # delete category with certain name, as specified by the user
    cur.execute("DELETE FROM categories WHERE user=? and category=?", (user, category))
    # commit changes
    conn.commit()
    # close database
    conn.close()


def query_categories(user):
    # connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # query records from table of categories
    cur.execute("SELECT * FROM categories WHERE user=?", (user,))
    rows = cur.fetchall()
    rows = [category[1] for category in rows]
    # commit changes
    conn.commit()
    # close database
    conn.close()
    return rows


# --------------------backend functions for expense database
def connect_expense():
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # create table of expenses
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
                user text,
                name text,
                amount real,
                category text,
                date text,
                id INTEGER PRIMARY KEY
                )""")
    # commit changes
    conn.commit()
    # close database
    conn.close()


def insert_expense(user, name, amt, category, date):
    # connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # insert expense information into expense table
    cur.execute("INSERT INTO expenses VALUES (?, ?, ?, ?, ?, NULL)",
                (user, name, amt, category, date))
    # commit changes
    conn.commit()
    # close database
    conn.close()


def query_expense(user):
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # query expenses from table of expenses
    cur.execute("SELECT * FROM expenses WHERE user=?", (user,))
    rows = cur.fetchall()
    # commit changes
    conn.commit()
    # close database
    conn.close()
    return rows


# delete expense information
def delete_expense(oid):
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # delete expense with specific id
    cur.execute("DELETE FROM expenses WHERE id=?", (oid,))
    # commit changes
    conn.commit()
    # close database
    conn.close()


def update_expense(user, name, amt, category, date, oid):
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # update expense information
    cur.execute("""UPDATE expenses SET
            user = :user,
            name = :name,
            amount = :amt,
            category = :category,
            date = :date

            WHERE oid = :oid""",
                {
                    'user': user,
                    'name': name,
                    'amt': amt,
                    'category': category,
                    'date': date,
                    'oid': oid
                })
    # commit changes
    conn.commit()
    # close database
    conn.close()


def sort_by(user, sort_method):
    if sort_method == "date-added":
        sort_method = "rowid"
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # query expenses according to sort method
    cur.execute(f"SELECT * FROM expenses WHERE user=? ORDER BY {sort_method}", (user,))
    rows = cur.fetchall()
    # commit changes
    conn.commit()
    # close database
    conn.close()
    return rows


def fetch_expenses_from(user, month, year):
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()

    if month != "All Time":
        # convert date to a suitable format
        datetime_obj = datetime.strptime(f'{year}-{month}', '%Y-%B')
        formatted_date = datetime_obj.strftime('%Y-%m')
        last_date_month = formatted_date + '-31'

        cur.execute("SELECT * FROM expenses where date >= ? and date <= ? and user=? ORDER BY date",
                    (formatted_date, last_date_month, user))
    else:
        current_year = int(year)
        next_year = current_year + 1
        current_year_obj = datetime.strptime(f'{str(current_year)}', '%Y')
        next_year_obj = datetime.strptime(f'{str(next_year)}', '%Y')
        cur.execute("SELECT * FROM expenses where date >= ? and date <= ? and user=? ORDER BY date",
                    (current_year_obj, next_year_obj, user))

    rows = cur.fetchall()
    # commit changes
    conn.commit()
    # close database
    conn.close()
    return rows

# ---------------------------------------------------


# --------------------------------------------------- backend functions for budget database
def connect_budget():
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # create table of budgets
    cur.execute("""CREATE TABLE IF NOT EXISTS budgets (
                user text,
                category text,
                amount text,
                id INTEGER PRIMARY KEY
                )""")
    # commit changes
    conn.commit()
    # close database
    conn.close()


def insert_budget(user, category, amt):
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # insert budget information into table of budgets
    cur.execute("INSERT INTO budgets VALUES (?, ?, ?, NULL)", (user, category, amt))
    # commit changes
    conn.commit()
    # close database
    conn.close()


def query_budgets(user):
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # query budgets records
    cur.execute("SELECT * FROM budgets WHERE user=?", (user,))
    rows = cur.fetchall()
    # commit changes
    conn.commit()
    # close database
    conn.close()
    return rows


def delete_budget(oid):
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # delete records with specific id
    cur.execute(f"DELETE FROM budgets WHERE id=?", (oid,))
    # commit changes
    conn.commit()
    # close database
    conn.close()


def update_budget(user, category, amt, oid):
    # create/connect to expense database
    conn = sqlite3.connect("expenses.db")
    # create cursor
    cur = conn.cursor()
    # update a record with a certain id
    cur.execute("""UPDATE budgets SET
            user = :user,
            category = :category,
            amount = :amt

            WHERE oid = :oid""",
                {
                    'user': user,
                    'category': category,
                    'amt': amt,
                    'oid': oid
                })
    # commit changes
    conn.commit()
    # close database
    conn.close()


# ---------------------------------------------------

