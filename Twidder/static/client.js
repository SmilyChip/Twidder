window.onload = function(){
    if (has_loggedin()) {
            display_profile_view();
    }
    else {
        display_welcome_view();
    }
}
//----------------------------Socket code----------------------------
var socket = null; 

// Function to establish conection with WebSocket
function establish_websocket_connection() {
    // Verify if there is a websocket conection established
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log('WebSocket connection already established.');
        return;
    }

    // Creates a new websocket instance if there is no conection established
    socket = new WebSocket("ws:0.0.0.0/start_session");

    socket.onopen = function(event) {
        console.log('Connection with server established.');
        token = localStorage.getItem('user_token');
        socket.send(JSON.stringify({'user': token}));
    };

    socket.onmessage = function(event) {
        var data = JSON.parse(event.data);
        if (data.action === 'logout') {
            sign_out();
        }
    };

    socket.onerror = function(error) {
        console.error('Connection error:', error);
    };

    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log('Connection closed.');
        } else {
            console.error('Connection lost.');
            // Try reconnecting after 2 seconds only if the connection was not cleanly closed
            setTimeout(establish_websocket_connection, 2000);
        }
    };
}

function close_websocket_connection() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
    } else {
        console.log('No WebSocket connection to close.');
    }
}

//------------------------Logic and HTML handling----------------------

// Function to display the welcome page
function display_welcome_view() {
    var welcome_view_script = document.getElementById('welcome_page');
    let welcome = document.getElementById('welcome_view');
    welcome.innerHTML = welcome_view_script.innerHTML;
    welcome.style.display = 'block'
}

// Function to shut down the welcome page
function shutdown_welcome_view() {
    let welcome = document.getElementById('welcome_view');
    welcome.innerHTML = '';
    welcome.style.display = "none";
}

// Function to forgot password page
function display_forgotPassword_view() {
    shutdown_welcome_view();
    var forgot_password_view_script = document.getElementById('forgot_password_page');
    let forgot_password = document.getElementById('forgot_password_view');
    forgot_password.innerHTML = forgot_password_view_script.innerHTML;
    forgot_password.style.display = 'block'
}

// Function to shut down the forgot password page
function shutdown_forgot_password() {
    let forgot_password = document.getElementById('forgot_password_view');
    forgot_password.innerHTML = '';
    forgot_password.style.display = "none";
    display_welcome_view();
}

// Function to display the profile page
function display_profile_view() {
    let profile_view_script = document.getElementById('profile_page');
    let profile = document.getElementById('profile_view');
    profile.innerHTML = profile_view_script.innerHTML;
    let home_content =  document.getElementById('home_content');
    establish_websocket_connection();
    profile.style.display = 'block';
    home_content.style.display = 'block';
    show_user_data();
    // It also reloads the wall only when the profile page is displayed 
    reload_wall();
    }

// Function to shut down the profile page
function shutdown_profile_view() {
    let profile = document.getElementById('profile_view');
    profile.innerHTML = '';
    profile.style.display = "none"
}

// Function to verify the length of the password in the login form 
function verify_login(form) {
    let passw = form.password.value;

    if (passw.length<9) {
        show_message('Password is too short.', 'login_message');
        return false;
    } else {
        verificate_user(form);
        return false; 
    }
}

// Function to veify the user's data in the login form
function verify_signup(form) {
    let passw = form.password_signup.value;
    let rep_passw = form.repeat_pass.value;
    
    if (passw === rep_passw && passw.length >= 9) {
        save_contact(form);
        return false;
    } else {
        show_message('Passwords do not match or are too short.', 'signup_message');
        return false;
    }
}

// Function to show an alert using the id of the alert code
function show_message(message, mess_id) {
    let message_dis = document.getElementById(mess_id);
    message_dis.textContent = message;
    message_dis.style.display = 'block';
    setTimeout(function() {
        message_dis.style.display = 'none';
    }, 3000);
}

// Function to verificate if the user is logged in
function has_loggedin() {
    // Retorn true if the user has a token, false if not
        let token = localStorage.getItem('user_token');
        if (token !== null && token !== undefined) {
            return true;
        }
        else {
            return false;}  
        }
    
