import sqlite3
import math

from app import app

def db_execute(sql):
  data = []
  try:
    with sqlite3.connect(app.config['DB_PATH'] + 'main.db') as conn:
      conn.create_function('LOG', 1, math.log)
      cursor = conn.execute(sql)
      for row in cursor:
        data.append(row)

    conn.commit()
  except sqlite3.Error as e:
    conn.rollback()
    print(e)
  finally:
    conn.close()
  return data

def list_users(column,value):
  sql = "SELECT email, given_name, family_name, b.name as user_type FROM user a INNER JOIN user_type b ON a.user_type = b.id  WHERE {} = '{}'".format(column,value)
  rows = db_execute(sql)

  users = []
  if rows != None:
    for row in rows:
      user = {
        'email'             : row[0],
        'given_name'        : row[1],
        'family_name'       : row[2],
        'user_type'         : row[3]
      }
      users.append(user)

  return users

def list_user_types():
  sql = 'SELECT id, name FROM user_type'
  rows = db_execute(sql)

  user_types = []
  for row in rows:
    user_types.append({
      'id'    : row[0],
      'name'  : row[1],
    })

  return user_types

def get_user_value(email,column):
  sql = 'SELECT {} FROM user WHERE email = "{}"'.format(column,email)
  data = db_execute(sql)
  if len(data) == 1:
    return data[0][0]
  return None

def get_user_type_id(user_type):
  sql = 'SELECT id FROM user_type WHERE name = "{}"'.format(user_type)
  data = db_execute(sql)
  if len(data) == 1:
    return data[0][0]
  return None

def upsert_user(user):
  user_type = 1
  if user['email'].endswith('@up.edu.ph'):
    user_type = 2
  if user['email'].endswith('@upou.edu.ph'):
    user_type = 3
  sql = """
          REPLACE INTO
          user (email,given_name,family_name,user_type)
          VALUES ('{email}','{given_name}','{family_name}','{user_type}')
        """.format(
          email = user['email'],
          given_name = user['given_name'],
          family_name = user['family_name'],
          user_type = user.get('user_type', user_type)
        )
  db_execute(sql)
  return list_users('email',user['email'])[0]