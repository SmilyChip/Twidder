from flask import Flask, jsonify, request
from email_validator import validate_email, EmailNotValidError
from flask_sock import Sock
from flask_mail import Mail, Message
import threading
from datetime import datetime, timedelta
import time
import json
import database_helper

app = Flask(__name__, static_folder='static')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'twidder0.s9pport@gmail.com'
#app.config['MAIL_PASSWORD'] = 'S0mo5_#ecQ59pport'
app.config['MAIL_PASSWORD'] = 'btyd cehb flpz gowr' 
sock = Sock(app)
mail = Mail(app)

@app.route("/")
def root():
    """
    This function is used to serve the index.html file of the web application.

    return: The index.html file of the web application.
    """
    return app.send_static_file('client.html')


@app.route('/sign_in', methods=['POST'])
def sign_in():
    """
    This function is used to sign in a user. 
    First verifies the request method (else return 405).
    Verifies if there's no missing data in the request (else return 400).
    Then verifies that the password is longer than 9 characters (else return 400).
    Then it verifies the email (else return 400) and checks if the user exists in the database (else 404).
    If the user exists, then validates the password for the given username (else 401). 
    Finally it generates an access token and returns it with 200 code. 
    If the user does not exist, it returns a 404 error. 

    parameters:
      -name: data
        -description: The data sent from the client.  
        -type: dict
      -name: username
        -description: The username of the user.
        -type: str
      -name: password
        -description: The password of the user.
        -type: str    

    responses:
      -200: Successfully signed in.
      -400: Invalid or missing data.
      -401: Wrong username or password.
      -404: User not found, wrong username.
      -405: Method not allowed (this endpoint only accepts POST requests).
      -500: Internal server error.
      -rtype: JSON
    """
    if request.method != 'POST':
        return jsonify({'message': 'Method not allowed.'}), 405
    
    data = request.get_json()
    if data is None or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Missing data or invalid request.'}), 400
    
    username = data['username']
    password = data['password']
    
    if len(password) < 9:
        return jsonify({'message': 'Invalid password length.'}), 400
    
    try:
        valid = validate_email(username, check_deliverability=False)
        if not valid:
            return jsonify({'message': 'Invalid email address.'}), 400
    except EmailNotValidError:
        return jsonify({'message': 'Invalid email address.'}), 400
    
    try:
        user_email = database_helper.find_user(username)
        if not user_email:
            return jsonify({'message': 'User not found.'}), 404
        
        user = database_helper.authenticate_user(username, password)
        if user:
            token = database_helper.generate_token(username)
            return jsonify({'message': 'Successfully signed in.', 'data': token}), 200
        else:
            return jsonify({'message': 'Wrong credentials (username/password).'}), 401
    except Exception as e:
        return jsonify({'message': 'Internal server error.', 'error': str(e)}), 500


