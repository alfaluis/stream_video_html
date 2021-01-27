// Activate recursive request once the page load
window.addEventListener("load",  doRecursiveRequest);

// Function to open Modal Object passing as parameter the name of the person identified
function openModal(person=null) {
    console.log("Passed Param:")
    console.log(person)
    $("#myModal").modal("toggle");
    if(person != null) {
        document.getElementById("modalBody").innerHTML = person + "!";
    }
    doRecursiveRequest();
}

// Function to check a good response from the server
function status(response) {
    if (response.ok) {
        return response;
    } else {
        return doRecursiveRequest();
    }
}

// Main function to continue asking for people identified
function doRecursiveRequest(){
    fetch('/detection', {method: "GET"})
        .then(status)
        .then(function(resJson) {return resJson.json();})
        .then(text => {
            console.log('GET response:');
            console.log(text);
            console.log(text.PersonName);
            if(text.PersonName != null){
                openModal(text.PersonName);
                setTimeout(openModal, 3000);
            } else{
                doRecursiveRequest();
            }
        })
        .catch(err => {
            console.log('Error log:');
            console.log(err);
            doRecursiveRequest();
        })
}