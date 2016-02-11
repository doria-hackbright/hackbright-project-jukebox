// On Load

$(function() {

    $.post('/guest', {'jukebox_id': window.location.href.slice(-36)}, function() {
        alert("I made a new user!");
    });

});
