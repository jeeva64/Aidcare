document.getElementById("loginForm").addEventListener("submit",function(event){
    const username=document.getElementById("username").value;
    const password=document.getElementById("password").value;
    let valid=true;
    if(username==""){
        document.getElementById("usernameError").textContent="Username is Required.";
        valid=false;
    }
    else if(username.length<3 || username.length > 100){
        document.getElementById("usernameError").textContent="Username must be between 3 and 100 characters.";
        valid=false;
    }
    else{
        document.getElementById("usernameError").textContent="";
    }
    
    if(password==0){
        document.getElementById("passwordError").textContent="Password is Required.";
        valid=false;
    }
    else if(password.length<8 ){
        document.getElementById("passwordError").textContent="Password must be atleast 8 characters long.";
        valid=false;
    }
    else{
        document.getElementById("passwordError").textContent="";
    }

    if(!valid){
        event.preventDefault();
    }
});