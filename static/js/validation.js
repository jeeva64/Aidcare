document.getElementById("registerForm").addEventListener("submit",function(e){
    
    let valid=true;
    const username=document.getElementById("uname").value.trim();
    if(username.length<3){
        document.getElementById("usernameError").textContent="Username must be atleast 3 characters long.";
        valid=false;
    }
    else{
        document.getElementById("usernameError").textContent="";
    }

    const email=document.getElementById("mail").value.trim();
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

    const address=document.getElementById("address").value.trim();
    if(address===""){
        document.getElementById("addressError").textContent="Address is required.";
        valid=false;
    }
    else{
        document.getElementById("addressError").textContent="";
    }

    const district=document.getElementById("district").value.trim();
    if(district===""){
        document.getElementById("districtError").textContent="Please select a district.";
        valid=false;
    }
    else{
        document.getElementById("districtError").textContent="";
    }

    const user_type=document.getElementById("u_type").value;
    if(user_type===""){
        document.getElementById("userTypeError").textContent="Please Select a User Type.";
        valid=false;
    }
    else{
        document.getElementById("userTypeError").textContent="";
    }

    const password=document.getElementById("password").value.trim();
    if(password.length<8){
        document.getElementById("passwordError").textContent="Password must be atleast 8 characters long.";
        valid=false;
    }
    else{
        document.getElementById("passwordError").textContent="";
    }

    const confirm_pass=document.getElementById("c_pass").value.trim();
    if(confirm_pass!=password){
        document.getElementById("confirmpasswordError").textContent="Password Mismatch!";
        valid=false;
    }
    else{
        document.getElementById("confirmpasswordError").textContent="";
    }

    if(!valid){
        e.preventDefault();
    }
});