// Function to show the content of the selected tab
function show_tab(evt, tab_name) {
    // Hide all tab contents
    var i, tab_content, tablink; 
    tab_content = document.getElementsByClassName('tab_content');
    for (i = 0; i < tab_content.length; i++) {
        tab_content[i].style.display = 'none';
    }

    // Deactivate all tabs
    var tablink = document.getElementsByClassName('tablink');
    for (var i = 0; i < tablink.length; i++) {
        tablink[i].className = tablink[i].className.replace(" selected_tab", "");
    }

    // Show the selected tab content
    document.getElementById(tab_name).style.display = 'block';
    // Mark the selected tab
    evt.currentTarget.className += ' selected_tab'
}

//---------------------Funcitions for server requests------------------

// Function to recover account
function recover_account(form) {
    let account = form.email.value;
    let data = {email: account};
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/recover_password", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            let response = JSON.parse(xhr.responseText);
            if (xhr.status === 200) {
                show_message("Recovery link sent to your email.", 'forgot_password_message');
                form.email.value = "";
            } else {if (response.message === 'Missing data or invalid request') {
                show_message('Missing data in the form, please try again.', 'forgot_password_message');}
                else if (response.message ===   'User not found.') {
                show_message('User not found with the provided email, please try again.', 'forgot_password_message');}
                else if (response.message ===   'Invalid email address.') {
                show_message('Provided email is invalid, please try again.', 'forgot_password_message');} 
                else if (response.message === 'Internal server error creating token.') {
                show_message('Server error creating credentials to change password, please try again.', 'forgot_password_message');}   
                else if (response.message ===   'Internal server error sending email.') {
                show_message('Server error sending email, please try again.', 'forgot_password_message');}
                else {
                show_message(response.message+', please try again','forgot_password_message');}
                }
        }
    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(data));
    return false;
}

// Function to Show the user's information
function show_user_data() {
    let token = localStorage.getItem('user_token');
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/get_user_data_by_token", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            let user = JSON.parse(xhr.responseText);
            if (xhr.status === 200) {
                document.getElementById("user_info").innerHTML = `
                    <h3 id="personal_info_string"> Your personal information </h3>
                    <p><b>Email:</b> ${user.data.email}</p>
                    <p><b>First Name:</b> ${user.data.firstname}</p>
                    <p><b>Family Name:</b> ${user.data.familyname}</p>
                    <p><b>Gender:</b> ${user.data.gender}</p>
                    <p><b>City:</b> ${user.data.city}</p>
                    <p><b>Country:</b> ${user.data.country}</p>
                `;
            } else {
                if (user.message === 'Error getting user data') {
                show_message('Server error getting data, please try again.', 'user_info_message');}    
                else {
                show_message(user.message,'user_info_message');}
            }
        }
    };
    xhr.setRequestHeader("Authorization", token);
    xhr.send();
}

//Function to save the user's information in the signup form
function save_contact(form){
    let email = form.username.value;
    let password = form.password_signup.value;
    let FirstName = form.name.value;
    let FamilyName = form.surname.value;
    let gender = form.gender.value; 
    let city = form.city.value;
    let country = form.country.value;

    let contact = {
        email: email,
        password: password,
        firstname: FirstName,
        familyname: FamilyName,
        gender: gender,
        city: city,
        country: country};

    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/sign_up", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            response = JSON.parse(xhr.responseText);
            if (xhr.status === 201) {
                if (response.data !== null || response.data !== undefined) {
                    localStorage.setItem('user_token', response.data);
                }
                show_message("User registered succesfully", 'signup_message');
                verify_login(form);
            } else {
                if (response.message === 'User already exists') {
                show_message('Email already registered.', 'signup_message');}
                else if (response.message ===   'Invalid data format') {
                show_message('Data has incorrect format, server error.', 'signup_message');}
                else if (response.message ===   'Invalid email address') {
                show_message('Provided email is invalid, please try again.', 'signup_message');}    
                else if (response.message ===   'Error creating the user') {
                show_message('Server error creating user, please try again.', 'signup_message');}    
                else {
                show_message(response.message,'signup_message');}
                }
        }
    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(contact));
}

