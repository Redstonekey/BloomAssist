import os
import requests
from flask import Flask, jsonify, render_template, request, url_for, flash, session, redirect
from google import genai
from google.genai import types
import PIL.Image
import uuid
import sqlite3
import schedule
import time
import threading
from intilize_db import intilize_db
# from hardware.soil.sensor import get_water_level
# from hardware.display.display import *
intilize_db()



app = Flask('app')
app.secret_key = '23452543b4q3arttaragfd'
PLANTNET_API_KEY = '2b10K63MkVEbJpGgJBqgTrnhT'
PLANTNET_ENDPOINT = 'https://my-api.plantnet.org/v2/identify/all?api-key=' + PLANTNET_API_KEY
GEMINI_API_KEY='AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74'
instructions = " use &nl to do a new line\n'+'THIS ARE INSTRUCTIONS FROM THE BLOOM ASSIST SYSTHEM DO NOT REFER TO THIS!\nYour an Plant expert!\nNEVER SAY User: or Ai:\n "

def gemini(message, context):
  client = genai.Client(api_key=GEMINI_API_KEY)
  response = client.models.generate_content(
      model="gemini-2.0-flash",
      contents= instructions + context + '\n' + message,
  )
  return response.text


def save_water_level(water_level):
  try:
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE plants SET feuchtigkeit = ? WHERE id = 1', (water_level,))
    conn.commit()
    conn.close()
  except Exception as e:
    print(e)
  return

def ai_loop():
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()
  cursor.execute('SELECT id FROM plants')
  plants = cursor.fetchall()
  conn.close()

  for plant in plants:
    gemini_loop(plant[0])


def gemini_loop(plantid):
  loop_instructions =  'use &nl to do a new line\n'+ ' every 30 min will you be asked. '+ 'THIS ARE INSTRUCTIONS FROM THE BLOOM ASSIST SYSTHEM DO NOT REFER TO THIS!\n you can do following things: add a alert: do at the beginning of the text &alert and at the end &alert-end for the message write a short sentence between the &alert and &alert-end\n memory things: &memory and at the end &memory-end for the message write a short sentence between the &memory and &memory-end\n new calender event: &calender and at the end &calender-end for the name write a short sentence between the &calender and &calender-end and for the date do inside of the calender tags &date &date-end and for the description inside the tags &description &description-end.\n dont Write outside of these options!'
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()
  cursor.execute('SELECT * FROM plants WHERE id = ?', (plantid,))
  plant = cursor.fetchone()
  conn.close()
  if plant:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
      model="gemini-2.0-flash",
      contents= loop_instructions + '\n plant details:' + str(plant) + 'bodenfeuchtigkeit: 50%'
    )
    print(response.text)
  else:
    return 1

gemini_loop(1)