@app.route("/sign_up", methods=['POST'])
def sign_up():
    """
    This function is used to sign up a new user. 
    First verifies the request method (else return 405).
    Verifies that there's no missing data from the request and checks if all 
    the parameters are valid (else return 400).   
    Then it tries to verify the email (else return 400) and checks if the user
    email already exists in the database (else return 409). 
    If the user does not exist, it registers the user in the database (return 201) (else return 500). 

    parameters:
      -name: data
        -description: The data sent in the request.  
        -type data: dict
      -name: email
        -description: The email of the user.
        -type: str
      -name: password
        -description: The password of the user.
        -type: str    
      -name: firstname
        -description: The first name of the user.
        -type: str
      -name: familyname
        -description: The familyname of the user.
        -type: str    
      -name: gender
        -description: The gender of the user.
        -type: str
      -name: city
        -description: The city of the user.
        -type: str    
      -name: country
        -description: The country of the user.
        -type: str    

    responses:
      -201: User registered successfully.
      -400: Invalid or missing data.
      -405: Method not allowed.
      -409: User already exists.
      -500: Internal server error.
      -rtype: JSON
    """
    if request.method != 'POST':
        return jsonify({'message': 'Method not allowed.'}), 405
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No JSON data received'}), 400

    email = data.get('email')
    password = data.get('password')
    firstname = data.get('firstname')
    familyname = data.get('familyname')
    gender = data.get('gender')
    city = data.get('city')
    country = data.get('country')

    # Validate parameters
    if not all([email, password, firstname, familyname, gender, city, country]):
        return jsonify({'message': 'Missing required fields'}), 400

    if not all(isinstance(value, str) for value in [email, password, firstname, familyname, gender, city, country]):
        return jsonify({'message': 'Invalid data format'}), 400

    if len(password) < 9:
        return jsonify({'message': 'Password too short'}), 400

    try:
        # Validate email
        valid = validate_email(email, check_deliverability=False)

        # Check if the user already exists
        if database_helper.find_user(email):
            return jsonify({'message': 'User already exists'}), 409

        # Register user
        success = database_helper.register_user(email, password, firstname, familyname, gender, city, country)
        if success:
            return jsonify({'message': 'User registered successfully'}), 201
        else:
            return jsonify({'message': 'Error creating the user'}), 500

    except EmailNotValidError:
        return jsonify({'message': 'Invalid email address'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sign_out', methods=['DELETE'])
def sign_out():
    """
    This function is used to sign out a user. 
    First verifies the request method (else return 405).
    Verifies that the token was sent (else return 401), 
    then verifies if the token is linked to a user in the database (else return 400).
    Then it deletes the token from the database (return 200).
    If there's an error deleting the token, it returns a 500 error.    

    parameters:
      -name: data
        -description: The data sent from the client.  
        -type data: dict
      -name: token
        -description: The client's token.  
        -in: header
        -type data: str
      -name: email
        -description: The client's email.  
        -type data: str

    responses:
      -200: User signed out successfully.
      -400: Incorrect token.
      -401: Token missing.
      -405: Method not allowed.
      -500: Internal server error.
      -rtype: JSON
    """
    if request.method != 'DELETE':
        return jsonify({'message': 'Method not allowed.'}), 405

    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'message': 'Token missing'}), 401

    email = database_helper.token_to_email(token)
    if not email:
        return jsonify({'message': 'Incorrect token.'}), 400

    if not database_helper.delete_token(token):
        return jsonify({'message': 'Error deleting the token'}), 500

    return jsonify({'message': 'User signed out successfully'}), 200


@app.route('/change_password', methods=['PUT'])
def change_password():
    """
    This function is used to change user's passwords. 
    First verifies the request method (else return 405).
    Verifies that the token was sent (else return 401) and 
    verifies the type and length of new password (else return 400).
    Then verifies if the token is linked to a user in the database (else return 400).
    After verifies if the credentials match (email, password) (else return 400).
    Finally changes the user's password in the database and return 200 (else return 500).

    parameters:
      -name: data
        -description: The data sent from the client.  
        -type data: dict
      -name: token
        -description: The client's token.  
        -in: header
        -type data: str
      -name: oldpassword
        -description: The client's old password.  
        -type data: str
      -name: newpassword
        -description: The client's nwe password.  
        -type data: str
              
    responses:
      -200: Password updated successfully.
      -400: Incorrect new password format or length, incorrect password.
      -401: Token missing.
      -405: Method not allowed.
      -500: Internal server error.
      -rtype: JSON
    """
    if request.method != 'PUT':
        return jsonify({'message': 'Method not allowed.'}), 405

    data = request.get_json()
    token = request.headers.get('Authorization')
    oldpassword = data.get('oldpassword')
    newpassword = data.get('newpassword')

    if not token:
        return jsonify({'message': 'Token missing'}), 401

    if not isinstance(newpassword, str) or len(newpassword) < 9:
        return jsonify({'message': 'Incorrect new password format or length'}), 400

    email = database_helper.token_to_email(token)

    if email is None:
        return jsonify({'message': 'Incorrect token'}), 401

    verify_user = database_helper.authenticate_user(email, oldpassword)

    if verify_user:
        success = database_helper.change_user_password(email, newpassword)
        if success:
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'message': 'Error changing the password'}), 500
    else:
        return jsonify({'message': 'Incorrect password'}), 400


