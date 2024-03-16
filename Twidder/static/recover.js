// Function to close window
function close_window() {
    window.close();
}    

// Fuction to display the welcome view
function display_message_view() {
    let done_view = document.getElementById('pass_change_view');
    let succesfully = document.getElementById('passchange_message');
    succesfully.innerHTML = done_view.innerHTML;
    succesfully.style.display = 'block'   
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

// Function to verify the data entered in the login form
function verify_data(form) {
    let password = form.password.value;
    let rep_password = form.repeat_password.value;
    if (password !== rep_password) {
        show_message('Passwords do not match.', 'showmessage');
        return false;}
    else if (password.length <9) {
        show_message('Passwords must be at least 9 characters long.', 'showmessage');
        return false;}
    reset_password(form);
    return false;    
}

// Function to reset the password
function reset_password(form) {
    // Obtener la URL actual
    let url = window.location.href;
    // Crear un objeto URLSearchParams para obtener los parámetros de la URL
    let params = new URLSearchParams(new URL(url).search);
    // Obtener el valor del parámetro 'token' de la URL
    let token = params.get('user');
    let new_password = form.password.value;
    
    let xhr = new XMLHttpRequest();
    xhr.open("PUT", "/reset_password", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            response = JSON.parse(xhr.responseText);
            if (xhr.status === 200) {
                show_message('Password succefully changed.', "showmessage");
                //Reset the input values to empty string
                form.password.value = "";
                form.repeat_password.value = "";
                let page = document.getElementById('recover_block');
                page.innerHTML = "";
                page.style.display = 'none';
                display_message_view();
            }
             else { 
                let response= JSON.parse(xhr.responseText);
                if (response.message === 'Missing data or token.') {
                show_message('Password missing, please try again.', 'showmessage');}
                else if (response.message === 'token expired.') {
                show_message('Credentials expired, please try sending recover email again.', 'showmessage');}
                else if (response.message === 'Error changing password.') {
                show_message('Server error changing password, please try again.', 'showmessage');}    
                else {
                show_message(response.message,'showmessage');}
            }
        };}
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.setRequestHeader("Authorization", token);
    xhr.send(JSON.stringify({newpassword: new_password}));
}