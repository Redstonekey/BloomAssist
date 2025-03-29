import os
import requests
from flask import Flask, json, jsonify, render_template, request, url_for, flash, session, redirect
import PIL.Image
import uuid
import sqlite3
import schedule
import time
import threading
from intilize_db import intilize_db
from hardware.soil.sensor import *
from hardware.display.display import *
import jwt
from datetime import datetime, timedelta
from functools import wraps
from ai import gemini

intilize_db()

JWT_SECRET = 'idkjustsomekeyyouwant'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(days=200)

app = Flask('app')
app.secret_key = '23452543b4q3arttaragfd'
PLANTNET_API_KEY = '2b10K63MkVEbJpGgJBqgTrnhT'
PLANTNET_ENDPOINT = 'https://my-api.plantnet.org/v2/identify/all?api-key=' + PLANTNET_API_KEY
GEMINI_API_KEY='AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74'
instructions = " use &nl to do a new line\n'+'THIS ARE INSTRUCTIONS FROM THE BLOOM ASSIST SYSTHEM DO NOT REFER TO THIS!\nYour an Plant expert!\nNEVER SAY User: or Ai:\n "


# Add this decorator function to verify tokens
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user = data['email']
        except:
            return jsonify({'message': 'Token is invalid'}), 402

        return f(*args, **kwargs)
    return decorated

# def gemini.text(message, context):
#   client = genai.Client(api_key=GEMINI_API_KEY)
#   response = client.models.generate_content(
#       model="gemini-2.0-flash",
#       contents= instructions + context + '\n' + message,
#   )
#   return response.text


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

# def ai_loop():
#   conn = sqlite3.connect('Bloom.db')
#   cursor = conn.cursor()
#   cursor.execute('SELECT id FROM plants')
#   plants = cursor.fetchall()
#   conn.close()
#   for plant in plants:
#     plantid = plant[0]
#     loop_instructions =  'use &nl to do a new line\n'+ ' every 30 min will you be asked. '+ 'THIS ARE INSTRUCTIONS FROM THE BLOOM ASSIST SYSTHEM DO NOT REFER TO THIS!\n you can do following things: add a alert: do at the beginning of the text &alert and at the end &alert-end for the message write a short sentence between the &alert and &alert-end\n memory things: &memory and at the end &memory-end for the message write a short sentence between the &memory and &memory-end\n new calender event: &calender and at the end &calender-end for the name write a short sentence between the &calender and &calender-end and for the date do inside of the calender tags &date &date-end and for the description inside the tags &description &description-end.\n dont Write outside of these options!'
#     conn = sqlite3.connect('Bloom.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM plants WHERE id = ?', (plantid,))
#     plant = cursor.fetchone()
#     conn.close()
#     if plant:
#       print(gemini.text(str(plant), loop_instructions))
# ai_loop()


def gemini_image(img_path, message, context):
    image = PIL.Image.open(img_path)
    if img_path == 'none':
        return gemini.text(message, context)
    return(gemini.picture(message, img_path, context))

def ai_loop():
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()
  cursor.execute('SELECT id FROM plants')
  plants = cursor.fetchall()
  conn.close()

  for plant in plants:
    plant_loop(plant[0])
  print('-'*11)
  print('AI LOOP DONE')
  print('-'*11)
  return 'AI LOOP DONE'

