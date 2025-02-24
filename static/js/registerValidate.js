document.getElementById("registerForm").addEventListener("submit",function(event){
    
    let valid=true;
    var username=document.getElementById("uname").value.trim();
    var email=document.getElementById("mail").value.trim();
    var mobile=document.getElementById("mobile").value.trim();
    var address=document.getElementById("address").value.trim();
    var district=document.getElementById("district").value;
    var user_type=document.getElementById("u_type").value;
    var password=document.getElementById("password").value.trim();
    var confirm_pass=document.getElementById("c_pass").value.trim();
    var checkbox=document.getElementById("agree");


    if(username.length<3 || username.length > 100){
        document.getElementById("usernameError").textContent="Username must be between 3 and 100 characters.";
        valid=false;
    }
    else{
        document.getElementById("usernameError").textContent="";
    }

    const emailRegex=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(email===""){
        document.getElementById("emailError").textContent="Email is required.";
        valid=false;
    }
    else if(!emailRegex.test(email)){
        document.getElementById("emailError").textContent="Invalid email format.";
        valid=false;
    }
    else{
        document.getElementById("emailError").textContent="";
    }

    var phoneno = /^\d{10}$/;
    if(!mobile.match(phoneno)){
        document.getElementById("mobileError").textContent="Mobile Number must be exactly 10 digits.";
        valid=false;
    }
    else{
        document.getElementById("mobileError").textContent="";
    }
    
    if(address===""){
        document.getElementById("addressError").textContent="Address is required.";
        valid=false;
    }
    else{
        document.getElementById("addressError").textContent="";
    }

    if(district===""){
        document.getElementById("districtError").textContent="Please select a district.";
        valid=false;
    }
    else{
        document.getElementById("districtError").textContent="";
    }

    if(user_type===""){
        document.getElementById("userTypeError").textContent="Please Select a User Type.";
        valid=false;
    }
    else{
        document.getElementById("userTypeError").textContent="";
    }

    if(password.length<8 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password) || !/[!@#$%^&*]/.test(password)){
        document.getElementById("passwordError").textContent="Password must be atleast 8 characters long and include uppercase, lowercase, a number, and a special character.";
        valid=false;
    }
    else{
        document.getElementById("passwordError").textContent="";
    }

    if(confirm_pass!=password){
        document.getElementById("confirmpasswordError").textContent="Password Mismatch!";
        valid=false;
    }
    else{
        document.getElementById("confirmpasswordError").textContent="";
    }

    if (!checkbox.checked) {
        document.getElementById("checkboxError").textContent = "You must agree to the terms and conditions.";
        valid=false;
    } else {
        document.getElementById("checkboxError").textContent = "";
    }

    if(!valid){
        event.preventDefault();
    }
});