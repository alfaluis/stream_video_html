var cTime = 0;
var takePic = 3;
var startProcess = false;
var intervalPreview;
var intervalCapture;
var startTime = new Date();
var postMess = true;

// Function to process the response from Post message (sentUserInfoPost)
function processResponse(responseJson){
    clearInterval(intervalCapture)
    console.log(responseJson)
    document.getElementById("texto").innerHTML = "Fotos Tomadas: " + responseJson.UploadProcess;
  	document.getElementById("tiempo").innerHTML = "";
  	if (responseJson.UploadProcess == "Success"){
  	    alert("Fotos subidas exitosamente. \nSe Procedera con registro de usario. Esto puede tomar un tiempo.")
  	    return true
  	} else {
  	    alert("Error al subir fotos. \nPor favor intente nuevamente.")
  	    return false
  	}
}

// Function to start training process and return response from server (flask)
function trainingProcess(uploadStatus){
    if (uploadStatus){
        console.log('upload Status Succeed:');
        console.log(uploadStatus);
        document.getElementById("texto").innerHTML = "Training...";
        fetch('/training_status', {method: "GET"})
            .then(function(response) {return response.json();})
            .then(function (text) {
                console.log('GET response:');
                console.log(text);
                cleanInfo()
                alert("Usuario registrado exitosamente!");})
            .catch(err => console.log(err));
    } else {
        cleanInfo()
        console.log('upload Status Fail');
        console.log(uploadStatus);
    }
}

// Post user information to server (flask)
function sentUserInfoPost(){
    // Disable intervalPeview Interval and activate captureCountDown
    clearInterval(intervalPreview);
    intervalCapture = setInterval(captureCountDown, 1000);
    
    // get values from Form
    var inFloor = document.getElementById("floor").value;
    var inName = document.getElementById("name").value;
    
    // restart variable
    startTime = new Date();
    // dictionary to sent
    var infoData = {take_pics: true, floor: inFloor, name: inName};
    
    // post message with 
    fetch('/client_info', {method: "POST",
                                     body:  JSON.stringify(infoData),
                                     headers: {"Content-type": "application/json"}}
        )
        .then(function(response) {return response.json();})
        .then(processResponse)
        .then(trainingProcess)
        .catch(err => console.log(err));
}

// Function called once the client press start button
function activateCountDown(){
    // validate information
    if (document.getElementById("name").value.length == 0 | document.getElementById("floor").value.length == 0){
        alert("Nombre o piso no puede estar vacia");
    }
    else{
        // activate timer function every 1s
	    intervalPreview = setInterval(previewCountDown, 1000);
	    setTimeout(sentUserInfoPost, 3000);
	    document.getElementById("btnStart").disabled = true;
	    startTime = new Date();
    }
}

function previewCountDown() {
    var d = new Date();
    document.getElementById("texto").innerHTML = "El Proceso comenzara a tomar fotos en: ";
    document.getElementById("tiempo").innerHTML = Math.round(3 - (d - startTime) / 1000);
}

function captureCountDown(){
    var d = new Date();
    document.getElementById("texto").innerHTML = "Tomando fotos... Tiempo restante:";
  	document.getElementById("tiempo").innerHTML = Math.round(3 - (d - startTime) / 1000);
}

function cleanInfo(){
    document.getElementById("btnStart").disabled = false;
    document.getElementById("texto").innerHTML = "";
    document.getElementById("formUser").reset();
}

