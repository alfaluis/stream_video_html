var cTime = 0;
var takePic = 3;
var startProcess = false;
var myVar;
var startTime = new Date();
var postMess = true;

function postMessage(){
    document.getElementById("texto").innerHTML = "Finished";
    var inFloor = document.getElementById("floor").value;
    var inName = document.getElementById("name").value;
    postMess = true;
    clearInterval(myVar);
    var url = "/route/to/change_color";
    var data = {take_pics: true, floor: inFloor, name: inName};
    $.post(url, data);
}

function activateCountDown(){
    if (document.getElementById("name").value.length == 0 | document.getElementById("floor").value.length == 0){
        alert("Nombre no puede estar vacia");
    }
    else{
	    myVar = setInterval(myTimer2, 1000);
	    startTime = new Date();
    }
}

function myTimer2() {
    var d = new Date();
    var t = d.toLocaleTimeString();
    document.getElementById("texto").innerHTML = "El Proceso comenzara a tomar fotos en: ";
    document.getElementById("tiempo").innerHTML = Math.round(3 - (d - startTime) / 1000);
    if (postMess == true) {
        postMess = false;
        timeoutID = setTimeout(postMessage, 3000);
    }

    if (Math.abs((startTime - d) / 1000) >= 3){
  	    document.getElementById("texto").innerHTML = "Tomando fotos... Tiempo restamte:";
  	    document.getElementById("tiempo").innerHTML = Math.round(3 - (d - startTime) / 1000);
        startTime = new Date();
    }
}