@app.route('/get_user_data_by_token', methods=['GET'])
def get_user_data_by_token():
    """
    This function is used to retrieve user data based on the provided token.
    First verifies the request method (else return 405).
    Verifies that the token was sent (else return 401).
    Then verifies if the token is linked to a user in the database (else return 400).
    Finally gets and retrieves user's data from the database and return 200 (else return 500).

    parameters:
      -name: token
        -description: The client's token.  
        -in: header
        -type data: str
      -name: email
        -description: The client's email.  
        -type data: str
      -name: user_data
        -description: The client's data.  
        -type data: dict  

    responses:
      -200: User data retrieved successfully.
      -401: Token missing or invalid.
      -405: Method Not Allowed.
      -500: Internal Server Error.
      -rtype: JSON
    """
    if request.method != 'GET':
        return jsonify({'message': 'Method not allowed.'}), 405

    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token missing'}), 401

    email = database_helper.token_to_email(token)
    if not email:
        return jsonify({'message': 'Incorrect token.'}), 401

    user_data = database_helper.get_user_data(email)
    if user_data is not None:
        return jsonify({'message': 'User data retrieved.', 'data': user_data}), 200
    else:
        return jsonify({'message': 'Error getting user data'}), 500


@app.route('/get_user_data_by_email/<email>', methods=['GET'])
def get_user_data_by_email(email):
    """
    This function is used to retrieve user data based on the provided email.
    First verifies the request method (else return 405).
    Verifies that the token was sent (else return 401).
    Verifies that the email was sent (else return 400).
    Then verifies if the email corresponds to a user in the database (else return 404).
    Then verifies if the token is linked to the user in the database (else return 401).
    Finally gets and retrieves user's data from the database and return 200 (else return 500).

    parameters:
      -name: token
        -description: The client's token.
        -in: header  
        -type data: str
      -name: email
        -description: The client's email to get data form.  
        -in: path
        -type data: str
      -name: user_email
        -description: The client's data.  
        -type data: dict  
      -name: user_data
        -description: The client's data.  
        -type data: dict  
    
    responses:
      -200: User data retrieved successfully.
      -400: Email missing.
      -401: Unauthorized - Token missing or invalid.
      -404: Not Found - User with the provided email does not exist.
      -405: Method Not Allowed.
      -500: Internal Server Error.
      -rtype: JSON
    """
    if request.method != 'GET':
        return jsonify({'message': 'Method not allowed.'}), 405

    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token missing'}), 401

    if not email or email == 'None':
        return jsonify({'message': 'Email missing'}), 400

    is_user = database_helper.find_user(email)
    if not is_user:
        return jsonify({'message': 'User with the provided email does not exist'}), 404

    user_email = database_helper.token_to_email(token)

    if not user_email:
        return jsonify({'message': 'Incorrect token provided'}), 401

    user_data = database_helper.get_user_data(email)
    if user_data:
        return jsonify({'message': 'User data retrieved', 'data': user_data}), 200
    else:
        return jsonify({'message': 'Error retrieving data'}), 500


@app.route('/get_user_messages_by_token', methods=['GET'])
def get_user_messages_by_token():
    """
    This function is used to retrieve user messages based on the provided token.
    First verifies the request method (else return 405).
    Verifies that the token was sent (else return 401).
    Then verifies if the token is linked to a user in the database (else return 401).
    Finally gets and retrieves user's data from the database and return 200 (else return 500).

    parameters:
      -name: token
        -description: The token associated with the user.
        -in: header
        -type: str
      -name: user_email
        -description: The client's email.
        -type: str
      -name: user_messages
        -description: The client's messages.
        -type: list    

    responses:
      -200: User messages retrieved successfully.
      -401: Unauthorized - Token missing or invalid.
      -405: Method Not Allowed.
      -500: Internal Server Error.
      -rtype: JSON
    """
    if request.method != 'GET':
        return jsonify({'message': 'Method not allowed.'}), 405

    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token missing'}), 401

    user_email = database_helper.token_to_email(token)

    if not user_email:
        return jsonify({'message': 'Incorrect token provided'}), 401
    
    user_messages = database_helper.get_user_messages(user_email)

    if isinstance(user_messages, list):
        return jsonify({'message': 'User messages retrieved', 'data': user_messages}), 200
    else:
        return jsonify({'message': 'Error getting user messages'}), 500


