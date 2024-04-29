# app.py
from flask import Flask, jsonify, render_template, Response, request, redirect, url_for
from facenet_pytorch import MTCNN
from deepface import DeepFace
import cv2
import time
import mysql.connector
import base64
from database import create_user, authenticate_user, get_user_age


app = Flask(__name__)

# MySQL connection configuration
mysql_connection = mysql.connector.connect(
    host="",
    port="3307",
    user="root",
    password="",
    database="database"
)

def insert_result_into_database(result):
    cursor = mysql_connection.cursor()

    # Define the MySQL query to insert the result
    insert_query = "INSERT INTO face_recognition_results (age, gender, emotion) VALUES (%s, %s, %s)"

    # Check if result is a list
    if isinstance(result, list):
        for res in result:
            age = res.get('age')
            gender = res.get('dominant_gender')
            dominant_emotion = res.get('dominant_emotion')

            # Check if all values are present
            if age is not None and gender is not None and dominant_emotion is not None:
                # Convert age to int if applicable
                try:
                    age = int(age)
                except ValueError:
                    age = None

                # Convert gender and dominant_emotion to strings
                gender = str(gender)
                dominant_emotion = str(dominant_emotion)

                # Insert data into the database
                if age is not None:
                    values = (age, gender, dominant_emotion)
                    cursor.execute(insert_query, values)
                    mysql_connection.commit()
                else:
                    print("Invalid age value, skipping insertion")
            else:
                print("Missing required data in result, skipping insertion")
    else:
        # Handle the case when result is not a list (assume it's a single dictionary)
        age = result.get('age')
        gender = result.get('gender')
        dominant_emotion = result.get('dominant_emotion')

        # Check if all values are present
        if age is not None and gender is not None and dominant_emotion is not None:
            # Convert age to int if applicable
            try:
                age = int(age)
            except ValueError:
                age = None

            # Convert gender and dominant_emotion to strings
            gender = str(gender)
            dominant_emotion = str(dominant_emotion)

            # Insert data into the database
            if age is not None:
                values = (age, gender, dominant_emotion)
                cursor.execute(insert_query, values)
                mysql_connection.commit()
            else:
                print("Invalid age value, skipping insertion")
        else:
            print("Missing required data in result, skipping insertion")

    # Commit the transaction
    mysql_connection.commit()

def save_image_to_database(image_data):
    cursor = mysql_connection.cursor()

    try:
        # Define the MySQL query to insert the image data
        insert_query = "INSERT INTO captured_images (base64_data, jpeg_data) VALUES (%s, %s)"

        # Encode the image data as base64
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')

        # Insert both base64 and JPEG data into the database
        cursor.execute(insert_query, (image_data_base64, image_data))
        mysql_connection.commit()
        print("Image saved to database successfully!")
    except mysql.connector.Error as err:
        print(f"Error saving image to database: {err}")
    finally:
        cursor.close()


def save_base64_and_image_to_database(base64_data, jpeg_data):
    cursor = mysql_connection.cursor()

    try:
        # Define the MySQL query to insert both Base64 and JPEG data
        insert_query = "INSERT INTO images (base64_data, jpeg_data) VALUES (%s, %s)"

        # Insert data into the database
        cursor.execute(insert_query, (base64_data, jpeg_data))
        mysql_connection.commit()
        print("Data saved to database successfully!")
    except mysql.connector.Error as err:
        print(f"Error saving data to database: {err}")
    finally:
        cursor.close()

def save_base64_image_and_convert_to_jpeg(base64_data):
    # Decode Base64 data back to binary
    binary_data = base64.b64decode(base64_data)
    
    # Convert binary data to JPEG format
    jpeg_data = binary_data  # In this example, we're keeping the binary data as is
    
    # Save both Base64 and JPEG data to the database
    save_base64_and_image_to_database(base64_data, jpeg_data)


# Define a global variable to track whether the video feed has finished
video_feed_finished = False

def detect_faces():
    global video_feed_finished  # Use the global variable

    video_capture = cv2.VideoCapture(0)  # Access the webcam (change to the appropriate device index if necessary)

    start_time = time.time()  # Record the start time
    while True:
        _, frame = video_capture.read()  # Read a frame from the webcam

        # Check if 5 seconds have elapsed
        if time.time() - start_time > 5:
            # Set the flag to indicate that video feed is finished
            video_feed_finished = True
            # Stop processing frames after 5 seconds
            break

        # Perform face recognition using FaceNet model of DeepFace
        result = DeepFace.analyze(frame, detector_backend='mtcnn')

        # Insert the result into MySQL database
        insert_result_into_database(result)

        # Save the image to the database
        save_image_to_database(cv2.imencode('.jpg', frame)[1].tobytes())

        # Process the result as needed
        # For example, you can print the result to the console
        print(result)

        # Encode the analyzed frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()

        # Yield the frame bytes as a response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    video_capture.release()

# Route for video feed
@app.route('/video_feed')
def video_feed():
    global video_feed_finished

    # Check if the video feed is finished
    if video_feed_finished:
        # If finished, redirect to the login page
        return redirect(url_for('login'))

    # Render the index.html template
    return render_template('index.html')

@app.route('/video_feed_data')
def video_feed_data():
    # Return the streaming video feed
    return Response(detect_faces(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if authenticate_user(username, password):
            age_input = get_user_age(username)
            if age_input is None:
                return "User age not found"
            if age_input <= 12:
                return redirect(url_for('kids'))
            else:
                return redirect(url_for('main'))
        else:
            return "Invalid username or password"
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    global video_feed_finished

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age_input = request.form['age_input']
        email = request.form['email']
        create_user(username, password, age_input, email)
        
        # Reset the video_feed_finished flag to False
        video_feed_finished = False
        
        return redirect(url_for('video_feed'))  # Redirect to the video feed page after successful registration
    
    return render_template('register.html')


@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/kids')
def kids():
    return render_template('kids.html')

if __name__ == '__main__':
    app.run(debug=True)
