function openModal() {
    $("#myModal").modal("toggle");
}


function detectPerson() {
    fetch('/detection', {method: "GET"})
        .then(function(response) {return response.json();})
        .then(function (text) {
            console.log('GET response:');
            console.log(text);
            openModal();
            setTimeout(openModal, 3000);
            })
        .catch(err => console.log(err));
}

async function detectPerson2() {
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
        openModal();
        setTimeout(openModal, 3000);
    })
}