@app.route('/get_user_messages_by_email/<email>', methods=['GET'])
def get_user_messages_by_email(email):
    """
    This function is used to retrieve user messages based on the provided email.
    First verifies the request method (else return 405).
    Verifies that the token was sent (else return 401).
    Verifies that the email was sent (else return 400).
    Then verifies if the email corresponds to a user in the database (else return 404).
    Then verifies if the token is linked to the user in the database (else return 401).
    Finally gets and retrieves user's messages from the database and return 200 (else return 500).
    
    parameters:
      -name: email
        -description: The email of the user whose messages are to be retrieved.
        -in: path
        -type: str
      -name: token
        -description: The client's token.
        -in: header
        -type: str
      -name: user_email
        -description: The client's email.
        -type: str
      -name: user_messages
        -description: The client's messages.
        -type: list

    responses:
      -200: User messages retrieved successfully.
      -400: Email missing.
      -401: Unauthorized - Token missing or invalid.
      -404: Not Found - Email does not exist.
      -405: Method Not Allowed.
      -500: Internal Server Error.
      -rtype: JSON
    """
    if request.method != 'GET':
        return jsonify({'message': 'Method Not Allowed'}), 405

    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token missing'}), 401

    if not email or email == 'None':
        return jsonify({'message': 'Email missing'}), 400

    is_user = database_helper.find_user(email)
    if not is_user:
        return jsonify({'message': 'Email does not exist'}), 404

    user_email = database_helper.token_to_email(token)

    if not user_email:
        return jsonify({'message': 'Incorrect token provided'}), 401

    user_messages = database_helper.get_user_messages(email)

    if isinstance(user_messages, list):
        return jsonify({'message': 'User messages retrieved', 'data': user_messages}), 200
    else:
        return jsonify({'message': 'Error retrieving data'}), 500


@app.route('/post_message', methods=['POST'])
def post_message():
    """
    This function is used to post a message from one user to another.
    First verifies the request method (else return 405).
    Verifies if there's no missing data in the request (else return 400).
    Then it verifies the client's email (else return 400) and checks if the 
    destination email exists in the database (else 404).
    If the user exists, then validates the password for the given username (else 401). 
    Finally it posts the message in the destination email and returns 200 code (else 500).  

    parameters:
      -name: data
        -description: The data sent from the client.  
        -type: dict
      -name: token
        -description: The client's token.
        -in: header
        -type: str
      -name: message
        -description: The client's message to post.
        -in: data
        -type: str    
      -name: email 
        -description: The email of the user.
        -in: data
        -type: str  
   
    responses:
      -201: Message posted successfully.
      -400: Bad Request - Missing required data or empty message.
      -401: Unauthorized - Incorrect token.
      -404: Email does not exist.
      -405: Method Not Allowed.
      -500: Internal Server Error.
      -rtype: JSON
    """
    if request.method != 'POST':
        return jsonify({'message': 'Method Not Allowed'}), 405

    data = request.get_json()
    token = request.headers.get('Authorization')
    message = data.get('message')
    email = data.get('email')

    # Check if token, message, and email are provided
    if not all([token, message, email]):
        return jsonify({'message': 'Missing required data'}), 400

    # Check if message is empty
    if not message.strip():
        return jsonify({'message': 'Empty message'}), 400

    # Check if token is valid
    email_from_token = database_helper.token_to_email(token)
    if email_from_token is None:
        return jsonify({'message': 'Incorrect token'}), 401
    
    # Check if receiver email exists
    if not database_helper.find_user(email):
        return jsonify({'message': 'Receiver email not found'}), 404

    # Post the message
    success = database_helper.post_message(email_from_token, email, message)
    if success:
        return jsonify({'message': 'Message posted successfully'}), 201
    else:
        return jsonify({'message': 'Error posting message'}), 500