//Function to verificate the user in the sign in
function verificate_user(form) {
    let email = form.username.value;
    let password = form.password.value;
    let user = {
        username: email,
        password: password
    };
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/sign_in", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            response = JSON.parse(xhr.responseText);
            if (xhr.readyState == 4 && xhr.status == 200) {
                localStorage.setItem('user_token', response.data);
                show_message('Succesfully loged in.','login_message');
                shutdown_welcome_view();            
                display_profile_view();
                }
            else {
                if (response.message === 'Missing data or invalid request') {
                    show_message('Missing data in the form, please try again.', 'login_message');}
                    else if (response.message ===   'User not found.') {
                    show_message('User not found with the provided email, please try again.', 'login_message');}
                    else if (response.message ===   'Invalid email address.') {
                    show_message('Provided email is invalid, please try again.', 'login_message');}    
                    else if (response.message ===   'Internal server error.') {
                    show_message('Server error logging the user, please try again.', 'login_message');}
                    else if (response.message ===   'Wrong credentials (username/password).') {
                    show_message('Email or password error, please try again.', 'login_message');}    
                    else {
                    show_message(response.message,'signup_message');}
                    }
            }
    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(user));
}

// Function to change the password
function change_password(form) {
    let old_password = form.old_password.value;
    let new_password = form.new_password.value;
    let repeat_new_password = form.repeat_new_password.value;
    let token = localStorage.getItem("user_token");
    
    // Validate if new passwords match
    if (new_password !== repeat_new_password || old_password === new_password) {
        show_message("Passwords do not match or the new password is the same as the old one.", "passchange_message");
        return false;}

    let xhr = new XMLHttpRequest();
    xhr.open("PUT", "/change_password", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            response = JSON.parse(xhr.responseText);
            if (xhr.status === 200) {
                show_message('Password succefully changed.', "passchange_message");
                //Reset the input values to empty string
                form.old_password.value = "";
                form.new_password.value = "";
                form.repeat_new_password.value = "";
            }
             else { 
                let response= JSON.parse(xhr.responseText);
                if (response.message === 'Incorrect new password format or length') {
                show_message('New password is not valid, incorrect format or length, please try again.', 'passchange_message');}
                else if (response.message ===   'Incorrect password.') {
                show_message('Incorrect actual password provided, please try again.', 'passchange_message');}
                else if (response.message ===   'Error changing the password') {
                show_message('Server error changing password, please try again.', 'passchange_message');}    
                else {
                show_message(response.message,'signup_message');}
            }
        };}
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.setRequestHeader("Authorization", token);
    xhr.send(JSON.stringify({oldpassword: old_password, newpassword: new_password}));
    return false;
    }

// Function to sign out
function sign_out() {
    let token = localStorage.getItem("user_token");
    let xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/sign_out", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            var response = JSON.parse(xhr.responseText);
            if (xhr.status === 200) {
                show_message(response.message, "logout_message");
                localStorage.removeItem('user_token');
                shutdown_profile_view();
                display_welcome_view();
                close_websocket_connection();
            } else {
                if (response.message === 'Error deleating the token') {
                show_message('Server error logging out, please try again.', 'logout_message');}
                else {show_message(response.message,'signup_message');}
            }
        }
    };
    xhr.setRequestHeader("Authorization", token);
    xhr.send();
}

// This function gets user email and message, then past it to the auxilair function that posts the message 
function post_message() {
    let message;
    let token = localStorage.getItem('user_token');
    let to_email;
    
    // Check which tab is selected
    var home_content = document.getElementById('home_content');
    var browse_content = document.getElementById('browse_content');

    if (home_content.style.display === 'block') {
        // If the Home tab is selected, post on own wall
        message = document.getElementById("post_message").value;

        // Check for empty message
        if (message.trim() === "") {
            show_message("Empty messages are not allowed.", 'post_home_message');
            return;
        }
        let xhr = new XMLHttpRequest();
        xhr.open("GET", "/get_user_data_by_token", true); 
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                var response = JSON.parse(xhr.responseText);
                if (xhr.status === 200) {
                    to_email = response.data.email;
                    post_message_request(message, to_email);
                } 
                else {
                    if (response.message === 'Error getting user data') {
                    show_message('Server error getting data, please try again.', 'post_home_message');}    
                    else {
                    show_message(response.message,'post_home_message');}
                }
            }
        };
        xhr.setRequestHeader("Authorization", token);
        xhr.send();
    } else if (browse_content.style.display === 'block') {
        // If the Browse tab is selected, post on another user's wall
        message = document.getElementById("post_message_other_user").value;
        // Check for empty message
        if (message.trim() === "") {
            show_message("Empty messages are not allowed.", 'post_home_message');
            document.getElementById('post_home_message').style.display = 'block';
            return;
        }
        to_email = document.getElementById("browse_user_email").value;
        post_message_request(message, to_email);
    }
}

