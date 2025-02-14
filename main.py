import os
import requests
from flask import Flask, jsonify, render_template, request, url_for, flash, session, redirect
from google import genai
from google.genai import types
import PIL.Image
import uuid
import sqlite3




app = Flask('app')
app.secret_key = '23452543b4q3arttaragfd'
PLANTNET_API_KEY = '2b10K63MkVEbJpGgJBqgTrnhT'
PLANTNET_ENDPOINT = 'https://my-api.plantnet.org/v2/identify/all?api-key=' + PLANTNET_API_KEY
GEMINI_API_KEY='AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74'

def gemini(message, context):
  client = genai.Client(api_key=GEMINI_API_KEY)
  response = client.models.generate_content(
      model="gemini-2.0-flash",
      contents='use &nl to do a new line\n'+'THIS ARE INSTRUCTIONS FROM THE BLOOM ASSIST SYSTHEM DO NOT REFER TO THIS:\nYour an Plant expert!\nNEVER SAY User: or Bot:\n' + context + '\n' + message,
  )
  return response.text


def gemini_image(img_path, message, context):
    image = PIL.Image.open(img_path)
    if img_path == 'none':
        return gemini(message, context)
    client = genai.Client(api_key="AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=["What is this image?", image])
    print(response.text)
    return(response.text)

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

  conn.commit()
  conn.close()

intilize_db()

def add_user_to_db(password, email):
  conn = sqlite3.connect('Bloom.db')
  cursor = conn.cursor()

  cursor.execute('''
  INSERT INTO user (password, email)
  VALUES (?, ?)
  ''', (password, email))

  conn.commit()
  conn.close()

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
        flash('User registered successfully.')
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

@app.route('/chat', methods=['POST', 'GET'])
def ai():
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




@app.route('/')
def index():
  return render_template('index.html')

@app.route('/add-plant')
def add_plant():
  return render_template('upload_form.html')


@app.route('/user')
def user():
  return 'USER <br><br> THIS PROJECT IS IN BETA AND THE SIDE IS NOT YET DEVELOPED <br> <a href="/">Go Back</a>'





@app.route('/identify_plant', methods=['POST', 'GET'])
def identify_plant():
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
    if request.method == 'POST':
        return 'TEST'
    return render_template('test_information.html')

    # Render the form template






@app.route('/test')
def testasdfasdf():
    return render_template('base.html')  # Render HTML-Formular



app.run(host='0.0.0.0', port=8080, debug=True)