@app.route('/recover_password', methods=['POST'])
def recover_password():
    """
    This function verifies that the email is in the data base and then sends a recovery link to that email. 
    First verifies the request method (else return 405).
    Verifies if there's no missing data in the request (else return 400).
    Then it verifies the email (else return 400) and checks if the user exists in the database (else 404).
    If the user exists, then creates a token for password recovery (else 401). 
    Finally it sends a recovery message to the user's email and returns it with 200 code. 
    If this fails, returns a 500 error. 

    parameters:
      -name: data
        -description: The data sent from the client.  
        -type: dict
      -name: username
        -description: The email of the user.
        -type: str
      -name: token
        -description: The recover password token of the user associated to email.
        -type: str    

    responses:
      -200: Email successfully sent.
      -400: Invalid or missing data.
      -404: User not found.
      -405: Method not allowed (this endpoint only accepts POST requests).
      -500: Internal server error.
      -rtype: JSON
    """
    if request.method != 'POST':
        return jsonify({'message': 'Method not allowed.'}), 405
    
    data = request.get_json()
    if data is None or 'email' not in data:
        return jsonify({'message': 'Missing data or invalid request.'}), 400
    
    username = data['email']
    
    try:
        valid = validate_email(username, check_deliverability=True)
        if not valid:
            return jsonify({'message': 'Invalid email address.'}), 400
    except EmailNotValidError:
        return jsonify({'message': 'Invalid email address.'}), 400
    
    try:
        user_email = database_helper.find_user(username)
        if not user_email:
            return jsonify({'message': 'User not found.'}), 404
        
        #creates a token and stores it in the database
        token = database_helper.token_pass_recover(username)
        if not token:
            return jsonify({'message': 'Internal server error creating token.'}), 500
    
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

    try:
      server_email = 'twidder0.s9pport@gmail.com'
      msg = Message('Recover your Twidder password', sender=server_email, recipients=[username])
      url = f'http://127.0.0.1:5000/change_password_by_email?user={token}'
      body = f'This email is used to recover your Twidder password. Please click <a href="{url}">here</a> to reset your password.'
      msg.html = body
      mail.send(msg)
    except Exception as e:
        return jsonify({'message': 'Internal server error sending email.'}), 500

    return jsonify({'message': 'Email sent succesfully'}), 200 


@app.route('/change_password_by_email')
def change_password_by_email():
    """
    This function is used to serve the recover_password.html file of the web application.

    return: The recover_password.html file of the web application.
    """
    return app.send_static_file('recover_password.html')


@app.route('/reset_password', methods=['PUT'])
def reset_password():
    """
    This function changes users password using the page sent to the user by email . 
    First verifies the request method (else return 405).
    Verifies if there's no missing data in the request (else return 400).
    Then it vinculates the user token to their email (else return 400).
    Finally it changes users password and eliminates their token and returns 200 code. 
    If this fails, returns a 500 error. 

    parameters:
      -name: data
        -description: The data sent from the client.  
        -type: dict
      -name: email
        -description: The email of the user.
        -type: str
      -name: newpassword
        -description: The new password of the user.
        -type: str
        -in: data  
      -name: token
        -description: The recover password token of the user associated to email.
        -type: str    

    responses:
      -200: Password successfully changed.
      -400: Invalid or missing data, token expired.
      -405: Method not allowed (this endpoint only accepts POST requests).
      -500: Internal server error changing password.
      -rtype: JSON
    """

    if request.method != 'PUT':
        return jsonify({'message': 'Method not allowed.'}), 405
    
    token = request.headers.get('Authorization')
    data = request.get_json()
    if data is None or 'newpassword' not in data or not token:
        return jsonify({'message': 'Missing data or token.'}), 400

    newpassword = data['newpassword']
    email = database_helper.token_to_email_recover(token)
    if not email:
        return jsonify({'message': 'token expired.'}), 400
    
    success = database_helper.change_user_password(email, newpassword)    
    if success:
        database_helper.delete_token_recover(token)    
        return jsonify({'message': 'Password changed.'}), 200
    
    return jsonify({'message': 'Error changing password.'}), 500