//Auxiliar function to post a message
function post_message_request(message, to_email) {
    let token = localStorage.getItem('user_token');

    //Clears the text box    
    if (home_content.style.display === 'block') {
        message_box = document.getElementById("post_message");
        message_box.value = "";    
    } else if (browse_content.style.display === 'block') {
        message_box = document.getElementById("post_message_other_user");
        message_box.value = "";}

    // Send POST request to post the message
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/post_message", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 201) {
                let response = JSON.parse(xhr.responseText);
                if (home_content.style.display === 'block') {
                    show_message('Message succesfully posted.', 'post_home_message');
                    reload_wall();
                } else {
                    show_message('Message succesfully posted.', 'browse_message');
                    reload_wall_browse();
                }
            } else {
                let response = JSON.parse(xhr.responseText);
                if (home_content.style.display === 'block') {
                    if (response.message === 'Missing required data') {
                    show_message('Missing data, verify email/message and try again.', 'post_home_message');}
                    else if (response.message === 'Receiver email not found') {
                    show_message('Server error user not found, please try again.', 'post_home_message');}
                    else if (response.message === 'Error posting message') {
                    show_message('Server error posting message, please try again.', 'post_home_message');}    
                    else {
                    show_message(response.message,'post_home_message');}
                } else {
                    if (response.message === 'Missing required data') {
                    show_message('Missing data, verify email/message and try again.', 'browse_message');}
                    else if (response.message === 'Receiver email not found') {
                    show_message('Server error user not found, please try again.', 'browse_message');}
                    else if (response.message === 'Error posting message') {
                    show_message('Server error posting message, please try again.', 'browse_message');}    
                    else {
                    show_message(response.message,'browse_message');}
            }
            }
        }
    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.setRequestHeader("Authorization", token);
    xhr.send(JSON.stringify({message: message, email: to_email}));
}

// Function to reload the wall and display newly posted messages
function reload_wall() {
    let token = localStorage.getItem('user_token');
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/get_user_messages_by_token", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            var response = JSON.parse(xhr.responseText);
            if (xhr.status === 200) {
                let message_wall = document.getElementById("message_wall_ms");
                message_wall.innerHTML = ""; 
                if (response.data !== null){
                    response.data.forEach(function (messages) {
                        var li = document.createElement("li");
                        li.appendChild(document.createTextNode(messages.sender + ": " + messages.message));
                        message_wall.appendChild(li);
                })};
            } else {
                if (response.message === 'Error getting user messages') {
                    show_message('Server error getting messages, please try again.', 'post_home_message');}    
                    else {
                    show_message(response.message,'post_home_message');}
            }
        }
    };
    xhr.setRequestHeader("Authorization", token);
    xhr.send();
}

// Function to reload the wall and display newly posted messages in Browse User
function reload_wall_browse() {
    let token = localStorage.getItem('user_token');
    let user_email = document.getElementById("browse_user_email").value;
    
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/get_user_messages_by_email/" + user_email, true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            response = JSON.parse(xhr.responseText);
            if (xhr.status === 200) {
                let browse_user_wall = document.getElementById("browse_user_wall_message");
                browse_user_wall.innerHTML = ""; // Clear existing messages
                response.data.forEach(function (messages) {
                    var li = document.createElement("li");
                    li.appendChild(document.createTextNode(messages.sender + ": " + messages.message));
                    browse_user_wall.appendChild(li);
                });
            } else {
                if (response.message === 'Email missing') {
                show_message('Missing email, please try again.', 'browse_user_wall_message');}
                else if (response.message === 'Email does not exist') {
                show_message('Email provided not found, please try again.', 'browse_user_wall_message');}
                else if (response.message === 'Error retrieving data') {
                show_message('Server error getting messages, please try again.', 'browse_user_wall_message');}    
                else {
                show_message(response.message,'browse_user_wall_message');}
            }
        }
    };
    xhr.setRequestHeader("Authorization", token);
    xhr.send();
}

