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
