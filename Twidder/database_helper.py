from flask_sqlalchemy import SQLAlchemy
import string 
import random
import sqlalchemy.exc
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

DATABASE_PATH = 'database.db'
#if app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://twidder_db_user:vtPvNum8SWLWTdtaIEZ3HFZa6yHGmLnt@dpg-cnrop0i1hbls73e0l7l0-a.oregon-postgres.render.com/twidder_db':
postgreSQL = True
SQLite = False
class User(db.Model):
    __tablename__ = 'users'

    email = db.Column(db.String(120), primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    familyname = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)

class Token(db.Model):
    __tablename__ = 'tokens'

    token = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(120), db.ForeignKey('users.email'))
    
class TokenRecover(db.Model):
    __tablename__ = 'tokens_recover'

    token = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(120), db.ForeignKey('users.email'))

class Message(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String(120), db.ForeignKey('users.email'))
    receiver_email = db.Column(db.String(120), db.ForeignKey('users.email'))
    message = db.Column(db.Text, nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_email])
    receiver = db.relationship('User', foreign_keys=[receiver_email])

#else: 
#    postgreSQL = False
#    SQLite = True

def create_tables():
    """
    Creates all the tables in the database.

    Returns:
        True if the tables were created successfully, False otherwise.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Read the schema file and execute the SQL commands
            with open('schema.sql', 'r') as schema_file:
                schema = schema_file.read()
                cursor.executescript(schema)

            # Commit the changes and close the database connection
            conn.commit()
            conn.close()

            return True
        except db.Error:
            return False
    else: 
        try:   
            db.create_all()  
        except db.Error:
            return False    

def authenticate_user(username, password):
    """
    Authenticates a user using the given username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        bool: True if the authentication is successful, False otherwise.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Check if the username and password match a user in the database
            cursor.execute('SELECT firstname FROM users WHERE email=? AND password=?', (username, password))
            user_data = cursor.fetchone()

            # Close the database connection
            conn.close()

            if user_data:
                # Authentication successful, generate and return an access token
                return True
            else:
                # Authentication failed
                return False
            
        except db.Error as e:
            return e
    else: 
        try: 
            user = User.query.filter_by(email=username, password=password).first()
            return user is not None        
        except db.Error as e:
            return e
            
def find_user(username):
    """
    Check if a user exists in the database.

    Args:
        username (str): The username of the user.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Check if the username and password match a user in the database
            cursor.execute('SELECT firstname FROM users WHERE email=?', (username,))
            user_data = cursor.fetchone()

            # Close the database connection
            conn.close()

            if user_data:
                # Authentication successful, generate and return an access token
                return True
            else:
                # Authentication failed
                return False
            
        except db.Error:
            return False        
    else: 
        try:
            user = User.query.filter_by(email=username).first()
            return user is not None
        except db.Error:
            return False 
            
def generate_token(username):
    """Generates a random access token for the given username.

    Args:
        username (str): The username for which the access token is generated.

    Returns:
        str: The generated access token.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    # Generate a random access token using a combination of letters and digits
    token_length = 25
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(token_length))
    if SQLite:
        try:            
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Update the access token for the user in the database
            cursor.execute("INSERT INTO tokens (token, email) VALUES (?, ?)", (token, username))
            conn.commit()
            conn.close()
            return token
        
        except db.Error as e:
            return e
    else:
        try:
            new_token = Token(token=token, email=username)
            db.session.add(new_token)
            db.session.commit()
            return token
        except db.Error as e:
            return e
    
