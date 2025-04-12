async function uploadImages() {
    let fileInput = document.getElementById("fileInput");
    let files = fileInput.files;
   
    if (files.length === 0) {
        alert("Please select at least one image.");
        return;
    }
 
    let formData = new FormData();
    for (let file of files) {
        formData.append("files", file);
    }
 
    try {
        let response = await fetch("/uploadfiles/", {
            method: "POST",
            body: formData
        });
 
        if (response.ok) {
            alert("Image uploaded successfully!");  // Show alert on successful upload
        } else {
            alert("Error uploading image. Please try again.");
        }
 
        let data = await response.json();
       
        if (data.uploaded_files) {
            data.uploaded_files.forEach(fileInfo => {
                addImageToGallery(fileInfo.path);
            });
        } else {
            console.error("Error uploading images:", data);
        }
    } catch (error) {
        console.error("Error:", error);
    }
}
 
function fetchAndDisplayImage() {
    let filename = document.getElementById("imageFilenameInput").value.trim();
    let imageContainer = document.getElementById("imageContainer");
 
    // Clear previous image
    imageContainer.innerHTML = "";
 
    if (!filename) {
        alert("Please enter an image filename.");
        return;
    }
 
    let imageUrl = `/images/${filename}`; // Construct API endpoint URL
 
    // Create an image element
    let imgElement = document.createElement("img");
    imgElement.src = imageUrl;
    imgElement.onerror = function () {
        alert("No image found.");
        imageContainer.innerHTML = ""; // Clear container if image fails to load
    };
 
    imgElement.style.maxWidth = "500px"; // Optional: Limit size
    imageContainer.appendChild(imgElement);
}