// Function to browse a user in the browse tab
function browse_user() {
    let user_email = document.getElementById("browse_user_email").value;
    let token = localStorage.getItem('user_token');

    let xhr_user_info = new XMLHttpRequest();
    xhr_user_info.open("GET", "/get_user_data_by_email/" + user_email, true);
    xhr_user_info.onreadystatechange = function() {
        if (xhr_user_info.readyState === XMLHttpRequest.DONE) {
            if (xhr_user_info.status === 200) {
                let response = JSON.parse(xhr_user_info.responseText);
                let browse_user_info = document.getElementById("browse_user_info");
                let browse_user_post = document.getElementById("browse_user_post");
                let browse_user_wall = document.getElementById("browse_user_wall");
                browse_user_info.innerHTML = ""; // Clear existing user information
                browse_user_wall.innerHTML = ""; // Clear existing user wall
                let user = response.data;
                browse_user_info.innerHTML = `
                    <h2>${user.firstname}'s personal information</h2>
                    <p><b>Email:</b> ${user.email}</p>
                    <p><b>First Name:</b> ${user.firstname}</p>
                    <p><b>Family Name:</b> ${user.familyname}</p>
                    <p><b>Gender:</b> ${user.gender}</p>
                    <p><b>City:</b> ${user.city}</p>
                    <p><b>Country:</b> ${user.country}</p>   
                `;
                browse_user_post.innerHTML = `
                    <h3> Post a message!</h3>
                    <textarea id="post_message_other_user" rows="4" cols="50" placeholder="Write a message..."></textarea>
                    <button onclick="post_message()">Post</button>        
                `;
                browse_user_wall.innerHTML =`
                    <h3>${user.firstname}'s message wall</h3> 
                    <div id="browse_user_wall_message"></div>
                    <button class="reload_button" onclick="reload_wall_browse()">Reload Wall</button>
                `;
                browse_user_info.style.display = "block";
                browse_user_post.style.display = "block";
                browse_user_wall.style.display = "block";

                get_messages_browse();
            } else {
                let response = JSON.parse(xhr_user_info.responseText);
                if (response.message === 'Email missing') {
                show_message('Missing email, please try again.', 'browse_message');}
                else if (response.message === 'User with the provided email does not exist') {
                show_message('Email provided not found, please try again.', 'browse_message');}
                else if (response.message === 'Error retrieving data') {
                show_message('Server error getting information.', 'browse_message');}    
                else {
                show_message(response.message,'browse_message');}
            }
        }
    };
    xhr_user_info.setRequestHeader("Authorization", token);
    xhr_user_info.send();
}

function get_messages_browse() {
    let user_email = document.getElementById("browse_user_email").value;
    let token = localStorage.getItem('user_token');
    let xhr_user_mess = new XMLHttpRequest();
    xhr_user_mess.open("GET", "/get_user_messages_by_email/" + user_email, true);
    xhr_user_mess.onreadystatechange = function() {
        if (xhr_user_mess.readyState === XMLHttpRequest.DONE) {
            if (xhr_user_mess.status === 200) {
                let response = JSON.parse(xhr_user_mess.responseText);
                let browse_user_message = document.getElementById("browse_user_wall_message")
                response.data.forEach(function (messages) {
                    var li = document.createElement("li");
                    li.appendChild(document.createTextNode(messages.sender + ": " + messages.message));
                    browse_user_message.appendChild(li);
                    });    
            } else {
                let response = JSON.parse(xhr_user_info.responseText);
                if (response.message === 'Email missing') {
                show_message('Missing email, please try again.', 'browse_message');}
                else if (response.message === 'Email does not exist') {
                show_message('Email provided not found, please try again.', 'browse_message');}
                else if (response.message === 'Error retrieving data') {
                show_message('Server error getting information.', 'browse_message');}    
                else {
                show_message(response.message,'browse_message');}
            }
        }
    };
    xhr_user_mess.setRequestHeader("Authorization", token);
    xhr_user_mess.send();
}