def token_to_email(token):
    """
    Retrieve the email associated with the given access token.

    Args:
        token (str): The access token for which the email is to be retrieved.

    Returns:
        str: The email associated with the given access token, or None if no match is found.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Retrieve the email associated with the access token
            cursor.execute("SELECT email FROM tokens WHERE token = ?", (token,))
            email = cursor.fetchone()

            # Close the database connection
            conn.close()

            if email:
                return email[0]
            else:
                return None
            
        except db.Error:
            return None
    else:
        try:    
            token_data = Token.query.filter_by(token=token).first()
            if token_data:
                return token_data.email
            else:
                return None 
        except db.Error:
            return None    

def register_user(email, password, firstname, familyname, gender, city, country):
    """
    Register a new user in the system.

    Args:
        email (str): The email address of the user.
        password (str): The password of the user.
        firstname (str): The first name of the user.
        familyname (str): The family name of the user.
        gender (str): The gender of the user (male or female).
        city (str): The city of the user.
        country (str): The country of the user.

    Returns:
        bool: True if the user was registered successfully, False otherwise.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Insert the new user into the database
            cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (email, password, firstname, familyname, gender, city, country))

            # Commit the changes and close the database connection
            conn.commit()
            conn.close()

            # Registration successful
            return True
        except db.Error:
            return False
    else: 
        try:
            new_user = User(email=email, password=password, firstname=firstname, familyname=familyname, gender=gender, city=city, country=country)
            db.session.add(new_user)
            db.session.commit()
            return True
        except db.Error:
            return False
            
def delete_token(token):
    """Deletes an access token from the database.

    Args:
        token (str): The access token to be deleted.

    Returns:
        bool: True if the token was deleted successfully, False otherwise.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Delete the token from the database
            cursor.execute("DELETE FROM tokens WHERE token = ?", (token,))
            conn.commit()
            conn.close()
            return True
        
        except db.Error:
            return False
    else: 
        try: 
            token_data = Token.query.filter_by(token=token).first()
            if token_data:
                db.session.delete(token_data)
                db.session.commit()
                return True
            else:
                return False
        except db.Error:
            return False    

def change_user_password(email, new_password):
    """
    Updates the password for the user with the given email address.

    Args:
        email (str): The email address of the user.
        new_password (str): The new password for the user.

    Returns:
        bool: True if the password was updated successfully, False otherwise.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Update the user's password
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
            conn.commit()
            conn.close()
            return True
        
        except db.Error:
            return False
    else: 
        try:
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = new_password
                db.session.commit()
                return True
            else:
                return False
        except db.Error:
            return False    
        
def get_user_data(email):
    """
    Retrieve the user data for the given email address.

    Args:
        email (str): The email address of the user.

    Returns:
        dict: A dictionary containing the user's data, or None if no user is found with the given email address.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Get the user data by email
            cursor.execute("SELECT email, firstname, familyname, gender, city, country FROM users WHERE email = ?", (email,))
            user_data = cursor.fetchone()

            # Close the database connection
            conn.close()

            if user_data:
                return {
                    'email': user_data[0],
                    'firstname': user_data[1],
                    'familyname': user_data[2],
                    'gender': user_data[3],
                    'city': user_data[4],
                    'country': user_data[5]
                }
            else:
                # User not found
                return None
        except db.Error:
            return None    
    else: 
        try: 
            user = User.query.filter_by(email=email).first()
            if user:
                return {
                    'email': user.email,
                    'firstname': user.firstname,
                    'familyname': user.familyname,
                    'gender': user.gender,
                    'city': user.city,
                    'country': user.country
                }
            else:
                return None
        except db.Error:
            return None  
        
def get_user_messages(email):
    """
    Retrieve a list of messages sent to the user with the given email address.

    Args:
        email (str): The email address of the user.

    Returns:
        List[Dict[str, str]]: A list of dictionaries, where each dictionary represents a message and contains the sender's email address and the message text. If no messages are found, an empty list is returned.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Get the user data by email
            cursor.execute("SELECT sender_email, message FROM messages WHERE receiver_email = ?", (email,))
            user_data = cursor.fetchall()

            # Close the database connection
            conn.close()

            if user_data:
                # Create a list to store dictionaries representing messages
                messages_list = []
                for sender_email, message in user_data:
                    message_dict = {'sender': sender_email, 'message': message}
                    messages_list.append(message_dict)

                return messages_list[::-1]
            
            else:
                # User has no messages
                return []
        except db.Error:
            return None    
    else: 
        try:
            # Execute the query using SQLAlchemy
            messages_data = db.session.execute("SELECT sender_email, message FROM messages WHERE receiver_email = :email", {"email": email})

            # Fetch all the results
            user_data = messages_data.fetchall()

            if user_data:
                # Create a list to store dictionaries representing messages
                messages_list = []
                for sender_email, message in user_data:
                    message_dict = {'sender': sender_email, 'message': message}
                    messages_list.append(message_dict)

                return messages_list[::-1]
            
            else:
                # User has no messages
                return []
        except Exception as e:
           return None    

