import sqlite3

def intilize_db():
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()

  cursor.execute('''
  CREATE TABLE IF NOT EXISTS user (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      password TEXT,
      email TEXT
  )
  ''')
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS plants (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      userid INTEGER,
      name TEXT,
      plant_type TEXT,
      plant_location TEXT,
      plant_date TEXT,
      notes TEXT,
      feuchtigkeit TEXT,
      ai_bewässerung TEXT,
      ai_licht TEXT,
      ai_dünger TEXT,
      image TEXT
  )
  ''')
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS chats (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      userid INTEGER,
      context TEXT,
      imageids TEXT
  )
  ''')
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS chatimages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      userid INTEGER,
      chatid TEXT,
      uuid TEXT
  )
  ''')
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS statistic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER,
    plantid TEXT,
    date TEXT,
    feuchtigkeit TEXT
  )
  ''')
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS wearos_verification (
    email TEXT PRIMARY KEY,
    code TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
  )
''')

  conn.commit()
  conn.close()
  return True

if __name__ == '__main__':
  intilize_db()