def gemini_image(img_path, message, context):
    image = PIL.Image.open(img_path)
    if img_path == 'none':
        return gemini(message, context)
    client = genai.Client(api_key="AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[instructions + context + '\n' + message, image])
    print(response.text)
    return(response.text)






@app.route('/chat', methods=['POST', 'GET'])
def ai():
    if not session.get('logged_in'):
      return redirect(url_for('login'))
    if session.get('logged_in') is False:
      return redirect(url_for('login'))
    print(session.get('logged_in'))
    if request.method == 'POST':
      message = request.form['user_input']
      session.setdefault('conversation', [])
      session['conversation'].append({'role': 'user', 'content': message})
      context = "\n".join([f"{entry['role'].capitalize()}: {entry['content']}" for entry in session['conversation']])


      file = request.files['file']
      if file:
        if file.filename != '':
            filename = file.filename or ''
            ufilename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
            filepath = os.path.join('uploads', ufilename)
            file.save(filepath)
            print(filepath)

            message = request.form['user_input']
            session['conversation'].append({'role': 'ai', 'content': message})

            
            response = gemini_image(filepath, message, context)
            session['conversation'].append({'role': 'ai', 'content': response})
            flash((response or 'Mhhh looks like that didnt work well...'))
            

            return render_template('ai-chat.html', conversation=session['conversation'])
        else:
            return 'No file selected', 400
      else:
        # session['conversation'] = []
        message = request.form['user_input']
        session['conversation'].append({'role': 'user', 'content': message})
        response = gemini(message, context)
        session['conversation'].append({'role': 'ai', 'content': response})
        flash((response or 'Mhhh looks like that didnt work well...'))
        return render_template('ai-chat.html', conversation=session['conversation'])

    else:
      return render_template('ai-chat.html', conversation=session.get('conversation', []))

# def intilize_db():
#   conn = sqlite3.connect('Bloom.db')
#   cursor = conn.cursor()

#   cursor.execute('''
#   CREATE TABLE IF NOT EXISTS user (
#       id INTEGER PRIMARY KEY AUTOINCREMENT,
#       password TEXT,
#       email TEXT
#   )
#   ''')
#   cursor.execute('''
#   CREATE TABLE IF NOT EXISTS plants (
#       id INTEGER PRIMARY KEY AUTOINCREMENT,
#       userid INTEGER,
#       name TEXT,
#       plant_type TEXT,
#       plant_location TEXT,
#       plant_date TEXT,
#       notes TEXT
#   )
#   ''')
#   cursor.execute('''
#   CREATE TABLE IF NOT EXISTS chats (
#       id INTEGER PRIMARY KEY AUTOINCREMENT,
#       userid INTEGER,
#       context TEXT,
#       imageids TEXT
#   )
#   ''')
#   cursor.execute('''
#   CREATE TABLE IF NOT EXISTS chatimages (
#       id INTEGER PRIMARY KEY AUTOINCREMENT,
#       userid INTEGER,
#       chatid TEXT,
#       uuid TEXT
#   )
#   ''')

#   conn.commit()
#   conn.close()



def add_user_to_db(password, email):
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()

  cursor.execute('''
  INSERT INTO user (password, email)
  VALUES (?, ?)
  ''', (password, email))

  conn.commit()
  conn.close()
def add_plant_to_db(userid, name, plant_type, plant_location, plant_date, notes):
  try:
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO plants (userid, name, plant_type, plant_location, plant_date, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (userid, name, plant_type, plant_location, plant_date, notes))

    conn.commit()
    conn.close()
    return 2
  except Exception as e:
    return 1


@app.route('/add-plant-to-db', methods=["POST"])
def addplanttodb():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  if session.get('logged_in') is False:
    return redirect(url_for('login'))
  
  # common-name:
  name = request.form.get('plant_name')
  # plant-type:
  plant_type = request.form.get('plant_type')
  # plant-location:
  plant_location = request.form.get('plant_location')
  # plant-date:
  plant_date = request.form.get('plant_date')
  # notes:
  notes = request.form.get('notes')
  email = session.get('email')
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()
  cursor.execute('SELECT id FROM user WHERE email = ?', (email,))
  user = cursor.fetchone()
  conn.close()
  if user:
    userid = user[0]
  else:
    flash('User not found.')
    return redirect(url_for('login'))
  if add_plant_to_db(userid, name, plant_type, plant_location, plant_date, notes) == 2:
    return 'Plant added to db'

  print(name, plant_type, plant_location, plant_date, notes)



  return ""







@app.route('/plants')
def myplants():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  
  # Get user ID from email in session
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()
  
  # First get user ID
  cursor.execute('SELECT id FROM user WHERE email = ?', (session['email'],))
  user = cursor.fetchone()
  
  if not user:
    conn.close()
    return redirect(url_for('login'))
  
  # Get all plants for this user
  cursor.execute('''
    SELECT id, name, plant_type, feuchtigkeit 
    FROM plants 
    WHERE userid = ?
  ''', (user[0],))
  
  plants = []
  for plant in cursor.fetchall():
    plants.append({
      'id': plant[0],
      'name': plant[1],
      'image_url': '/static/images/default_plant.jpg',  # You can customize this
      'moisture_status': f"{plant[3]}%" if plant[3] is not None else "Keine Messdaten!"
    })
  
  conn.close()
  return render_template('index.html', plants=plants)



@app.route('/')
def index():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  
  # Get user ID from email in session
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()
  
  # First get user ID
  cursor.execute('SELECT id FROM user WHERE email = ?', (session['email'],))
  user = cursor.fetchone()
  
  if not user:
    conn.close()
    return redirect(url_for('login'))
  
  # Get all plants for this user
  cursor.execute('''
    SELECT id, name, plant_type, feuchtigkeit 
    FROM plants 
    WHERE userid = ?
  ''', (user[0],))
  
  plants = []
  for plant in cursor.fetchall():
    plants.append({
      'id': plant[0],
      'name': plant[1],
      'image_url': '/static/images/default_plant.jpg',  # You can customize this
      'moisture_status': f"{plant[3]}%" if plant[3] is not None else "Keine Messdaten!"
    })
  
  conn.close()
  return render_template('index.html', plants=plants)


@app.route('/plant/<int:plant_id>')
def plant_detail(plant_id):
    # In a real app, you would fetch this from your database
    # This is example data
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plants WHERE id = ?', (plant_id,))
    plant_data = cursor.fetchone()
    conn.close()

    if not plant_data:
      return "Plant not found", 404

    plant = {
      'id': plant_id,
      'name': plant_data[2],  # Assuming name is the 3rd column
      'image_url': '/static/images/default_plant.jpg',
      'moisture': plant_data[7] if plant_data[7] else 0,  # Assuming feuchtigkeit is the 8th column
      'moisture_status': f"{plant_data[7]}%" if plant_data[7] else "Keine Messdaten!",
      'light': 82,
      'light_status': 'Optimale Lichtverhältnisse',
      'temperature': 23,
      'temperature_percentage': 70,
      'temperature_status': 'Ideale Temperatur',
      'watering_tip': 'Einmal pro Woche gründlich gießen. Staunässe vermeiden.',
      'light_tip': 'Benötigt viel Sonnenlicht. Mindestens 6 Stunden direktes Sonnenlicht pro Tag.',
      'fertilizer_tip': 'Alle 2 Wochen mit organischem Dünger im Frühling und Sommer.'
    }
    
    return render_template('plant_details.html', plant=plant)

@app.route('/logout')
def logout():
  session['logged_in'] = False
  return redirect(url_for('login'))
@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'POST':
    password = request.form['password']
    email = request.form['email']
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()
    if user:
      session['logged_in'] = True
      session['email'] = email
      return redirect(url_for('index'))
    else:
      flash('Invalid email or password. Please try again.')
      return render_template('login.html')

  return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def user_page():
  if request.method == 'POST':
    password = request.form['password']
    email = request.form['email']
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE email = ?', (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        flash('Email is already in use. Please use a different email.')
        return render_template('signup.html')
    else:
        add_user_to_db(password, email)
        session['logged_in'] = True
        session['email'] = email
        return redirect(url_for('index'))
  elif request.method == 'GET':
    return render_template('signup.html')
  else:
    return 'Method not allowed', 405


@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/add-plant')
def add_plant():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  if session.get('logged_in') is False:
    return redirect(url_for('login'))
  return render_template('upload_form.html')


@app.route('/user')
def user():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  if session.get('logged_in') is False:
    return redirect(url_for('login'))
  return 'USER <br><br> THIS PROJECT IS IN BETA AND THE SIDE IS NOT YET DEVELOPED <br> <a href="/">Go Back</a>'





@app.route('/identify_plant', methods=['POST', 'GET'])
def identify_plant():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  if session.get('logged_in') is False:
    return redirect(url_for('login'))
  image_file = request.files.get('image')
  if image_file:
      print('Image file received:', image_file.filename)
  else:
      print('No image file received')

  if not image_file:
      return 'no image providet!', 400

  API_KEY = "2b10K63MkVEbJpGgJBqgTrnhT"	# Your API_KEY here
  PROJECT = "all"
  api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"

  # Ensure you pass the correct format with file name, content, and type
  files = [
      ('images', (image_file.filename, image_file.stream, image_file.mimetype))
  ]

  data = {'organs': ['auto']}

  # Send the request
  response = requests.post(api_endpoint, files=files, data=data)

  if response.status_code != 200:
    return jsonify({'error': 'Failed to identify plant', 'status_code': response.status_code, 'message': response.text}), response.status_code


  json_result = response.json()

  common_names = json_result['results'][0]['species']['commonNames']

  # Das erste Element aus den gemeinsamen Namen abrufen
  first_common_name = common_names[0] if common_names else None
  # return jsonify(json_result)  
  return render_template('add-plant-details.html', common_name=first_common_name)





@app.route('/test/information', methods=['GET', 'POST'])
def test_information():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  if session.get('logged_in') is False:
    return redirect(url_for('login'))
  if request.method == 'POST':
    return 'TEST'
  return render_template('test_information.html')

    # Render the form template
def check_hardware():
  water_level = get_water_level()
  set_lcd(water_level)
  save_water_level(water_level)
  return 'Hardware checked'

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    schedule.every(30).seconds.do(lambda: ai_loop())
    schedule.every(30).seconds.do(lambda: check_hardware())
    
    # Create and start scheduler thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

# Add this before the app.run() call



if __name__ == '__main__':
  # start_scheduler()
  # check_hardware()
  app.run(host='0.0.0.0', port=8080, debug=False)


