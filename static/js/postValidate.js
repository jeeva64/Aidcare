document.getElementById("postForm").addEventListener("submit",function(event){
    
    let valid=true;
    var title=document.getElementById("title").value.trim();
    var description=document.getElementById("description").value.trim();
    var district=document.getElementById("district").value;
    var productImage=document.getElementById("image");

    if(title.length<3 || title.length > 25){
        document.getElementById("titleError").textContent="Post Title must be between 3 and 25 characters.";
        valid=false;
    }else{
        document.getElementById("titleError").textContent="";
    }

    if(description===""){
        document.getElementById("descriptionError").textContent="Item Description is required.";
        valid=false;
    }else{
        document.getElementById("descriptionError").textContent="";
    }

    if(district===""){
        document.getElementById("districtError").textContent="Please select a district.";
        valid=false;
    }else{
        document.getElementById("districtError").textContent="";
    }
    
    if(productImage.files.length === 0){
        document.getElementById("imageError").textContent="Item Image is required.";
        valid=false;
    }
    else{
        let file = productImage.files[0];
        let allowedTypes = ["image/jpeg", "image/png", "image/jpg"];
        let maxSize = 2 * 1024 * 1024; // 2MB

        // Validate File Type
        if (!allowedTypes.includes(file.type)) {
            document.getElementById("imageError").textContent = "Only JPG, PNG, and JPEG files are allowed.";
            valid = false;
        }
        // Validate File Size
        else if (file.size > maxSize) {
            document.getElementById("imageError").textContent = "Image size must be less than 2MB.";
            valid = false;
        } else {
            document.getElementById("imageError").textContent="";
        }
    }

    if(!valid){
        event.preventDefault();
    }
});