def plant_loop(plantid):
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()
  cursor.execute('SELECT * FROM plants WHERE id = ?', (plantid,))
  plant = cursor.fetchone()
  conn.close()

  if not plant:
    return 'Plant not found'
  plant_info = str(plant) if isinstance(plant, tuple) else plant
  gemini.text(plant_info, 'Werte alle Informationen aus! Wenn du dringende Informationen hast antworte nur mit folgender sytax für eine Benachrichtigung beim User: &alert(alert nachricht)')
  return




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
        response = gemini.text(message, context)
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
@app.route('/add-plant-to-db', methods=["POST"])
def add_plant_to_db():
    """Handle adding a new plant with AI-generated care tips"""
    
    # Check authentication
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Get form data with default values
    plant_data = {
        'name': request.form.get('plant_name', '').strip(),
        'plant_type': request.form.get('plant_type', '').strip(),
        'plant_location': request.form.get('plant_location', '').strip(),
        'plant_date': request.form.get('plant_date', '').strip(),
        'notes': request.form.get('notes', '').strip()
    }

    # Debug print
    print("Received plant data:", plant_data)

    # Validate required fields
    if not all([plant_data['name'], plant_data['plant_type'], 
                plant_data['plant_location'], plant_data['plant_date']]):
        print("Missing required fields")  # Debug print
        flash('Please fill in all required fields')
        return redirect(url_for('add_plant'))

    try:
        # Get user ID
        conn = sqlite3.connect('Bloom.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM user WHERE email = ?', (session.get('email'),))
        user = cursor.fetchone()
        conn.close()

        if not user:
            flash('User not found')
            return redirect(url_for('login'))

        userid = user[0]

        # Generate AI care tips
        context = f"Plant Info - ID: {userid}, Name: {plant_data['name']}, Type: {plant_data['plant_type']}, " \
                 f"Location: {plant_data['plant_location']}, Date: {plant_data['plant_date']}, " \
                 f"Notes: {plant_data['notes']}. Answer always in German!"

        tips = {
            'bewässerung': gemini.text('give a tip about the following plant for the following categorie only 1 sentenc Bewässerung dont use &nl', context),
            'licht': gemini.text('give a tip about the following plant for the following categorie only 1 sentenc Lichtbedarf dont use &nl', context),
            'dünger': gemini.text('give a tip about the following plant for the following categorie only 1 sentenc Dünger dont use &nl', context)
        }

        # Save to database
        conn = sqlite3.connect('Bloom.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO plants (
                userid, name, plant_type, plant_location, plant_date, notes,
                ai_bewässerung, ai_licht, ai_dünger
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            userid, 
            plant_data['name'],
            plant_data['plant_type'],
            plant_data['plant_location'],
            plant_data['plant_date'],
            plant_data['notes'],
            tips['bewässerung'],
            tips['licht'],
            tips['dünger']
        ))
        conn.commit()
        conn.close()
        
        flash('Plant added successfully!')
        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
        flash(f'Error occurred: {str(e)}')
        return redirect(url_for('add_plant'))



@app.route('/my-plants')
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
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()
    
    # Fetch plant details
    plant = cursor.execute('''
      SELECT * FROM plants WHERE id = ?
    ''', (plant_id,)).fetchone()
    
    # Fetch last 7 days of statistics
    stats = cursor.execute('''
      SELECT date, feuchtigkeit 
      FROM statistic 
      WHERE plantid = ? 
      ORDER BY date DESC 
      LIMIT 7
    ''', (plant_id,)).fetchall()
    
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
      'watering_tip': plant_data[8],
      'light_tip': plant_data[9],
      'fertilizer_tip': plant_data[10]
    }
        # Prepare data for the chart
    dates = [stat[0] for stat in stats][::-1]  # Reverse to show chronological order
    moisture_data = [float(stat[1]) for stat in stats][::-1]
    
    return render_template('plant_details.html',
      plant=plant,
      dates=json.dumps(dates),
      moisture_data=json.dumps(moisture_data)
     )

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

@app.route('/delete/<int:plant_id>', methods=['GET'])
def delete_plant(plant_id):
  if not session.get('logged_in'):
    return redirect(url_for('login'))
    
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()
  
  # Verify the plant belongs to the logged in user
  cursor.execute('''
    SELECT userid FROM plants 
    WHERE id = ?
  ''', (plant_id,))
  plant = cursor.fetchone()
  
  if not plant:
    conn.close()
    flash('Plant not found')
    return redirect(url_for('index'))
    
  # Get user ID for logged in user
  cursor.execute('SELECT id FROM user WHERE email = ?', (session['email'],))
  user = cursor.fetchone()
  
  if not user or plant[0] != user[0]:
    conn.close() 
    flash('Not authorized to delete this plant')
    return redirect(url_for('index'))
  
  # Delete plant
  cursor.execute('DELETE FROM plants WHERE id = ?', (plant_id,))
  conn.commit()
  conn.close()
  return redirect(url_for('index'))

# ------------------------------------------
#             !API ROUTES!
# ------------------------------------------

