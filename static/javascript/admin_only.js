// Admin View Specific Javascript

$(function() {

    // Ensures that the proper public URL is provided
    $("#public-url").text(window.location.href.slice(0,-6));

    // Deletes the playlist using the button
    $("#delete-jukebox").click(function(){
        $.post("/jukebox/" + window.location.href.slice(-36, -6)  +
            "/delete", {'jukebox_id': window.location.href.slice(-36, -6)});
    });

    // Shuts down the jukebox when the window is closed
    $(window).on('beforeunload', function(e) {
        console.log("HELLO");
        $.post("/jukebox/" + window.location.href.slice(-36, -6)  +
            "/delete", {'jukebox_id': window.location.href.slice(-36, -6)});
    });

});