def post_message(sender_email, receiver_email, message):
    """
    Post a new message to the system.

    Args:
        sender_email (str): The email address of the message sender.
        receiver_email (str): The email address of the message receiver.
        message (str): The text of the message.

    Returns:
        bool: True if the message was posted successfully, False otherwise.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Insert the message into the messages table
            cursor.execute("INSERT INTO messages (sender_email, receiver_email, message) VALUES (?, ?, ?)",
                        (sender_email, receiver_email, message))

            # Commit the changes and close the database connection
            conn.commit()
            conn.close()

            return True
        
        except db.Error:
            return False
    else: 
        try:
            # Create a new message object
            new_message = Message(sender_email=sender_email, receiver_email=receiver_email, message=message)           
            # Add the message to the database session
            db.session.add(new_message)
            # Commit the changes to the database
            db.session.commit()
            return True
        
        except Exception as e:
            return False
            
def get_first_user_token(username): 
    """
    Retrieve the first access token for the given user.

    Args:
        username (str): The username of the user.

    Returns:
        str: The first access token for the user, or None if no tokens are found.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Insert the message into the messages table
            cursor.execute('SELECT token FROM tokens WHERE email=?', (username,))
            user_data = cursor.fetchone()
            # Commit the changes and close the database connection
            conn.commit()
            conn.close()
            return user_data
        
        except db.Error:
            return False    
    else: 
        try:
            # Query the database for the first token associated with the username
            first_token = Token.query.filter_by(email=username).first()

            if first_token:
                return first_token.token
            else:
                return None
        
        except Exception as e:
            print(e)
            return None

def token_pass_recover(email):
    """Generates a random pass recover token for the given username. 

    Args:
        email (str): The username for which the recover token is generated.

    Returns:
        str: The generated access token.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    # Generate a random access token using a combination of letters and digits
    token_length = 25
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(token_length))
    if SQLite:
        try:                       
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Update the access token for the user in the database
            cursor.execute("INSERT INTO tokens_recover (token, email) VALUES (?, ?)", (token, email))
            conn.commit()
            conn.close()
            return token

        except db.Error as e:
            return e
    else: 
        try: 
            # Create a new token_recover object
            new_token = TokenRecover(token=token, email=email)
            # Add the token to the database session
            db.session.add(new_token)
            # Commit the changes to the database
            db.session.commit()
            return token
        
        except Exception as e:
            return None    

def delete_token_recover(token):
    """Deletes an access token from the database.

    Args:
        token (str): The access token to be deleted.

    Returns:
        bool: True if the token was deleted successfully, False otherwise.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Delete the token from the database
            cursor.execute("DELETE FROM tokens_recover WHERE token = ?", (token,))
            conn.commit()
            conn.close()
            return True
        
        except db.Error:
            return False
    else:
        try:
            # Query the database for the token to be deleted
            token_to_delete = TokenRecover.query.filter_by(token=token).first()
            
            if token_to_delete:
                # Delete the token from the database
                db.session.delete(token_to_delete)
                # Commit the changes to the database
                db.session.commit()        
                return True
            else:
                return False
        
        except Exception as e:
            return False
        
def token_to_email_recover(token):
    """
    Retrieve the email associated with the given recover token.

    Args:
        token (str): The access token for which the email is to be retrieved.

    Returns:
        str: The email associated with the given access token, or None if no match is found.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    if SQLite:
        try:
            # Connect to the database
            conn = db.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Retrieve the email associated with the access token
            cursor.execute("SELECT email FROM tokens_recover WHERE token = ?", (token,))
            email = cursor.fetchone()

            # Close the database connection
            conn.close()

            if email:
                return email[0]
            else:
                return None
            
        except db.Error:
            return None
    else: 
        try:
            # Query the database for the token to be deleted
            token_to_delete = TokenRecover.query.filter_by(token=token).first()
            if token_to_delete:
                # Delete the token from the database
                db.session.delete(token_to_delete)
                # Commit the changes to the database
                db.session.commit()
                return True
            else:
                return False
        
        except Exception as e:
            return False