sessions = {}

@sock.route('/start_session')
def start_session(ws):
    """
    This function initiates a session for a WebSocket connection.
    
    Upon receiving a WebSocket connection, it continuously listens for messages from the client.
    It expects a JSON object containing user information, specifically a token.
    The token is used to retrieve the username from the database. If the token is invalid,
    it sends a message to force logout. If the token is valid, it checks if there is a previous session
    for the user. If a previous session exists, it deactivates it by sending a logout message.
    Then, it activates the current session and stores it in the sessions dictionary.

    parameters:
      - ws: WebSocket connection

    responses:
      - N/A
    """
    while ws:
        user = ws.receive()
        if user:
            data = json.loads(user)
            username = database_helper.token_to_email(data.get('user'))
            # invalid token provided
            if not username:
                first_ws.send(json.dumps({'action': 'force_logout', 'message': 'User logged in from another location.'}))
            previous_session = sessions.get(username)
            if previous_session:
                # Deactivate the previous session
                try:
                    first_ws = sessions[username][0]
                    first_ws.send(json.dumps({'action': 'logout', 'message': 'User logged in from another location.'}))
                    del sessions[username][0]
                    sessions[username] = []
                    sessions[username].append(ws)    
                    ws.send(json.dumps({'action': 'session_activated'}))    
                    print(sessions)
                except Exception as e:
                    print(e)
                    sessions[username] = []
                    sessions[username].append(ws)
                    ws.send(json.dumps({'action': 'session_activated'}))
            else:            
                sessions[username] = []
                sessions[username].append(ws)    
                ws.send(json.dumps({'action': 'session_activated'}))


# Maximum time to reconect a session (in seconds)
MAX_RECONNECT_TIME = 60

@sock.route('/connection_lost')
def handle_connection_lost(ws):
    # Get user session
    client_id = ws
    
    # Deletes user from session dictionary
    username = sessions.get(client_id)
    del sessions[username][0]

    # Check when the user disconects
    disconnected_time = datetime.now()

    # Función para verificar la reconexión del cliente
    def check_reconnection():
        while True:
            # Esperar un tiempo corto antes de verificar la reconexión
            time.sleep(3)
            # Si el cliente se reconecta, sal de la función
            if client_id in sessions:
                break
            # Verificar si ha pasado el tiempo máximo para la reconexión
            if datetime.now() - disconnected_time > timedelta(seconds=MAX_RECONNECT_TIME):
                # Get user token by email
                old_user_token = database_helper.get_first_user_token(username)
                # Force sign out from server database
                if old_user_token:
                    database_helper.delete_token(old_user_token)
                else: print('Fatal error deleting token')    
                break

    # starts a thread to check reconnection 
    threading.Thread(target=check_reconnection).start()

# Server setting
if __name__ == '__main__':
    # Creates the tables for the db
    #database_helper.create_tables()
    #app.debug = True
    #if "AZURE_POSTGRESQL_CONNECTIONSTRING" in os.environ:
    #  conn = os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"]
    #  values = dict(x.split("=") for x in conn.split(' '))
    #  user = values['user']
    #  host = values['host']
    #  database = values['dbname']
    #  password = values['password']
    #  db_uri = f'postgresql+psycopg2://{user}:{password}@{host}/{database}'
    #  app.config['SQLALCHEMY_DATABASE_URI'] = db_uri 
    #  debug_flag = False
    #else: # when running locally: use sqlite
    #  #db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    #  #db_uri = f'sqlite:///{db_path}'
    app.run(debug = False, host= "0.0.0.0")
    sock.run(app)
      
