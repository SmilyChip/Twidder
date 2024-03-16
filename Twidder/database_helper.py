import sqlite3
import string 
import random
from flask import g

DATABASE_PATH = 'database.db'

def create_tables():
    """
    Creates all the tables in the database.

    Returns:
        True if the tables were created successfully, False otherwise.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Read the schema file and execute the SQL commands
        with open('schema.sql', 'r') as schema_file:
            schema = schema_file.read()
            cursor.executescript(schema)

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        return True
    except sqlite3.Error:
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
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
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
        
    except sqlite3.Error as e:
        return e    
    
def find_user(username):
    """
    Check if a user exists in the database.

    Args:
        username (str): The username of the user.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
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
        
    except sqlite3.Error:
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
    try:
        # Generate a random access token using a combination of letters and digits
        token_length = 25
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for _ in range(token_length))
        
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Update the access token for the user in the database
        cursor.execute("INSERT INTO tokens (token, email) VALUES (?, ?)", (token, username))
        conn.commit()
        conn.close()
        return token
    
    except sqlite3.Error as e:
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
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
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
        
    except sqlite3.Error:
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
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Insert the new user into the database
        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (email, password, firstname, familyname, gender, city, country))

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        # Registration successful
        return True
    except sqlite3.Error:
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
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Delete the token from the database
        cursor.execute("DELETE FROM tokens WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return True
     
    except sqlite3.Error:
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
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Update the user's password
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
        conn.commit()
        conn.close()
        return True
    
    except sqlite3.Error:
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
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
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
    except sqlite3.Error:
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
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
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
    except sqlite3.Error:
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
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Insert the message into the messages table
        cursor.execute("INSERT INTO messages (sender_email, receiver_email, message) VALUES (?, ?, ?)",
                       (sender_email, receiver_email, message))

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        return True
    
    except sqlite3.Error:
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
    try:
         # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Insert the message into the messages table
        cursor.execute('SELECT token FROM tokens WHERE email=?', (username,))
        user_data = cursor.fetchone()
        # Commit the changes and close the database connection
        conn.commit()
        conn.close()
        return user_data
    
    except sqlite3.Error:
        return False    

def token_pass_recover(email):
    """Generates a random pass recover token for the given username. 

    Args:
        email (str): The username for which the recover token is generated.

    Returns:
        str: The generated access token.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    try:
        # Generate a random access token using a combination of letters and digits
        token_length = 25
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for _ in range(token_length))
        
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Update the access token for the user in the database
        cursor.execute("INSERT INTO tokens_recover (token, email) VALUES (?, ?)", (token, email))
        conn.commit()
        conn.close()
        return token
    
    except sqlite3.Error as e:
        return e

def delete_token_recover(token):
    """Deletes an access token from the database.

    Args:
        token (str): The access token to be deleted.

    Returns:
        bool: True if the token was deleted successfully, False otherwise.

    Raises:
        sqlite3.Error: If an error occurs while connecting to or executing queries on the database.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Delete the token from the database
        cursor.execute("DELETE FROM tokens_recover WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return True
     
    except sqlite3.Error:
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
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
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
        
    except sqlite3.Error:
        return None
