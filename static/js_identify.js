window.addEventListener("load",  doRecursiveRequest);

function openModal(person=null) {
    console.log("Passed Param:")
    console.log(person)
    $("#myModal").modal("toggle");
    if(person != null) {
        document.getElementById("modalBody").innerHTML = person + "!";
    }
    doRecursiveRequest();
}

async function detectPerson2(url) {
    try{
        let response = await fetch('/detection', {method: "GET"});
        let data = await response.json();
        return data
     } catch(err) {
        throw err
     }
}

function clickResp(){
    detectPerson2()
    .then(text => {
        console.log('GET response:');
        console.log(text);
        openModal("bla bla");
        setTimeout(openModal, 3000);
    })
}

function status(response) {
    if (response.ok) {
        return response;
    } else {
        return doRecursiveRequest();
    }
}

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