$(document).ready(function() {
    let url = ?IP;
    let ws_port = '9001';
    let http_port = '8001';
    let viewer = document.getElementById('num-current-vehicle-text');
    let changeBackground = document.getElementById("number_of_current_vehicle");
    $.get('http://' + url + ":" + http_port + "/init", function(results) {
        viewer.innerText = results['data'];
        changeBackground.style.background = results['color'];
    }, 'json')
    ws = new WebSocket("ws://" + url + ":" + ws_port);

    ws.onopen = function(event) {
        ws.send('Hello Everyone, This message is from js.');
    }

    ws.onmessage = function(event) {
        console.log(event.data);
        let msg = JSON.parse(event.data);
        viewer.innerText = msg['data'];
        changeBackground.style.background = msg['color'];
        if(msg['is_alert']) {
            alert("Oops! The parking lot seemed to be already full.")
        }
    }

})