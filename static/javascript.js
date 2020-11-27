var cTime = 5;
var takePic = 3;
function myTimer(){
    setTimeout(myTimer, 1000);
    if (takePic > 0){
        if (cTime > 0){
            document.getElementById("texto").innerHTML = "El sistema comenzara a tomar fotos en: ";
            document.getElementById("tiempo").innerHTML = cTime + "s.";
            cTime = cTime - 1;
        }
        else {
            document.getElementById("texto").innerHTML = "Tomando foto... Tiempo restante:";
            document.getElementById("tiempo").innerHTML = takePic + "s.";;
            takePic = takePic - 1;
        }
    }
    else {
        document.getElementById("texto").innerHTML = "Procesando...";
        document.getElementById("tiempo").innerHTML = "";
    }
}
