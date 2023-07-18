import os
from flask import Flask, flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

from werkzeug.utils import secure_filename
from pathlib import Path
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
from backend import *
import json
from PIL import Image, ImageDraw
from google.cloud import datastore
from flask_bcrypt import Bcrypt
import constants

from datetime import date, datetime
import io

import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../keys/posture-analysis-391020-95adb2ea5a9a.json'


UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'dflskfdlTKRGvfkg64tfrf65tgy88jDFGDgFDFsfw43'
bcrypt = Bcrypt(app)
datastore_client = datastore.Client()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def root():
    return render_template("index.j2")

@app.route('/home')
def home():
    return render_template("home.j2")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate form data
        if not username or not password or not confirm_password:
            flash('All fields are required.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        else:
            # Check if username already exists
            query = datastore_client.query(kind=constants.user)
            users = list(query.fetch())
            for user in users:
                if user['username'] == username:
                    flash('Username is already taken.', 'error')
                    return render_template('index.j2')
            else:
                # Store the user in the database (replace with your actual user model storage)
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                new_user = datastore.entity.Entity(key=datastore_client.key(constants.user))
                new_user.update({'username': username, 'password': hashed_password, 'results': []})
                datastore_client.put(new_user)
                
                session["user"] = new_user.key.id
                flash('Account created successfully.', 'success')
                return redirect('/home')

    return render_template('index.j2')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user in the database (replace with your actual user model retrieval)
        query = datastore_client.query(kind=constants.user)
        users = list(query.fetch())
        for user in users:
            if user['username'] == username and bcrypt.check_password_hash(user['password'], password):
        #user = next((user for user in users if user['username'] == username), None)
        #if user and bcrypt.check_password_hash(user['password'], password):
            # User authenticated, perform login
            # ...

                session["user"] = user.key.id
                flash('Logged in successfully.', 'success')
                return redirect('/home')
            else:
                flash('Invalid username or password.', 'error')

    return render_template('index.j2')

# logs user out and clears session data
@app.route("/logout")
def logout():
    session.clear()
    render_template('index.j2')
    
@app.route('/new_user')
def new_user():
    return render_template("new_user.j2")

from PIL import Image, ImageDraw

@app.route('/analyze', methods=['POST','GET'])
def analyze():
    # Get the uploaded image file and coordinates from the form
    image_file = request.files['image']
    coordinates = request.form.get('coordinateJSON')

    # Process the image and draw lines
    image = Image.open(image_file)
    draw = ImageDraw.Draw(image)
    # Convert the coordinates JSON string to a dictionary
    coordinate_dict = json.loads(coordinates)
    # Draw lines using the coordinates
    
    count = 0
    for position, coordinate in coordinate_dict.items():
        if count == 0:
            x1, y1 = coordinate
            count = 1
            continue
        # Customize line drawing parameters (e.g., color, thickness, etc.)
        x2, y2 = coordinate
        draw.line([(x1, y1), (x2, y2)], fill='red', width=2)
        x1 = x2
        y1= y2

    # Save the merged image to a file or in-memory buffer
    merged_image_path = 'static/images/image.jpg'
    
    # Check if the image has an alpha channel
    if image.mode == 'RGBA':
        # Convert the image to RGB mode for JPEG format
        merged_image = image.convert('RGB')
        # Save as JPEG
        merged_image.save(merged_image_path, 'JPEG')
    else:
        # Save as PNG
        image.save(merged_image_path, 'PNG')

    asjson = json.loads(coordinates)
    results = get_results(asjson)
    issues = results['issues']
    angleDict = results['angleDict']
    

    my_dict = {
        'Name': ('John Doe', "now"),
        'Age': (30, 43),
        'Country': ('USA', 'canada')
    }


    return render_template("new_user_results.j2", image_path=merged_image_path, issues=issues, angleDict=angleDict)


@app.route('/save_user_upload', methods=['POST','GET'])
def save_upload():
    user_id = session['user']
    user_key = datastore_client.key(constants.user, int(user_id))
    user = datastore_client.get(key=user_key)
   
    saved_image = request.form.get('saved_image')
    issue = request.form.get("issues")
    issues = eval(issue)
    angleDic = request.form.get('angleDict')
    angleDict = eval(angleDic)

    
    user['results'].append({"date": str(date.today()), "issues": issues, "angleDict": angleDict})
    #new_data.update({"date": str(date.today()), "issues": issues, "angleDict": angleDict})
    datastore_client.put(user)

    #boat_key = datastore_client.key(constants.user_data, int(new_data.key.id))
    #boat = datastore_client.get(key=boat_key)

    return render_template("new_user_results.j2", image_path=saved_image, issues=issues, angleDict=angleDict)




@app.route('/saved_data', methods=['GET'])
def get_saved_data():
    user_id = session['user']
    user_key = datastore_client.key(constants.user, int(user_id))
    user = datastore_client.get(key=user_key)
    results = user['results']
    

    a = results

    """a = []
    for i in range(len(b)):
        if len(a) == 0:
            a.append(b[i])
            continue
        index = 0
       
        for e in range(len(a)):
            if compareDates(b[i-1]['date'], b[i]['date']) > 0:
                index += 1 
            else: break
       
        a.insert(index, b[i])"""
    
    """for i in range(len(b)):
        if len(a) == 0:
            a.append(b[i])
            continue
        index = 0
        while compareDates(b[i]['date'], b[i-1]['date']) > 0:
            index += 1
        a.insert(index, b[i])"""

    
    neckAngles = []
    hipAngles = []
    backAngles = []
    dates = []
    # make 3 arrays for each attribute
    for result in a:
        angleDict = result['angleDict']
        back = angleDict['back']
        neck = angleDict['neck']
        hip = angleDict['hip']
        date = result['date']
      
        print(hip)

        index = 0
        for i in range(len(dates)):
            print(index)
            if compareDates(date, dates[i]) > 0:
                index += 1
            else:
                break
        
        neckAngles.insert(index, neck)
        backAngles.insert(index, back)
        hipAngles.insert(index, hip)
        dates.insert(index, date)

    
    

    # Save the graph image to a BytesIO object
    x = []
    for i in range(1, len(dates) + 1):
        x.append(i*2)
    y = hipAngles
    
    print(y)
    print(x)
    

    plt.plot(x, y)
   
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Hip')
    # Set the x-axis tick labels to the values from the dates array
    plt.xticks(x, dates)

    # Save the graph to a file
    graph_filename = 'static/graphs/hip_graph.png'
    plt.savefig(graph_filename)
    plt.close()


    ##################### back ############
    y = backAngles
    

    plt.plot(x, y)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('back')
    # Set the x-axis tick labels to the values from the dates array
    plt.xticks(x, dates)

    # Save the graph to a file
    graph_filename = 'static/graphs/back_graph.png'
    plt.savefig(graph_filename)
    plt.close()

    #################### neck

    y = neckAngles
    

    plt.plot(x, y)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('neck')
    # Set the x-axis tick labels to the values from the dates array
    plt.xticks(x, dates)

    # Save the graph to a file
    graph_filename = 'static/graphs/neck_graph.png'
    plt.savefig(graph_filename)
    plt.close()
   
    
   
    return render_template("saved_data.j2", results=a)



def generate_graph():
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    plt.plot(x, y)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Graph Title')
    return plt

def compareDates(date1_str, date2_str):
    date1 = datetime.strptime(date1_str, '%Y-%m-%d')
    date2 = datetime.strptime(date2_str, '%Y-%m-%d')
    if date1 > date2:
        return 1 
    return 0

def getDays(date1_str, date2_str):
    date_format = '%Y-%m-%d'

    # Convert date strings to datetime objects
    date1 = datetime.strptime(date1_str, date_format)
    date2 = datetime.strptime(date2_str, date_format)

    # Calculate the timedelta between the dates
    delta = date1 - date2

    # Get the number of days
    num_days = delta.days

    return num_days

@app.route('/delete_result', methods=['POST'])
def delete_result():
    data_id = request.form.get('data_id')
    print(data_id)

    data_key = datastore_client.key(constants.user_data, int(data_id))
    data = datastore_client.get(key=data_key)
    datastore_client.delete(data)

    return get_saved_data()


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9112)) 
    app.run(port=port)