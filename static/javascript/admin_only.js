 $(function() {

    // Start WebSockets
    var socket = new WebSocket("ws://" + document.domain + ":5000/websocket/");

    socket.onopen = function() {
        socket.send('{"jukebox_id" : ' + '"' + window.location.href.slice(-42,-6) + '"' + '}');
        console.log("Socket Opened");
    };

});
