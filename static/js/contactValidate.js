document.getElementById("contactForm").addEventListener("submit",function(event){
    let valid=true;
    var name=document.getElementById("name").value.trim();
    var email=document.getElementById("mail").value.trim();
    var mobile=document.getElementById("mobile").value;
    var subject=document.getElementById("subject").value.trim();
    var message=document.getElementById("message").value.trim();

    if(name.length<3 || name.length > 100){
        document.getElementById("nameError").textContent="Username must be between 3 and 100 characters.";
        valid=false;
    }
    else{
        document.getElementById("nameError").textContent="";
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

    if(subject===""){
        document.getElementById("subjectError").textContent="Subject is required.";
        valid=false;
    }
    else{
        document.getElementById("subjectError").textContent="";
    }

    if(message===""){
        document.getElementById("messageError").textContent="Message is required.";
        valid=false;
    }
    else{
        document.getElementById("messageError").textContent="";
    }

    if(!valid){
        event.preventDefault();
    }
});