@app.route('/api/login', methods=['POST'])
def api_login():
    if request.method == 'POST':
        data = request.get_json()
        password = data.get('password')
        email = data.get('email')
        
        conn = sqlite3.connect('Bloom.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Generate token
            token = jwt.encode({
                'email': email,
                'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA
            }, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            return jsonify({
                'success': True,
                'email': email,
                'token': token,
                'message': 'Login successful',
                'code': 1
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials',
                'code': 2
            }), 401
    return redirect(url_for('index'))

@app.route('/api/signup', methods=['POST'])
def api_signup():
    if request.method == 'POST':
        data = request.get_json()
        password = data.get('password')
        email = data.get('email')

        conn = sqlite3.connect('Bloom.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Email already exists',
                'code': 2
            }), 409
        else:
            add_user_to_db(password, email)
            conn.close()
            
            # Generate token for the new user
            token = jwt.encode({
                'email': email,
                'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA
            }, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            return jsonify({
                'success': True,
                'email': email,
                'token': token,
                'message': 'Signup successful',
                'code': 1
            }), 201
    return redirect(url_for('index'))



@app.route('/api/delete/<plantid>', methods=['DELETE'])
@token_required
def api_delete(plantid):  
  # Get email from token
  token = request.headers['Authorization'].replace('Bearer ', '')
  try:
    token_data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    email = token_data['email']
    print(email)
    print('-'*50) 
  except:
    return jsonify({'success': False, 'message': 'Invalid token', 'code': 4}), 401
  
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()
  
  # Verify the plant belongs to the logged in user
  cursor.execute('''
    SELECT userid FROM plants 
    WHERE id = ?
  ''', (plantid,))
  plant = cursor.fetchone()
  
  if not plant:
    conn.close()
    return jsonify({
    'success': False,
    'plantid': plantid,
    'message': 'Plant doesnt exist',
    'code': 3 
    })
    
  # Get user ID for token user
  cursor.execute('SELECT id FROM user WHERE email = ?', (email,))
  user = cursor.fetchone()
  
  if not user or plant[0] != user[0]:
    conn.close() 
    return jsonify({
    'success': False,
    'plantid': plantid,
    'message': 'You dont have Permission for that!',
    'code': 2 
    })
  
  # Delete plant
  cursor.execute('DELETE FROM plants WHERE id = ?', (plantid,))
  conn.commit()
  conn.close()

  return jsonify({
    'success': True,
    'plantid': plantid,
    'message': 'Plant deleted successfully',
    'code': 1
  }), 201

@app.route('/api/getplants', methods=['GET'])
@token_required
def api_get_plants():
  # Get email from token
  token = request.headers['Authorization'].replace('Bearer ', '')
  try:
    token_data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    email = token_data['email']
  except:
    return jsonify({'success': False, 'message': 'Invalid token', 'code': 4}), 401

  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()

  # Get user ID
  cursor.execute('SELECT id FROM user WHERE email = ?', (email,))
  user = cursor.fetchone()

  if not user:
    conn.close()
    print('User not found')
    return jsonify({'success': False, 'message': 'User not found', 'code': 3}), 404

  # Get all plants for this user
  cursor.execute('''
    SELECT id, name, plant_type, plant_location, plant_date, feuchtigkeit, 
          ai_bewässerung, ai_licht, ai_dünger, notes
    FROM plants 
    WHERE userid = ?
  ''', (user[0],))

  plants = []
  for plant in cursor.fetchall():
    print(plant)
    plants.append({
      'id': plant[0],
      'name': plant[1],
      'type': plant[2],
      'location': plant[3],
      'date': plant[4],
      'moisture': plant[5],
      'watering_tip': plant[6],
      'light_tip': plant[7],
      'fertilizer_tip': plant[8],
      'notes': plant[9]
    })

  conn.close()
  print('Plants retrieved successfully')
  return jsonify({
    'success': True,
    'plants': plants,
    'message': 'Plants retrieved successfully',
    'code': 1
  }), 200

@app.route('/api/add-plant', methods=['POST'])
@token_required
def api_add_plant():
  # Get email from token
  token = request.headers['Authorization'].replace('Bearer ', '')
  try:
    token_data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    email = token_data['email']
  except:
    return jsonify({'success': False, 'message': 'Invalid token', 'code': 4}), 401

  # Get JSON data
  data = request.get_json()
  if not data:
    return jsonify({'success': False, 'message': 'No data provided', 'code': 3}), 400

  # Extract plant data
  plant_data = {
    'name': data.get('name', '').strip(),
    'plant_type': data.get('plant_type', '').strip(),
    'plant_location': data.get('plant_location', '').strip(), 
    'plant_date': data.get('plant_date', '').strip(),
    'notes': data.get('notes', '').strip()
  }

  # Validate required fields
  if not all([plant_data['name'], plant_data['plant_type'], 
        plant_data['plant_location'], plant_data['plant_date']]):
    return jsonify({'success': False, 'message': 'Missing required fields', 'code': 2}), 400

  try:
    # Get user ID
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM user WHERE email = ?', (email,))
    user = cursor.fetchone()

    if not user:
      conn.close()
      return jsonify({'success': False, 'message': 'User not found', 'code': 3}), 404

    userid = user[0]

    # Generate AI care tips
    context = f"Plant Info - Name: {plant_data['name']}, Type: {plant_data['plant_type']}, " \
          f"Location: {plant_data['plant_location']}, Date: {plant_data['plant_date']}, " \
          f"Notes: {plant_data['notes']}. Answer always in German!"

    tips = {
      'bewässerung': gemini.text('give a tip about the following plant for the following categorie only 1 sentenc Bewässerung', context),
      'licht': gemini.text('give a tip about the following plant for the following categorie only 1 sentenc Lichtbedarf', context),
      'dünger': gemini.text('give a tip about the following plant for the following categorie only 1 sentenc Dünger', context)
    }

    # Save to database
    cursor.execute('''
      INSERT INTO plants (
        userid, name, plant_type, plant_location, plant_date, notes,
        ai_bewässerung, ai_licht, ai_dünger
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
      userid,
      plant_data['name'],
      plant_data['plant_type'],
      plant_data['plant_location'],
      plant_data['plant_date'],
      plant_data['notes'],
      tips['bewässerung'],
      tips['licht'],
      tips['dünger']
    ))
    
    plant_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
      'success': True,
      'plant_id': plant_id,
      'message': 'Plant added successfully',
      'code': 1
    }), 201

  except Exception as e:
    return jsonify({'success': False, 'message': str(e), 'code': 5}), 500

@app.route('/api/wearos/login', methods=['POST'])
def api_wearos_login():
  data = request.get_json()
  verification_code = str(uuid.uuid4())[:6]  # Generate 6-digit code
  
  try:
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()
    
    # Store verification code temporarily
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS wearos_verification (
        email TEXT PRIMARY KEY,
        code TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    ''')
    
    cursor.execute('''
      INSERT OR REPLACE INTO wearos_verification (email, code)
      VALUES (?, ?)
    ''', (data.get('email'), verification_code))
    
    conn.commit()
    conn.close()
    
    return jsonify({
      'success': True,
      'verification_code': verification_code,
      'message': 'Enter this code in your mobile app',
      'code': 1
    }), 200
    
  except Exception as e:
    return jsonify({
      'success': False, 
      'message': str(e),
      'code': 2
    }), 500

@app.route('/api/wearos/verify', methods=['POST']) 
def api_wearos_verify():
  data = request.get_json()
  email = data.get('email')
  code = data.get('code')
  
  try:
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()
    
    # Check verification code
    cursor.execute('''
      SELECT code FROM wearos_verification 
      WHERE email = ? AND 
          datetime(timestamp) > datetime('now', '-5 minutes')
    ''', (email,))
    
    stored_code = cursor.fetchone()
    
    if not stored_code or stored_code[0] != code:
      conn.close()
      return jsonify({
        'success': False,
        'message': 'Invalid or expired code',
        'code': 2
      }), 401
      
    # Delete used verification code
    cursor.execute('DELETE FROM wearos_verification WHERE email = ?', (email,))
    conn.commit()
    conn.close()
    
    # Generate auth token
    token = jwt.encode({
      'email': email,
      'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA
    }, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return jsonify({
      'success': True,
      'token': token,
      'message': 'WearOS device verified successfully',
      'code': 1
    }), 200
    
  except Exception as e:
    return jsonify({
      'success': False,
      'message': str(e),
      'code': 3
    }), 500
  

def save_water_level_statistic(water_level_n_save):
  try:
    conn = sqlite3.connect('Bloom.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO statistic (userid, plantid, date, feuchtigkeit)
    VALUES (1, 1, datetime('now'), ?)
    ''', (water_level_n_save,))
    conn.commit()
    conn.close()
  except Exception as e:
    print(e)
  return 


    # Render the form template
def check_hardware():
  water_level_status, water_level_n = get_water_level() # type: ignore
  set_lcd(water_level_status, water_level_n) # type: ignore
  water_level_n_save = water_level_n * 10
  save_water_level(water_level_n_save)
  save_water_level_statistic(water_level_n_save)
  return

def run_scheduler():
    while True:
      schedule.run_pending()
      time.sleep(1)

def start_schedule():
  schedule.every(15).seconds.do(lambda: check_hardware())
  schedule.every(2).minutes.do(lambda: ai_loop())
  scheduler_thread = threading.Thread(target=run_scheduler)
  scheduler_thread.daemon = True
  scheduler_thread.start()
if __name__ == '__main__':
  debug = True
  start_schedule()
  app.run(host='0.0.0.0', port=8080, debug=False) 