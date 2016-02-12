$(function() {

    //On load, a post request is sent to create a new user
    $.post('/guest', {'jukebox_id': window.location.href.slice(-36)}, function() {
        console.log("I made a new user!");
    });

});
