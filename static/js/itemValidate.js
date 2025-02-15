document.getElementById("itemForm").addEventListener("submit",function(event){

    let valid=true;
    var itemName=document.getElementById("name").value.trim();
    var description=document.getElementById("description").value.trim();
    var productImage=document.getElementById("product");

    if(itemName.length<3 || itemName.length > 25){
        document.getElementById("usernameError").textContent="Itemname must be between 3 and 25 characters.";
        valid=false;
    }
    else{
        document.getElementById("usernameError").textContent="";
    }

    if(description===""){
        document.getElementById("descriptionError").textContent="Item Description is required.";
        valid=false;
    }
    else{
        document.getElementById("descriptionError").textContent="";
    }

    if(productImage.files.length === 0){
        document.getElementById("productError").textContent="Item Image is required.";
        valid=false;
    }
    else{
        let file = productImage.files[0];
        let allowedTypes = ["image/jpeg", "image/png", "image/jpg"];
        let maxSize = 2 * 1024 * 1024; // 2MB

        // Validate File Type
        if (!allowedTypes.includes(file.type)) {
            document.getElementById("productError").textContent = "Only JPG, PNG, and JPEG files are allowed.";
            valid = false;
        }
        // Validate File Size
        else if (file.size > maxSize) {
            document.getElementById("productError").textContent = "Image size must be less than 2MB.";
            valid = false;
        } else {
            document.getElementById("productError").textContent="";
        }
    }

    if(!valid){
        event.preventDefault();
    }
});